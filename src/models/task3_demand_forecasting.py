"""
Task 3: Predict high-demand job roles by analyzing job posting patterns over time.
Builds time-series forecasting models with chronological train/test splits,
computes MAE, RMSE, MAPE, R2 metrics, and generates 30-day future demand projections.
"""
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import config
from src.data.loader import load_jobs_data

def calculate_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Computes Mean Absolute Percentage Error (MAPE)."""
    mask = y_true != 0
    if not np.any(mask):
        return 0.0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100.0)

def create_time_series_features(series: pd.Series, max_lags: int = 7) -> Tuple[pd.DataFrame, pd.Series]:
    """Generates lag features, rolling windows, and day-of-week seasonality."""
    df_ts = pd.DataFrame({"demand": series})
    
    # Lag features
    for lag in range(1, max_lags + 1):
        df_ts[f"lag_{lag}"] = df_ts["demand"].shift(lag)
        
    # Rolling statistics
    df_ts["rolling_mean_3"] = df_ts["demand"].shift(1).rolling(3).mean()
    df_ts["rolling_mean_7"] = df_ts["demand"].shift(1).rolling(7).mean()
    df_ts["rolling_std_7"] = df_ts["demand"].shift(1).rolling(7).std().fillna(0)

    # Calendar features
    dates = pd.to_datetime(series.index)
    df_ts["day_of_week"] = dates.dayofweek
    df_ts["is_weekend"] = df_ts["day_of_week"].isin([5, 6]).astype(int)

    # One-hot encode day of week
    for dow in range(7):
        df_ts[f"dow_{dow}"] = (df_ts["day_of_week"] == dow).astype(int)

    df_ts = df_ts.dropna()
    feature_cols = [c for c in df_ts.columns if c not in ["demand", "day_of_week"]]
    return df_ts[feature_cols], df_ts["demand"]

def train_and_forecast_role(
    series: pd.Series,
    role_name: str,
    forecast_horizon: int = 30,
    test_ratio: float = 0.20
) -> Dict[str, Any]:
    """
    Trains an autoregressive ensemble model on a role's posting time series,
    evaluates on test split, and forecasts future demand with 95% confidence intervals.
    """
    X, y = create_time_series_features(series)
    
    # Chronological Train-Test Split
    n_samples = len(X)
    split_idx = int(n_samples * (1 - test_ratio))
    split_idx = max(split_idx, n_samples - 8) # At least 8 days test
    
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    # Train robust ensemble model
    model = GradientBoostingRegressor(
        n_estimators=100,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Predictions on test set
    y_test_pred = model.predict(X_test)
    y_test_pred = np.maximum(y_test_pred, 0) # Non-negative postings

    # Accuracy Metrics
    mae = float(mean_absolute_error(y_test, y_test_pred))
    rmse = float(np.sqrt(mean_squared_error(y_test, y_test_pred)))
    mape = float(calculate_mape(y_test.values, y_test_pred))
    r2 = float(r2_score(y_test, y_test_pred))

    # Calculate residual standard error for prediction intervals
    train_residuals = y_train - model.predict(X_train)
    residual_std = float(np.std(train_residuals))

    # Refit model on full available historical data for future forecast
    model_full = GradientBoostingRegressor(
        n_estimators=120,
        learning_rate=0.05,
        max_depth=3,
        random_state=42
    )
    model_full.fit(X, y)

    # Recursive multi-step forecasting for future horizon
    last_date = pd.to_datetime(series.index[-1])
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, forecast_horizon + 1)]
    
    # Iterative recursive forecast simulation
    history_demand = list(series.values)
    future_forecasts = []
    future_lower_95 = []
    future_upper_95 = []

    for step, f_date in enumerate(future_dates):
        # Build features for current step
        recent_demands = history_demand[-7:]
        lag_features = {f"lag_{i}": recent_demands[-i] for i in range(1, 8)}
        r_mean3 = np.mean(history_demand[-3:])
        r_mean7 = np.mean(history_demand[-7:])
        r_std7 = np.std(history_demand[-7:])
        dow = f_date.dayofweek
        is_wknd = 1 if dow in [5, 6] else 0

        feat_dict = {
            **lag_features,
            "rolling_mean_3": r_mean3,
            "rolling_mean_7": r_mean7,
            "rolling_std_7": r_std7,
            "is_weekend": is_wknd,
            **{f"dow_{d}": 1 if dow == d else 0 for d in range(7)}
        }
        
        # Ensure column ordering matches training
        input_row = pd.DataFrame([feat_dict])[X.columns]
        pred_val = float(max(0, model_full.predict(input_row)[0]))
        
        # Error expands slightly over forecast horizon
        horizon_uncertainty = 1.96 * residual_std * np.sqrt(1 + 0.05 * step)
        
        future_forecasts.append(round(pred_val, 1))
        future_lower_95.append(round(max(0.0, pred_val - horizon_uncertainty), 1))
        future_upper_95.append(round(pred_val + horizon_uncertainty, 1))
        
        # Append prediction back into historical window for next step
        history_demand.append(pred_val)

    return {
        "role_name": role_name,
        "metrics": {
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE": round(mape, 2),
            "R2_Score": round(r2, 4)
        },
        "train_size": len(X_train),
        "test_size": len(X_test),
        "history": {
            "dates": [str(d) for d in series.index],
            "actuals": [int(v) for v in series.values]
        },
        "test_evaluation": {
            "dates": [str(d) for d in y_test.index],
            "actuals": [float(v) for v in y_test.values],
            "predicted": [round(float(v), 1) for v in y_test_pred]
        },
        "future_forecast": {
            "dates": [d.strftime("%Y-%m-%d") for d in future_dates],
            "predicted_demand": future_forecasts,
            "lower_95_ci": future_lower_95,
            "upper_95_ci": future_upper_95
        },
        "model_object": model_full
    }

def run_demand_forecasting(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Executes demand prediction across Total Market Volume and key high-demand roles.
    Saves trained models and returns forecast metrics and time-series representations.
    """
    if df is None:
        df = load_jobs_data()

    # Filter to dense period: Feb 13, 2024 onwards
    valid_df = df[df["published_date"].notna()].copy()
    valid_df["date"] = pd.to_datetime(valid_df["date"])
    dense_df = valid_df[valid_df["date"] >= pd.to_datetime("2024-02-13")].copy()
    
    # Daily counts overall
    daily_overall = dense_df.groupby("date").size()
    
    target_categories = [
        "Software & Web Development",
        "AI & Machine Learning",
        "Digital Marketing & SEO",
        "Video Production & Animation",
        "UI/UX & Creative Design",
        "Data Science & Analytics"
    ]
    
    models_dict = {}
    role_forecasts = []

    # 1. Total Market Volume
    print("Forecasting Total Market Volume...")
    total_forecast = train_and_forecast_role(daily_overall, "Overall Job Market", forecast_horizon=30)
    models_dict["Overall Job Market"] = total_forecast.pop("model_object")
    role_forecasts.append(total_forecast)

    # 2. Individual Categories
    for cat in target_categories:
        print(f"Forecasting {cat}...")
        cat_df = dense_df[dense_df["category"] == cat]
        cat_daily = cat_df.groupby("date").size().reindex(daily_overall.index, fill_value=0)
        
        cat_result = train_and_forecast_role(cat_daily, cat, forecast_horizon=30)
        models_dict[cat] = cat_result.pop("model_object")
        role_forecasts.append(cat_result)

    # Save models
    config.FORECAST_MODELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(models_dict, config.FORECAST_MODELS_PATH)
    print(f"Forecast models saved to {config.FORECAST_MODELS_PATH}")

    # Summary table
    metrics_summary = [
        {
            "Role / Domain": rf["role_name"],
            "MAE": rf["metrics"]["MAE"],
            "RMSE": rf["metrics"]["RMSE"],
            "MAPE (%)": f"{rf['metrics']['MAPE']}%",
            "R² Score": rf["metrics"]["R2_Score"]
        }
        for rf in role_forecasts
    ]

    return {
        "models_summary": metrics_summary,
        "forecasts": role_forecasts
    }

if __name__ == "__main__":
    results = run_demand_forecasting()
    print("=== Task 3 Forecasting Summary ===")
    for m in results["models_summary"]:
        print(f" - {m['Role / Domain']}: MAE={m['MAE']}, RMSE={m['RMSE']}, MAPE={m['MAPE (%)']}, R²={m['R² Score']}")
