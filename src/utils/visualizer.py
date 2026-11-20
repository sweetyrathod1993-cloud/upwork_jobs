"""
Visualization utilities for generating interactive Plotly charts and static figures.
Supports direct JSON exports for modern web frontends and HTML/PNG rendering.
"""
from typing import Dict, Any, List
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

import config

def create_task1_keyword_salary_chart(data: Dict[str, Any]) -> str:
    """Generates an interactive Plotly bar chart for top paying keywords."""
    top_kws = data["top_paying_keywords"]
    names = [k["keyword"] for k in top_kws][::-1]
    rates = [k["mean_hourly_rate"] for k in top_kws][::-1]
    medians = [k["median_hourly_rate"] for k in top_kws][::-1]
    counts = [k["job_count_hourly"] for k in top_kws][::-1]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=rates,
        y=names,
        orientation="h",
        name="Mean Rate ($/hr)",
        marker=dict(
            color=rates,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Rate ($)")
        ),
        text=[f"${r:.1f}/hr (Med: ${m:.0f})" for r, m in zip(rates, medians)],
        textposition="auto",
        customdata=counts,
        hovertemplate="<b>%{y}</b><br>Mean Rate: $%{x:.2f}/hr<br>Job Postings: %{customdata:,}<extra></extra>"
    ))

    fig.update_layout(
        title="Top Paying Skills & Keywords in Job Titles",
        xaxis_title="Average Hourly Rate ($/hr)",
        yaxis_title="Keyword / Skill",
        template="plotly_white",
        height=520,
        margin=dict(l=140, r=40, t=60, b=50)
    )
    return fig.to_json()

def create_task2_growth_bubble_chart(data: Dict[str, Any]) -> str:
    """Generates a growth rate vs volume bubble chart for emerging categories."""
    cats = data["category_growth_ranking"]
    names = [c["category"] for c in cats]
    growths = [c["growth_rate_pct"] for c in cats]
    volumes = [c["total_postings"] for c in cats]
    momentums = [c["momentum_score"] for c in cats]
    statuses = [c["status"] for c in cats]

    fig = go.Figure()
    
    # Color mapping by status
    color_map = {
        "High-Growth Emerging": "#10B981", # Emerald
        "Established Powerhouse": "#3B82F6", # Blue
        "Steady Growth": "#8B5CF6", # Purple
        "Maturing / Stable": "#64748B" # Gray
    }

    for status_type, color in color_map.items():
        sub_indices = [i for i, s in enumerate(statuses) if s == status_type]
        if sub_indices:
            fig.add_trace(go.Scatter(
                x=[growths[i] for i in sub_indices],
                y=[volumes[i] for i in sub_indices],
                text=[names[i] for i in sub_indices],
                mode="markers+text",
                name=status_type,
                textposition="top center",
                marker=dict(
                    size=[max(14, min(50, np_val)) for np_val in [momentums[i] / 5.0 for i in sub_indices]],
                    color=color,
                    opacity=0.85,
                    line=dict(width=1, color="#1e293b")
                ),
                hovertemplate="<b>%{text}</b><br>Growth: %{x:.1f}%<br>Total Jobs: %{y:,}<br>Status: " + status_type + "<extra></extra>"
            ))

    fig.update_layout(
        title="Job Categories: Growth Velocity vs Total Posting Volume",
        xaxis_title="Growth Rate (%)",
        yaxis_title="Total Job Postings (Log Scale)",
        yaxis_type="log",
        template="plotly_white",
        height=500,
        margin=dict(l=60, r=30, t=60, b=50)
    )
    return fig.to_json()

