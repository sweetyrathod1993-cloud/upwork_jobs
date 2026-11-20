"""
Task 6: Track changes in job market dynamics over months.
Monitors posting volume, hourly rate trends, budget shifts, category share evolution,
and provides an automated monthly dynamic update engine for dashboards.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

import config
from src.data.loader import load_jobs_data

def analyze_monthly_dynamics(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Computes month-by-month market indicators, shift deltas, and category shares.
    """
    if df is None:
        df = load_jobs_data()

    # Ensure year_month column exists and sort chronologically
    valid_df = df[df["published_date"].notna()].copy()
    valid_df["year_month"] = pd.to_datetime(valid_df["published_date"]).dt.strftime("%Y-%m")
    
    # We focus on months with meaningful volume (e.g., 2024-01, 2024-02, 2024-03)
    # Plus historical Nov/Dec 2023 for baseline comparisons
    monthly_groups = valid_df.groupby("year_month")

    monthly_summary = []
    
    prev_volume = None
    prev_rate = None
    prev_budget = None

    for ym, group in sorted(monthly_groups):
        vol = len(group)
        hourly_sub = group[group["hourly_rate"].notna()]
        budget_sub = group[group["budget_clean"].notna()]

        avg_rate = float(hourly_sub["hourly_rate"].mean()) if len(hourly_sub) > 0 else 0.0
        median_rate = float(hourly_sub["hourly_rate"].median()) if len(hourly_sub) > 0 else 0.0
        avg_budget = float(budget_sub["budget_clean"].mean()) if len(budget_sub) > 0 else 0.0
        
        pct_hourly = (len(hourly_sub) / vol * 100.0) if vol > 0 else 0.0

        # MoM Deltas
        vol_change = ((vol - prev_volume) / prev_volume * 100.0) if prev_volume and prev_volume > 0 else 0.0
        rate_change = ((avg_rate - prev_rate) / prev_rate * 100.0) if prev_rate and prev_rate > 0 else 0.0
        budget_change = ((avg_budget - prev_budget) / prev_budget * 100.0) if prev_budget and prev_budget > 0 else 0.0

        # Top 3 categories this month
        cat_counts = group["category"].value_counts()
        top_cats = [
            {"name": cat, "count": int(cnt), "share_pct": round(cnt / vol * 100.0, 1)}
            for cat, cnt in cat_counts.head(4).items()
            if cat != "Other / General"
        ]

        # Top 3 countries this month
        country_counts = group["country"].value_counts()
        top_countries = [
            {"country": c, "count": int(cnt)}
            for c, cnt in country_counts.head(3).items()
            if c not in ["Unknown", ""]
        ]

        monthly_summary.append({
            "year_month": ym,
            "total_postings": vol,
            "avg_hourly_rate": round(avg_rate, 2),
            "median_hourly_rate": round(median_rate, 2),
            "avg_budget": round(avg_budget, 2),
            "pct_hourly": round(pct_hourly, 1),
            "pct_fixed": round(100.0 - pct_hourly, 1),
            "volume_growth_mom_pct": round(vol_change, 1),
            "rate_change_mom_pct": round(rate_change, 1),
            "budget_change_mom_pct": round(budget_change, 1),
            "top_categories": top_cats,
            "top_countries": top_countries
        })

        prev_volume = vol
        prev_rate = avg_rate
        prev_budget = avg_budget

    # Weekly breakdown for the latest dense months (Feb - March 2024)
    dense_df = valid_df[valid_df["date"] >= "2024-02-01"].copy()
    dense_df["week"] = pd.to_datetime(dense_df["date"]).dt.to_period("W").astype(str)
    
    weekly_trends = []
    for wk, w_group in dense_df.groupby("week"):
        w_vol = len(w_group)
        w_rate = float(w_group["hourly_rate"].dropna().mean()) if len(w_group["hourly_rate"].dropna()) > 0 else 0.0
        weekly_trends.append({
            "week": str(wk),
            "postings": w_vol,
            "avg_hourly_rate": round(w_rate, 2)
        })

    return {
        "monthly_summary": monthly_summary,
        "weekly_dense_trends": weekly_trends,
        "latest_month": monthly_summary[-1] if monthly_summary else {},
        "penultimate_month": monthly_summary[-2] if len(monthly_summary) >= 2 else {}
    }

def update_monthly_dynamics(new_df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """Dynamic update handler called when new monthly data is ingested."""
    return analyze_monthly_dynamics(new_df)

if __name__ == "__main__":
    results = analyze_monthly_dynamics()
    print("=== Task 6 Monthly Dynamics Summary ===")
    for m in results["monthly_summary"]:
        print(f"Month {m['year_month']}: {m['total_postings']} jobs | Avg Rate: ${m['avg_hourly_rate']}/hr | Hourly %: {m['pct_hourly']}% | MoM Vol Growth: {m['volume_growth_mom_pct']}%")
