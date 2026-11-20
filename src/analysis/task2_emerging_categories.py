"""
Task 2: Identify emerging job categories based on posting frequency and growth rate over time.
Computes period-over-period growth, momentum scores, trend slopes, and micro-niche breakouts.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

import config
from src.data.loader import load_jobs_data

def analyze_emerging_categories(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Analyzes posting frequencies over time across categories to identify
    emerging, high-growth, and maturing sectors of the freelance job market.
    """
    if df is None:
        df = load_jobs_data()

    # Filter to valid dates
    valid_df = df[df["published_date"].notna()].copy()
    valid_df["date"] = pd.to_datetime(valid_df["date"])
    
    # Filter to dense period: starting from 2024-02-13 where continuous data is collected
    dense_df = valid_df[valid_df["date"] >= pd.to_datetime("2024-02-13")].copy()
    
    # Group by week
    dense_df["week_period"] = dense_df["date"].dt.to_period("W").astype(str)
    unique_weeks = sorted(dense_df["week_period"].unique())
    
    # Weekly category cross-tabulation
    weekly_cat = pd.crosstab(dense_df["week_period"], dense_df["category"])
    
    # Analyze each category
    category_growth = []
    
    first_half_weeks = unique_weeks[:len(unique_weeks)//2]
    second_half_weeks = unique_weeks[len(unique_weeks)//2:]

    for cat in weekly_cat.columns:
        if cat == "Other / General":
            continue
            
        counts_series = weekly_cat[cat]
        v1 = counts_series.loc[first_half_weeks].mean()
        v2 = counts_series.loc[second_half_weeks].mean()
        total_vol = int(counts_series.sum())
        
        # Percentage growth
        pct_growth = ((v2 - v1) / (v1 + 1e-5)) * 100.0
        
        # Regression trend slope
        x = np.arange(len(counts_series))
        y = counts_series.values
        if len(x) > 1:
            slope, intercept = np.polyfit(x, y, 1)
        else:
            slope = 0.0
            
        # Momentum score = Growth Rate * log10(Total Volume)
        momentum = float(pct_growth * np.log10(max(total_vol, 10)))

        # Classification
        if pct_growth > 15.0 and total_vol > 500:
            classification = "High-Growth Emerging"
        elif pct_growth >= 0.0 and total_vol > 5000:
            classification = "Established Powerhouse"
        elif pct_growth >= 0.0:
            classification = "Steady Growth"
        else:
            classification = "Maturing / Stable"

        category_growth.append({
            "category": cat,
            "total_postings": total_vol,
            "early_period_avg_weekly": round(float(v1), 1),
            "late_period_avg_weekly": round(float(v2), 1),
            "growth_rate_pct": round(float(pct_growth), 2),
            "trend_slope": round(float(slope), 2),
            "momentum_score": round(momentum, 2),
            "status": classification,
            "weekly_trend": [int(val) for val in counts_series.values]
        })

    # Sort categories by momentum score
    category_growth.sort(key=lambda x: x["momentum_score"], reverse=True)

    # Emerging Micro-Niches analysis (sub-keywords inside the titles)
    micro_niches = [
        {"keyword": "LLM / LangChain / RAG", "pattern": r"llm|langchain|rag|vector db|vector database"},
        {"keyword": "Generative AI / ChatGPT", "pattern": r"chatgpt|generative ai|openai|gpt-4"},
        {"keyword": "TikTok & Shorts Video Editing", "pattern": r"tiktok|reels|shorts|capcut"},
        {"keyword": "AI Automation / Make / Zapier", "pattern": r"make\.com|zapier|n8n|automation"},
        {"keyword": "Next.js & Fullstack React", "pattern": r"next\.js|nextjs|tailwind"},
        {"keyword": "Flutter Cross-Platform", "pattern": r"flutter"},
        {"keyword": "Cold Outreach & B2B Leads", "pattern": r"cold email|cold outreach|appointment setter"},
        {"keyword": "Shopify Plus / Dropshipping", "pattern": r"shopify plus|dropshipping|e-commerce store"},
        {"keyword": "Solana & Web3 DApps", "pattern": r"solana|smart contract|dapp"}
    ]

    micro_niche_results = []
    for niche in micro_niches:
        mask = dense_df["title_clean"].str.lower().str.contains(niche["pattern"], regex=True, na=False)
        sub_df = dense_df[mask]
        if len(sub_df) > 10:
            weekly_sub = sub_df.groupby("week_period").size().reindex(unique_weeks, fill_value=0)
            v1_sub = weekly_sub.loc[first_half_weeks].mean()
            v2_sub = weekly_sub.loc[second_half_weeks].mean()
            growth_sub = ((v2_sub - v1_sub) / (v1_sub + 1e-5)) * 100.0
            
            micro_niche_results.append({
                "niche": niche["keyword"],
                "total_postings": int(len(sub_df)),
                "growth_rate_pct": round(float(growth_sub), 1),
                "weekly_volume": [int(x) for x in weekly_sub.values]
            })

    micro_niche_results.sort(key=lambda x: x["growth_rate_pct"], reverse=True)

    return {
        "analysis_period": {
            "start_week": unique_weeks[0],
            "end_week": unique_weeks[-1],
            "total_weeks": len(unique_weeks),
            "week_labels": unique_weeks
        },
        "category_growth_ranking": category_growth,
        "emerging_categories": [c for c in category_growth if c["status"] == "High-Growth Emerging"],
        "established_powerhouses": [c for c in category_growth if c["status"] == "Established Powerhouse"],
        "micro_niche_breakouts": micro_niche_results
    }

if __name__ == "__main__":
    results = analyze_emerging_categories()
    print("=== Task 2 Analysis Summary ===")
    print("Top Emerging / High-Growth Categories:")
    for c in results["category_growth_ranking"][:5]:
        print(f" - {c['category']}: {c['growth_rate_pct']}% growth (Postings: {c['total_postings']}, Momentum: {c['momentum_score']})")
