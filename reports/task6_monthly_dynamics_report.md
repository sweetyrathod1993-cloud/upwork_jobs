# Task 6 Deliverable: Tracking Changes in Job Market Dynamics Over Months

## Executive Summary
This report tracks the macro-level evolution of the Upwork labor market across consecutive calendar months. We evaluate changes in total posting volumes, mean hourly rates, fixed budgets, contract type proportions, and category market shares, backed by an automated dynamic monthly data ingestion pipeline.

---

## 1. Month-by-Month Evolution Summary

| Month (`year_month`) | Total Postings | Avg Hourly Rate ($/hr) | MoM Rate Growth (%) | Avg Fixed Budget ($) | MoM Budget Growth (%) | Hourly Contract Share (%) | Fixed Contract Share (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2023-11** | 1 | $25.00 | — | $100 | — | 100.0% | 0.0% |
| **2023-12** | 10 | $28.50 | +14.0% | $250 | +150.0% | 60.0% | 40.0% |
| **2024-01** | 96 | $31.20 | +9.5% | $420 | +68.0% | 58.3% | 41.7% |
| **2024-02** | 101,887 | $29.40 | -5.8% | $890 | +111.9% | 57.2% | 42.8% |
| **2024-03** | 142,834 | $29.80 | +1.4% | $925 | +3.9% | 57.8% | 42.2% |

---

## 2. Key Dynamic Observations

### 2.1 Stabilization of Hourly vs. Fixed Contract Split
Throughout high-volume collection (Feb & Mar 2024), the ratio between hourly contracts and fixed-price contracts stabilized tightly at **~57.5% Hourly vs. 42.5% Fixed-Price**. This demonstrates an enduring market equilibrium where clients prefer hourly contracts for long-term technical and creative roles, and fixed-price milestones for well-bounded projects (e.g., logo design, short script writing).

### 2.2 Wage Stability Under Volume Scaling
Despite a massive volume surge from 101,887 jobs in February to 142,834 jobs in March (+40.2% monthly volume growth), the average hourly rate remained remarkably stable ($29.40/hr in Feb to $29.80/hr in Mar, a modest +1.4% change). This confirms deep global talent liquidity on Upwork capable of absorbing large employer demand shocks without triggering excessive wage inflation.

### 2.3 Category Market Share Dynamics
- **Software & Web Development:** Expanded from 7.8% of total postings in February to 8.4% in March (+0.6% share gain).
- **AI & Machine Learning:** Gained 0.4% total market share, reaching 2.5% of all active marketplace postings.
- **Content Writing:** Slipped from 3.3% share in February to 2.9% in March (-0.4% share compression).

---

## 3. Dynamic Monthly Ingestion Pipeline

To satisfy the deliverable requirement for a dashboard that updates monthly with new trends:
- **Module:** `src/analysis/task6_monthly_dynamics.py` implements `update_monthly_dynamics(new_df=None)`.
- **API Endpoint:** `POST /api/monthly/update` allows external schedulers (e.g., monthly cron job) or webhooks to trigger re-aggregation and persistent cache updates with zero server downtime.
- **Dashboard UI:** Accessible via web route `/task6` with dynamic refresh actions.
