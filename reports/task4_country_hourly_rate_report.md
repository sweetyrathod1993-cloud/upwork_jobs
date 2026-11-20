# Task 4 Deliverable: Comparison of Average Hourly Rates Across Different Countries

## Executive Summary
This report analyzes geographic wage differentials across **212 countries and territories** represented in the Upwork job postings corpus. We examine average hourly rates, median rates, fixed-price budgets, and market volume concentration, presenting empirical insights into global labor arbitrage and cross-border freelance hiring.

---

## 1. Geospatial Wage Aggregation Methodology
- **Sample Screening:** Filtered records with identified client countries and non-null hourly rates ($3.00/hr to $350.00/hr).
- **Statistical Filtering:** Countries with fewer than 50 hourly job postings were classified as exploratory, while countries with $\ge 50$ hourly job postings were evaluated for statistical benchmarks.
- **ISO-3 Geospatial Mapping:** Country names were mapped to ISO Alpha-3 codes to enable high-resolution choropleth rendering on natural-earth world projections.

---

## 2. Global Wage Hierarchy (Top Paying Countries)

Clients residing in high-income Western economies and specialized technology hubs offer the highest mean hourly rates:

| Rank | Country | ISO-3 | Total Jobs | Hourly Jobs | Mean Hourly Rate ($/hr) | Median Rate ($/hr) | Hourly Contract Share (%) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Switzerland** | CHE | 1,767 | 812 | **$44.80** | $40.00 | 45.9% |
| **2** | **United States** | USA | 99,834 | 44,210 | **$38.90** | $35.00 | 44.3% |
| **3** | **Australia** | AUS | 12,618 | 5,680 | **$37.50** | $32.00 | 45.0% |
| **4** | **Norway** | NOR | 740 | 320 | **$37.10** | $35.00 | 43.2% |
| **5** | **Canada** | CAN | 11,658 | 5,120 | **$36.40** | $30.00 | 43.9% |
| **6** | **Denmark** | DNK | 850 | 385 | **$36.20** | $32.50 | 45.3% |
| **7** | **United Kingdom** | GBR | 19,149 | 8,420 | **$35.80** | $30.00 | 44.0% |
| **8** | **Germany** | DEU | 4,844 | 2,150 | **$35.20** | $30.00 | 44.4% |
| **9** | **Netherlands** | NLD | 4,435 | 1,940 | **$34.60** | $30.00 | 43.7% |
| **10** | **Israel** | ISR | 2,082 | 910 | **$34.10** | $30.00 | 43.7% |
| **11** | **Singapore** | SGP | 2,501 | 1,080 | **$33.80** | $30.00 | 43.2% |
| **12** | **United Arab Emirates**| ARE | 4,039 | 1,720 | **$32.50** | $28.00 | 42.6% |
| **13** | **Sweden** | SWE | 1,180 | 510 | **$32.10** | $28.00 | 43.2% |
| **14** | **France** | FRA | 3,163 | 1,350 | **$31.80** | $27.50 | 42.7% |
| **15** | **Ireland** | IRL | 1,220 | 540 | **$31.40** | $28.00 | 44.3% |

---

## 3. Client Volume Concentration (Largest Hiring Markets)

The top 5 countries account for over **66% of all job postings** globally:

1. **United States:** 99,834 jobs (40.8% market share) | Mean Rate: $38.90/hr | Mean Budget: $940
2. **United Kingdom:** 19,149 jobs (7.8% market share) | Mean Rate: $35.80/hr | Mean Budget: $880
3. **India:** 15,835 jobs (6.5% market share) | Mean Rate: $18.40/hr | Mean Budget: $410
4. **Australia:** 12,618 jobs (5.2% market share) | Mean Rate: $37.50/hr | Mean Budget: $890
5. **Canada:** 11,658 jobs (4.8% market share) | Mean Rate: $36.40/hr | Mean Budget: $860

---

## 4. Regional Wage Benchmarks

| Geographical Region | Total Postings ($N$) | Mean Hourly Rate ($/hr) | Median Hourly Rate ($/hr) | Mean Fixed Budget ($) |
| :--- | :---: | :---: | :---: | :---: |
| **North America** | 112,450 | **$38.40** | $35.00 | $925 |
| **Western Europe** | 35,420 | **$35.60** | $30.00 | $860 |
| **Middle East & North Africa**| 8,910 | **$29.40** | $25.00 | $680 |
| **Southern & Eastern Europe**| 12,380 | **$27.80** | $25.00 | $620 |
| **Latin America** | 4,120 | **$24.20** | $20.00 | $510 |
| **Asia-Pacific** | 42,150 | **$21.90** | $18.00 | $490 |
| **Sub-Saharan Africa** | 3,840 | **$18.10** | $15.00 | $380 |

---

## 5. Visual Deliverables
- **Interactive Choropleth World Map:** Implemented via Plotly.js at web route `/task4`.
- **API Endpoint:** Data accessible via `GET /api/task4/geography`.
