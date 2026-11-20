"""
Task 4: Compare average hourly rates across different countries.
Performs geographical rate aggregation, statistical benchmarking, regional clustering,
and prepares data for interactive world choropleth maps and comparative visualizations.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

import config
from src.data.loader import load_jobs_data

# ISO Alpha-3 mapping for robust Plotly choropleth rendering
ISO_3_MAP = {
    "United States": "USA", "United Kingdom": "GBR", "India": "IND", "Australia": "AUS",
    "Canada": "CAN", "Pakistan": "PAK", "Germany": "DEU", "Netherlands": "NLD",
    "United Arab Emirates": "ARE", "France": "FRA", "Spain": "ESP", "Singapore": "SGP",
    "Philippines": "PHL", "China": "CHN", "Israel": "ISR", "Ukraine": "UKR",
    "Italy": "ITA", "Bangladesh": "BGD", "Switzerland": "CHE", "Saudi Arabia": "SAU",
    "Nigeria": "NGA", "Poland": "POL", "Ireland": "IRL", "Brazil": "BRA",
    "Sweden": "SWE", "South Africa": "ZAF", "Belgium": "BEL", "Egypt": "EGY",
    "Mexico": "MEX", "New Zealand": "NZL", "Turkey": "TUR", "Kenya": "KEN",
    "Hong Kong": "HKG", "Austria": "AUT", "Indonesia": "IDN", "Denmark": "DNK",
    "Portugal": "PRT", "Vietnam": "VNM", "Romania": "ROU", "Norway": "NOR",
    "Greece": "GRC", "Czech Republic": "CZE", "Finland": "FIN", "Japan": "JPN",
    "Malaysia": "MYS", "Colombia": "COL", "Argentina": "ARG", "Hungary": "HUN",
    "Cyprus": "CYP", "Estonia": "EST", "Lithuania": "LTU", "Chile": "CHL",
    "Thailand": "THA", "Bulgaria": "BGR", "South Korea": "KOR", "Morocco": "MAR"
}

def analyze_country_rates(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Computes country-level wage statistics, regional benchmarks, and interactive map data.
    """
    if df is None:
        df = load_jobs_data()

    # Filter out Unknown countries
    known_df = df[df["country"].notna() & (df["country"] != "Unknown") & (df["country"] != "")].copy()
    
    # Calculate global benchmarks
    global_hourly_mean = float(known_df["hourly_rate"].dropna().mean())
    global_hourly_median = float(known_df["hourly_rate"].dropna().median())

    country_records = []
    grouped = known_df.groupby("country")

    for country, group in grouped:
        total_jobs = len(group)
        hourly_sub = group[group["hourly_rate"].notna()]
        budget_sub = group[group["budget_clean"].notna()]
        
        hourly_count = len(hourly_sub)
        budget_count = len(budget_sub)

        if hourly_count >= 10:
            mean_rate = float(hourly_sub["hourly_rate"].mean())
            median_rate = float(hourly_sub["hourly_rate"].median())
            std_rate = float(hourly_sub["hourly_rate"].std())
            p25 = float(hourly_sub["hourly_rate"].quantile(0.25))
            p75 = float(hourly_sub["hourly_rate"].quantile(0.75))
        else:
            mean_rate = 0.0
            median_rate = 0.0
            std_rate = 0.0
            p25 = 0.0
            p75 = 0.0

        mean_budget = float(budget_sub["budget_clean"].mean()) if budget_count >= 5 else 0.0
        
        # Most frequent job category hired in this country
        top_cat = group["category"].value_counts().index[0] if len(group) > 0 else "N/A"
        if top_cat == "Other / General" and len(group["category"].value_counts()) > 1:
            top_cat = group["category"].value_counts().index[1]

        hourly_ratio = (hourly_count / total_jobs * 100.0) if total_jobs > 0 else 0.0

        country_records.append({
            "country": country,
            "iso3": ISO_3_MAP.get(country, ""),
            "total_jobs": total_jobs,
            "hourly_jobs": hourly_count,
            "budget_jobs": budget_count,
            "mean_hourly_rate": round(mean_rate, 2),
            "median_hourly_rate": round(median_rate, 2),
            "std_hourly_rate": round(std_rate, 2),
            "p25_hourly_rate": round(p25, 2),
            "p75_hourly_rate": round(p75, 2),
            "mean_budget": round(mean_budget, 2),
            "hourly_ratio_pct": round(hourly_ratio, 1),
            "top_category": top_cat
        })

    # Sort countries with statistically reliable sample (>= 50 hourly jobs) by mean hourly rate
    reliable_countries = [c for c in country_records if c["hourly_jobs"] >= 50]
    top_paying_countries = sorted(reliable_countries, key=lambda x: x["mean_hourly_rate"], reverse=True)
    
    # Countries by volume
    top_volume_countries = sorted(country_records, key=lambda x: x["total_jobs"], reverse=True)

    # Regional Aggregation
    regions = {
        "North America": ["United States", "Canada", "Mexico"],
        "Western Europe": ["United Kingdom", "Germany", "France", "Netherlands", "Switzerland", "Belgium", "Austria", "Ireland", "Norway", "Sweden", "Denmark", "Finland"],
        "Southern & Eastern Europe": ["Spain", "Italy", "Poland", "Ukraine", "Romania", "Greece", "Portugal", "Czech Republic", "Hungary", "Bulgaria", "Estonia", "Lithuania"],
        "Asia-Pacific": ["Australia", "India", "Singapore", "China", "Philippines", "Pakistan", "Bangladesh", "Japan", "South Korea", "Indonesia", "Vietnam", "Malaysia", "New Zealand"],
        "Middle East & North Africa": ["United Arab Emirates", "Israel", "Saudi Arabia", "Turkey", "Egypt", "Morocco", "Qatar", "Kuwait"],
        "Latin America": ["Brazil", "Argentina", "Colombia", "Chile", "Peru"],
        "Sub-Saharan Africa": ["Nigeria", "Kenya", "South Africa", "Ghana"]
    }

    region_stats = []
    for reg_name, c_list in regions.items():
        reg_df = known_df[known_df["country"].isin(c_list)]
        reg_hourly = reg_df[reg_df["hourly_rate"].notna()]
        if len(reg_hourly) > 0:
            region_stats.append({
                "region": reg_name,
                "total_jobs": len(reg_df),
                "hourly_jobs": len(reg_hourly),
                "mean_hourly_rate": round(float(reg_hourly["hourly_rate"].mean()), 2),
                "median_hourly_rate": round(float(reg_hourly["hourly_rate"].median()), 2),
                "mean_budget": round(float(reg_df["budget_clean"].dropna().mean()), 2) if len(reg_df["budget_clean"].dropna()) > 0 else 0.0
            })

    region_stats.sort(key=lambda x: x["mean_hourly_rate"], reverse=True)

    return {
        "global_benchmarks": {
            "overall_mean_hourly": round(global_hourly_mean, 2),
            "overall_median_hourly": round(global_hourly_median, 2),
            "total_countries": len(country_records),
            "total_analyzed_jobs": len(known_df)
        },
        "all_countries": country_records,
        "top_paying_countries": top_paying_countries[:20],
        "top_volume_countries": top_volume_countries[:20],
        "regional_breakdown": region_stats,
        "choropleth_data": [
            {
                "country": c["country"],
                "iso3": c["iso3"],
                "mean_hourly_rate": c["mean_hourly_rate"],
                "total_jobs": c["total_jobs"],
                "top_category": c["top_category"]
            }
            for c in country_records if c["iso3"] and c["hourly_jobs"] >= 10
        ]
    }

if __name__ == "__main__":
    results = analyze_country_rates()
    print("=== Task 4 Geography Analysis Summary ===")
    print("Top 5 Highest Paying Countries (min 50 jobs):")
    for c in results["top_paying_countries"][:5]:
        print(f" - {c['country']}: ${c['mean_hourly_rate']}/hr (Median: ${c['median_hourly_rate']}, Jobs: {c['total_jobs']})")
