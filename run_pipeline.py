"""
End-to-End Orchestration Pipeline for Job Market Analysis and Recommendation System.
Executes all 8 tasks, builds models, precomputes metrics, saves caches, and generates deliverables.
"""
import sys
import json
import time
from pathlib import Path

import config
from src.data.preprocessor import preprocess_dataset
from src.data.loader import load_jobs_data
from src.analysis.task1_keyword_salary import analyze_keyword_salaries
from src.analysis.task2_emerging_categories import analyze_emerging_categories
from src.models.task3_demand_forecasting import run_demand_forecasting
from src.analysis.task4_country_rates import analyze_country_rates
from src.recommendation.engine import JobRecommendationEngine
from src.analysis.task6_monthly_dynamics import analyze_monthly_dynamics
from src.analysis.task7_remote_landscape import analyze_remote_landscape
from src.analysis.task8_future_scenarios import simulate_future_market_scenarios

def run_full_pipeline(force_reprocess: bool = False):
    start_time = time.time()
    print("=" * 70)
    print("JOB MARKET ANALYSIS & RECOMMENDATION SYSTEM - PIPELINE EXECUTION")
    print("=" * 70)

    # Step 1: Preprocessing & Database Sync
    print("\n>>> [Step 1/8] Preprocessing raw dataset and indexing database...")
    if force_reprocess or not config.PROCESSED_PARQUET_PATH.exists():
        df = preprocess_dataset()
    else:
        print("Preprocessed parquet exists. Loading...")
        df = load_jobs_data()

    print(f"Total jobs ready in corpus: {len(df):,}")

    # Step 2: Task 1 - Correlation between Keywords and Salaries
    print("\n>>> [Step 2/8] Executing Task 1: Keyword-Salary Correlation Analysis...")
    t1_results = analyze_keyword_salaries(df)
    print(f"Computed stats for {len(t1_results['keyword_correlations'])} keywords.")

    # Step 3: Task 2 - Emerging Job Categories
    print("\n>>> [Step 3/8] Executing Task 2: Emerging Categories Growth Analysis...")
    t2_results = analyze_emerging_categories(df)
    print(f"Ranked {len(t2_results['category_growth_ranking'])} categories.")

    # Step 4: Task 3 - Demand Forecasting Model
    print("\n>>> [Step 4/8] Executing Task 3: High-Demand Roles Predictive Forecasting...")
    t3_results = run_demand_forecasting(df)
    print(f"Trained forecast models for {len(t3_results['models_summary'])} sectors.")

    # Step 5: Task 4 - Country Hourly Rates
    print("\n>>> [Step 5/8] Executing Task 4: Global Hourly Rates Geography...")
    t4_results = analyze_country_rates(df)
    print(f"Analyzed hourly rates across {len(t4_results['all_countries'])} countries.")

    # Step 6: Task 5 - Recommendation Engine Indexing
    print("\n>>> [Step 6/8] Executing Task 5: Recommendation Engine Index Build...")
    recommender = JobRecommendationEngine()
    recommender.build_and_save_index(df)

    # Step 7: Task 6 - Monthly Dynamics
    print("\n>>> [Step 7/8] Executing Task 6: Tracking Monthly Market Dynamics...")
    t6_results = analyze_monthly_dynamics(df)
    print(f"Tracked dynamics across {len(t6_results['monthly_summary'])} months.")

    # Step 8: Task 7 & Task 8 - Remote Landscape & Future Scenarios
    print("\n>>> [Step 8/8] Executing Task 7 & Task 8: Remote Trends & Future Scenarios...")
    t7_results = analyze_remote_landscape(df)
    t8_results = simulate_future_market_scenarios(df)

    # Save aggregated metrics to JSON cache
    all_metrics = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_jobs": len(df),
        "task1": t1_results,
        "task2": t2_results,
        "task3": {
            "models_summary": t3_results["models_summary"],
            "forecasts": t3_results["forecasts"]
        },
        "task4": t4_results,
        "task6": t6_results,
        "task7": t7_results,
        "task8": t8_results
    }

    config.METRICS_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(config.METRICS_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nAll task metrics cached successfully at {config.METRICS_CACHE_PATH}")

    elapsed = round(time.time() - start_time, 2)
    print("=" * 70)
    print(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed} SECONDS!")
    print("=" * 70)

if __name__ == "__main__":
    force = "--force" in sys.argv
    run_full_pipeline(force_reprocess=force)
