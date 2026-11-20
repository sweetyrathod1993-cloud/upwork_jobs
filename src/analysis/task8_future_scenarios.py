"""
Task 8: Predict future job market trends.
Develops predictive analytics scenarios (Baseline, Accelerated AI Disruption,
Global Outsourcing Shift) with quarterly quantitative projections through 2026.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

import config
from src.data.loader import load_jobs_data

def simulate_future_market_scenarios(
    df: Optional[pd.DataFrame] = None,
    custom_ai_factor: float = 1.0,
    custom_outsourcing_factor: float = 1.0
) -> Dict[str, Any]:
    """
    Simulates three distinct macroeconomic and technological scenarios for the
    global freelance job market through 2026.
    """
    if df is None:
        df = load_jobs_data()

    base_volume = len(df)
    base_rate = float(df["hourly_rate"].dropna().mean())
    base_ai_volume = int((df["category"] == "AI & Machine Learning").sum())
    base_writing_volume = int((df["category"] == "Content & Copywriting").sum())
    base_web_volume = int((df["category"] == "Software & Web Development").sum())

    quarters = [
        "2024-Q1 (Base)", "2024-Q2", "2024-Q3", "2024-Q4",
        "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4",
        "2026-Q1", "2026-Q2", "2026-Q3", "2026-Q4"
    ]
    n_steps = len(quarters)

    # 1. SCENARIO A: Baseline Steady State
    # Volume: +3.2% quarterly compound; Rates: +0.8% quarterly compound
    vol_a, rates_a, ai_a, writing_a, web_a = [], [], [], [], []
    for t in range(n_steps):
        v = base_volume * ((1 + 0.032) ** t)
        r = base_rate * ((1 + 0.008) ** t)
        ai_v = base_ai_volume * ((1 + 0.08) ** t)
        w_v = base_writing_volume * ((1 + 0.01) ** t)
        web_v = base_web_volume * ((1 + 0.03) ** t)

        vol_a.append(int(v))
        rates_a.append(round(r, 2))
        ai_a.append(int(ai_v))
        writing_a.append(int(w_v))
        web_a.append(int(web_v))

    # 2. SCENARIO B: Accelerated AI Disruption & Agentic Automation
    # AI demand rockets (+22% quarterly); Repetitive writing/data entry contracts (-7% quarterly); Rates diverge
    vol_b, rates_b, ai_b, writing_b, web_b = [], [], [], [], []
    for t in range(n_steps):
        # AI surge multiplier
        v = base_volume * ((1 + 0.05 * custom_ai_factor) ** t)
        r = base_rate * ((1 + 0.015 * custom_ai_factor) ** t)
        ai_v = base_ai_volume * ((1 + 0.20 * custom_ai_factor) ** t)
        w_v = base_writing_volume * ((1 - 0.06 * custom_ai_factor) ** t)
        web_v = base_web_volume * ((1 + 0.04 * custom_ai_factor) ** t)

        vol_b.append(int(v))
        rates_b.append(round(r, 2))
        ai_b.append(int(ai_v))
        writing_b.append(int(max(w_v, 100)))
        web_b.append(int(web_v))

    # 3. SCENARIO C: Global Economic Tightening & Offshore Outsourcing Surge
    # Total volume accelerates rapidly (+7.5% quarterly) as enterprise cuts local staff; Rates remain competitive (+0.4% quarterly)
    vol_c, rates_c, ai_c, writing_c, web_c = [], [], [], [], []
    for t in range(n_steps):
        v = base_volume * ((1 + 0.075 * custom_outsourcing_factor) ** t)
        r = base_rate * ((1 + 0.004) ** t)
        ai_v = base_ai_volume * ((1 + 0.09) ** t)
        w_v = base_writing_volume * ((1 + 0.03) ** t)
        web_v = base_web_volume * ((1 + 0.08 * custom_outsourcing_factor) ** t)

        vol_c.append(int(v))
        rates_c.append(round(r, 2))
        ai_c.append(int(ai_v))
        writing_c.append(int(w_v))
        web_c.append(int(web_v))

    return {
        "simulation_parameters": {
            "quarters": quarters,
            "custom_ai_factor": custom_ai_factor,
            "custom_outsourcing_factor": custom_outsourcing_factor
        },
        "scenarios": {
            "baseline": {
                "name": "Scenario A: Baseline Continuous Growth",
                "description": "Steady market expansion in line with historical freelance adoption. Balanced growth across technical, marketing, and creative sectors.",
                "total_volume": vol_a,
                "avg_hourly_rate": rates_a,
                "ai_ml_volume": ai_a,
                "writing_volume": writing_a,
                "web_dev_volume": web_a,
                "terminal_volume_2026": vol_a[-1],
                "terminal_rate_2026": rates_a[-1]
            },
            "ai_disruption": {
                "name": "Scenario B: Accelerated AI & Agentic Disruption",
                "description": "Explosive growth in AI development, LLM fine-tuning, and RAG pipelines. Repetitive entry-level writing and data entry contracts compress while senior AI architects command unprecedented hourly premiums.",
                "total_volume": vol_b,
                "avg_hourly_rate": rates_b,
                "ai_ml_volume": ai_b,
                "writing_volume": writing_b,
                "web_dev_volume": web_b,
                "terminal_volume_2026": vol_b[-1],
                "terminal_rate_2026": rates_b[-1]
            },
            "economic_outsourcing": {
                "name": "Scenario C: Enterprise Tightening & Offshore Outsourcing",
                "description": "Macroeconomic restructuring drives corporate enterprises to replace full-time domestic headcount with agile freelance squads across India, Latin America, and Eastern Europe.",
                "total_volume": vol_c,
                "avg_hourly_rate": rates_c,
                "ai_ml_volume": ai_c,
                "writing_volume": writing_c,
                "web_dev_volume": web_c,
                "terminal_volume_2026": vol_c[-1],
                "terminal_rate_2026": rates_c[-1]
            }
        },
        "strategic_takeaways": [
            {
                "persona": "Job Seekers / Freelancers",
                "recommendation": "Transition from generalist skillsets to AI-native workflows. Combine domain knowledge with prompt engineering, Python, and automated pipeline tooling to maintain pricing power."
            },
            {
                "persona": "Recruiters & Hiring Managers",
                "recommendation": "Shift compensation models toward outcome-based milestones and hourly contracts with verified portfolio proof. Leverage global talent pools in Eastern Europe and South Asia for maximum ROI."
            },
            {
                "persona": "Enterprises & Startups",
                "recommendation": "Build hybrid teams consisting of core in-house product leads managing elastic on-demand global freelancers for burst development cycles."
            }
        ]
    }

if __name__ == "__main__":
    results = simulate_future_market_scenarios()
    print("=== Task 8 Future Scenarios Summary ===")
    for k, sc in results["scenarios"].items():
        print(f"[{sc['name']}] 2026 Vol: {sc['terminal_volume_2026']:,} | Rate: ${sc['terminal_rate_2026']}/hr")
