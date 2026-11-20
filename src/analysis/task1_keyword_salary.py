"""
Task 1: Analyze the correlation between job title keywords and offered salaries.
Computes Pearson, Spearman correlations, ANOVA tests, regression coefficients,
seniority premiums, and statistical significance.
"""
import re
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression

import config
from src.data.loader import load_jobs_data

def analyze_keyword_salaries(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Performs full statistical correlation and regression analysis between
    job title keywords and offered salaries (hourly rates and fixed budgets).
    """
    if df is None:
        df = load_jobs_data()

    # Filter to valid hourly rates
    hourly_df = df[df["hourly_rate"].notna() & (df["hourly_rate"] > 0)].copy()
    overall_mean_hourly = float(hourly_df["hourly_rate"].mean())
    overall_median_hourly = float(hourly_df["hourly_rate"].median())
    overall_std_hourly = float(hourly_df["hourly_rate"].std())

    # Filter to valid fixed budgets
    budget_df = df[df["budget_clean"].notna() & (df["budget_clean"] > 0)].copy()
    overall_mean_budget = float(budget_df["budget_clean"].mean())
    overall_median_budget = float(budget_df["budget_clean"].median())

    # Define comprehensive list of target keywords to evaluate
    eval_keywords = [
        # AI & Data
        "AI", "Machine Learning", "Deep Learning", "LLM", "Data Science", "Data Engineer",
        "NLP", "Computer Vision", "Python", "SQL", "Tableau", "Power BI",
        # Web & Dev
        "Full Stack", "Frontend", "Backend", "React", "Node.js", "Django", "Vue", "Angular",
        "Next.js", "PHP", "WordPress", "Laravel", "JavaScript", "TypeScript", "Go", "Rust",
        # Cloud & DevOps
        "AWS", "Azure", "GCP", "DevOps", "Docker", "Kubernetes", "Cybersecurity",
        # Mobile
        "Flutter", "React Native", "iOS", "Android", "Swift",
        # Design & Media
        "UI/UX", "Figma", "Graphic Design", "Logo Design", "Video Editing", "Animation",
        # Marketing & Writing
        "SEO", "Google Ads", "Facebook Ads", "Media Buyer", "Content Writer", "Copywriter",
        # Ops & Other
        "Virtual Assistant", "Lead Generation", "Shopify", "Blockchain", "Web3", "Solidity"
    ]

    keyword_stats = []
    reg_features = []

    for kw in eval_keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        
        # Indicator mask for hourly
        mask_hourly = hourly_df["title_clean"].str.lower().str.contains(pattern, regex=True, na=False)
        count_hourly = int(mask_hourly.sum())

        # Indicator mask for budget
        mask_budget = budget_df["title_clean"].str.lower().str.contains(pattern, regex=True, na=False)
        count_budget = int(mask_budget.sum())

        if count_hourly >= 15:
            kw_rates = hourly_df.loc[mask_hourly, "hourly_rate"]
            non_kw_rates = hourly_df.loc[~mask_hourly, "hourly_rate"]
            
            mean_rate = float(kw_rates.mean())
            median_rate = float(kw_rates.median())
            std_rate = float(kw_rates.std())
            q25 = float(kw_rates.quantile(0.25))
            q75 = float(kw_rates.quantile(0.75))

            # Pearson Correlation & p-value
            pearson_corr, pearson_p = stats.pearsonr(mask_hourly.astype(int), hourly_df["hourly_rate"])
            # Spearman Correlation & p-value
            spearman_corr, spearman_p = stats.spearmanr(mask_hourly.astype(int), hourly_df["hourly_rate"])
            # One-Way ANOVA F-test
            f_stat, anova_p = stats.f_oneway(kw_rates, non_kw_rates)

            # Budget stats
            budget_mean = float(budget_df.loc[mask_budget, "budget_clean"].mean()) if count_budget > 5 else 0.0
            budget_median = float(budget_df.loc[mask_budget, "budget_clean"].median()) if count_budget > 5 else 0.0

            hourly_diff = mean_rate - overall_mean_hourly
            percent_premium = (hourly_diff / overall_mean_hourly) * 100.0

            keyword_stats.append({
                "keyword": kw,
                "job_count_hourly": count_hourly,
                "job_count_budget": count_budget,
                "mean_hourly_rate": round(mean_rate, 2),
                "median_hourly_rate": round(median_rate, 2),
                "std_hourly_rate": round(std_rate, 2),
                "iqr_25": round(q25, 2),
                "iqr_75": round(q75, 2),
                "hourly_premium": round(hourly_diff, 2),
                "percent_premium": round(percent_premium, 1),
                "pearson_corr": round(float(pearson_corr), 4),
                "pearson_p": float(pearson_p),
                "spearman_corr": round(float(spearman_corr), 4),
                "spearman_p": float(spearman_p),
                "f_stat": round(float(f_stat), 2),
                "anova_p": float(anova_p),
                "mean_budget": round(budget_mean, 2),
                "median_budget": round(budget_median, 2)
            })

            hourly_df[f"kw_{kw}"] = mask_hourly.astype(int)
            reg_features.append(f"kw_{kw}")

    # Multiple Regression Model to estimate simultaneous independent keyword coefficients
    reg_results = {}
    if reg_features:
        X = hourly_df[reg_features]
        y = hourly_df["hourly_rate"]
        reg_model = LinearRegression()
        reg_model.fit(X, y)
        
        base_intercept = float(reg_model.intercept_)
        r2_score = float(reg_model.score(X, y))

        for feat, coef in zip(reg_features, reg_model.coef_):
            clean_kw = feat.replace("kw_", "")
            reg_results[clean_kw] = {
                "coefficient_dollar_impact": round(float(coef), 2),
                "model_intercept": round(base_intercept, 2),
                "model_r2": round(r2_score, 4)
            }
        
        # Merge regression impact into keyword_stats
        for stat_item in keyword_stats:
            kw = stat_item["keyword"]
            if kw in reg_results:
                stat_item["regression_coef"] = reg_results[kw]["coefficient_dollar_impact"]
            else:
                stat_item["regression_coef"] = 0.0

    # Sort keywords by mean hourly rate
    keyword_stats.sort(key=lambda x: x["mean_hourly_rate"], reverse=True)

    # Seniority Analysis
    seniority_stats = []
    for level in ["Lead / Principal / Architect", "Senior", "Mid / Standard", "Junior / Entry", "Not Specified"]:
        sub = hourly_df[hourly_df["seniority"] == level]
        if len(sub) > 0:
            seniority_stats.append({
                "seniority": level,
                "count": len(sub),
                "mean_hourly": round(float(sub["hourly_rate"].mean()), 2),
                "median_hourly": round(float(sub["hourly_rate"].median()), 2),
                "p25": round(float(sub["hourly_rate"].quantile(0.25)), 2),
                "p75": round(float(sub["hourly_rate"].quantile(0.75)), 2)
            })

    return {
        "overall_metrics": {
            "total_hourly_jobs": len(hourly_df),
            "total_budget_jobs": len(budget_df),
            "overall_mean_hourly": round(overall_mean_hourly, 2),
            "overall_median_hourly": round(overall_median_hourly, 2),
            "overall_std_hourly": round(overall_std_hourly, 2),
            "overall_mean_budget": round(overall_mean_budget, 2),
            "overall_median_budget": round(overall_median_budget, 2)
        },
        "keyword_correlations": keyword_stats,
        "seniority_premium": seniority_stats,
        "top_paying_keywords": keyword_stats[:15],
        "top_discount_keywords": sorted(keyword_stats, key=lambda x: x["mean_hourly_rate"])[:10],
        "regression_model_summary": {
            "r2_score": reg_results.get(eval_keywords[0], {}).get("model_r2", 0.0) if reg_results else 0.0,
            "base_rate": reg_results.get(eval_keywords[0], {}).get("model_intercept", 0.0) if reg_results else 0.0
        }
    }

if __name__ == "__main__":
    results = analyze_keyword_salaries()
    print("=== Task 1 Analysis Summary ===")
    print(f"Evaluated {len(results['keyword_correlations'])} keywords.")
    print("Top 5 Highest Paying Keywords:")
    for k in results["top_paying_keywords"][:5]:
        print(f" - {k['keyword']}: ${k['mean_hourly_rate']}/hr (Pearson r={k['pearson_corr']}, p={k['pearson_p']:.2e})")