def create_task3_forecast_chart(forecast_data: Dict[str, Any]) -> str:
    """Renders historical actuals, test predictions, and 30-day forecast curves."""
    fig = go.Figure()

    hist_dates = forecast_data["history"]["dates"]
    hist_actuals = forecast_data["history"]["actuals"]
    
    test_dates = forecast_data["test_evaluation"]["dates"]
    test_preds = forecast_data["test_evaluation"]["predicted"]

    fut_dates = forecast_data["future_forecast"]["dates"]
    fut_preds = forecast_data["future_forecast"]["predicted_demand"]
    fut_lower = forecast_data["future_forecast"]["lower_95_ci"]
    fut_upper = forecast_data["future_forecast"]["upper_95_ci"]

    # Historical Actuals
    fig.add_trace(go.Scatter(
        x=hist_dates,
        y=hist_actuals,
        name="Historical Actual Demand",
        mode="lines+markers",
        line=dict(color="#2563EB", width=2),
        marker=dict(size=4)
    ))

    # Test Set Predictions
    fig.add_trace(go.Scatter(
        x=test_dates,
        y=test_preds,
        name="Validation Model Prediction",
        mode="lines",
        line=dict(color="#F59E0B", width=2, dash="dash")
    ))

    # Future Confidence Band (Upper & Lower)
    fig.add_trace(go.Scatter(
        x=fut_dates + fut_dates[::-1],
        y=fut_upper + fut_lower[::-1],
        fill="toself",
        fillcolor="rgba(16, 185, 129, 0.15)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=True,
        name="95% Confidence Band"
    ))

    # Future Point Forecast
    fig.add_trace(go.Scatter(
        x=fut_dates,
        y=fut_preds,
        name="30-Day Future Forecast",
        mode="lines+markers",
        line=dict(color="#10B981", width=3),
        marker=dict(size=5)
    ))

    metrics = forecast_data["metrics"]
    metrics_annotation = f"MAE: {metrics['MAE']} | RMSE: {metrics['RMSE']} | MAPE: {metrics['MAPE']}% | R²: {metrics['R2_Score']}"

    fig.update_layout(
        title=f"Demand Forecasting: {forecast_data['role_name']}<br><sup>{metrics_annotation}</sup>",
        xaxis_title="Date",
        yaxis_title="Daily Job Postings",
        template="plotly_white",
        height=500,
        hovermode="x unified",
        margin=dict(l=60, r=40, t=80, b=50)
    )
    return fig.to_json()

def create_task4_country_map(country_data: Dict[str, Any]) -> str:
    """Creates an interactive Plotly World Choropleth Map of average hourly rates."""
    choropleth_list = country_data["choropleth_data"]
    
    locations = [c["iso3"] for c in choropleth_list]
    hover_texts = [c["country"] for c in choropleth_list]
    rates = [c["mean_hourly_rate"] for c in choropleth_list]
    jobs = [c["total_jobs"] for c in choropleth_list]
    categories = [c["top_category"] for c in choropleth_list]

    fig = go.Figure(data=go.Choropleth(
        locations=locations,
        z=rates,
        text=hover_texts,
        colorscale="Viridis",
        autocolorscale=False,
        reversescale=False,
        marker_line_color="#475569",
        marker_line_width=0.6,
        colorbar_title="Hourly Rate ($/hr)",
        customdata=list(zip(jobs, categories)),
        hovertemplate="<b>%{text} (%{location})</b><br>Avg Rate: $%{z:.2f}/hr<br>Postings: %{customdata[0]:,}<br>Top Sector: %{customdata[1]}<extra></extra>"
    ))

    fig.update_layout(
        title="Global Freelance Hourly Rates by Country",
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth"
        ),
        template="plotly_white",
        height=540,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    return fig.to_json()

def create_task8_scenarios_chart(scenario_data: Dict[str, Any]) -> str:
    """Renders a multi-scenario projection line chart comparing future paths."""
    quarters = scenario_data["simulation_parameters"]["quarters"]
    scenarios = scenario_data["scenarios"]

    fig = go.Figure()

    colors = {
        "baseline": "#2563EB",
        "ai_disruption": "#10B981",
        "economic_outsourcing": "#F59E0B"
    }

    for key, sc in scenarios.items():
        fig.add_trace(go.Scatter(
            x=quarters,
            y=sc["total_volume"],
            name=sc["name"].split(":")[0],
            mode="lines+markers",
            line=dict(color=colors.get(key, "#6B7280"), width=3),
            marker=dict(size=6),
            hovertemplate="<b>" + sc["name"] + "</b><br>Quarter: %{x}<br>Projected Volume: %{y:,}<extra></extra>"
        ))

    fig.update_layout(
        title="Predictive Analytics: Future Market Trajectories (2024 - 2026)",
        xaxis_title="Quarter",
        yaxis_title="Projected Job Postings Volume",
        template="plotly_white",
        height=480,
        hovermode="x unified",
        margin=dict(l=60, r=40, t=60, b=50)
    )
    return fig.to_json()
