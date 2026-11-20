"""
Main Flask Web Application and REST API service for
Job Market Analysis and Recommendation System.
"""
import json
import logging
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash

import config
from src.data.loader import query_jobs, load_jobs_data
from src.recommendation.engine import get_recommender
from src.analysis.task6_monthly_dynamics import update_monthly_dynamics
from src.analysis.task8_future_scenarios import simulate_future_market_scenarios
from src.utils.visualizer import (
    create_task1_keyword_salary_chart,
    create_task2_growth_bubble_chart,
    create_task3_forecast_chart,
    create_task4_country_map,
    create_task8_scenarios_chart
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Cache metrics in memory
_METRICS_DATA: Optional[Dict[str, Any]] = None

def get_metrics() -> Dict[str, Any]:
    """Loads precomputed metrics from cache or computes them if not present."""
    global _METRICS_DATA
    if _METRICS_DATA is not None:
        return _METRICS_DATA

    if config.METRICS_CACHE_PATH.exists():
        with open(config.METRICS_CACHE_PATH, "r", encoding="utf-8") as f:
            _METRICS_DATA = json.load(f)
            return _METRICS_DATA

    from run_pipeline import run_full_pipeline
    run_full_pipeline()
    with open(config.METRICS_CACHE_PATH, "r", encoding="utf-8") as f:
        _METRICS_DATA = json.load(f)
    return _METRICS_DATA

# -------------------------------------------------------------
# HTML Template Views
# -------------------------------------------------------------

@app.route("/")
def index():
    metrics = get_metrics()
    chart_json = create_task1_keyword_salary_chart(metrics["task1"])
    return render_template("index.html", metrics=metrics, chart_json=chart_json)

@app.route("/task1")
def task1_salaries():
    metrics = get_metrics()
    chart_json = create_task1_keyword_salary_chart(metrics["task1"])
    return render_template("task1_salaries.html", t1=metrics["task1"], chart_json=chart_json)

@app.route("/task2")
def task2_emerging():
    metrics = get_metrics()
    chart_json = create_task2_growth_bubble_chart(metrics["task2"])
    return render_template("task2_emerging.html", t2=metrics["task2"], chart_json=chart_json)

@app.route("/task3")
def task3_forecast():
    metrics = get_metrics()
    forecasts = metrics["task3"]["forecasts"]
    forecasts_json = json.dumps(forecasts)
    return render_template("task3_forecast.html", t3=metrics["task3"], forecasts_json=forecasts_json)

@app.route("/task4")
def task4_geography():
    metrics = get_metrics()
    chart_json = create_task4_country_map(metrics["task4"])
    return render_template("task4_geography.html", t4=metrics["task4"], chart_json=chart_json)

@app.route("/recommend")
def task5_recommend():
    metrics = get_metrics()
    categories = sorted(list(config.CATEGORIES_TAXONOMY.keys()))
    top_countries = [c["country"] for c in metrics["task4"]["top_volume_countries"][:25]]
    return render_template("task5_recommend.html", categories=categories, countries=top_countries)

@app.route("/task6")
def task6_monthly():
    metrics = get_metrics()
    return render_template("task6_monthly.html", t6=metrics["task6"])

@app.route("/task7")
def task7_remote():
    metrics = get_metrics()
    return render_template("task7_remote.html", t7=metrics["task7"])

@app.route("/task8")
def task8_future():
    metrics = get_metrics()
    chart_json = create_task8_scenarios_chart(metrics["task8"])
    return render_template("task8_future.html", t8=metrics["task8"], chart_json=chart_json)

@app.route("/api/docs")
def api_docs():
    return render_template("api_docs.html")

# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint for Docker container and orchestrator probes."""
    return jsonify({
        "status": "healthy",
        "service": "WorkPulse Labor Analytics",
        "version": "1.0.0",
        "total_jobs_indexed": 244827
    }), 200

@app.route("/api/stats/summary", methods=["GET"])
def api_summary():
    metrics = get_metrics()
    return jsonify({
        "total_postings": metrics["total_jobs"],
        "mean_hourly_rate": metrics["task1"]["overall_metrics"]["overall_mean_hourly"],
        "median_hourly_rate": metrics["task1"]["overall_metrics"]["overall_median_hourly"],
        "total_countries": metrics["task4"]["global_benchmarks"]["total_countries"],
        "top_categories_count": len(metrics["task2"]["category_growth_ranking"])
    })

@app.route("/api/task1/salaries", methods=["GET"])
def api_task1():
    metrics = get_metrics()
    return jsonify(metrics["task1"])

@app.route("/api/task2/categories", methods=["GET"])
def api_task2():
    metrics = get_metrics()
    return jsonify(metrics["task2"])

@app.route("/api/task3/forecasts", methods=["GET"])
def api_task3():
    metrics = get_metrics()
    return jsonify(metrics["task3"])

@app.route("/api/task4/geography", methods=["GET"])
def api_task4():
    metrics = get_metrics()
    return jsonify(metrics["task4"])

@app.route("/api/task6/monthly", methods=["GET"])
def api_task6():
    metrics = get_metrics()
    return jsonify(metrics["task6"])

@app.route("/api/monthly/update", methods=["POST"])
def api_monthly_update():
    """Dynamic monthly ingestion handler for Task 6."""
    global _METRICS_DATA
    logger.info("Executing dynamic monthly update pipeline...")
    updated_t6 = update_monthly_dynamics()
    
    if _METRICS_DATA is not None:
        _METRICS_DATA["task6"] = updated_t6
        with open(config.METRICS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(_METRICS_DATA, f, indent=2)

    return jsonify({
        "status": "success",
        "message": "Monthly job market dynamics recalculated successfully.",
        "latest_month": updated_t6.get("latest_month", {})
    })

@app.route("/api/task7/remote", methods=["GET"])
def api_task7():
    metrics = get_metrics()
    return jsonify(metrics["task7"])

@app.route("/api/task8/scenarios", methods=["GET"])
def api_task8():
    ai_factor = float(request.args.get("ai_factor", 1.0))
    outsourcing_factor = float(request.args.get("outsourcing_factor", 1.0))
    scenarios_data = simulate_future_market_scenarios(
        custom_ai_factor=ai_factor,
        custom_outsourcing_factor=outsourcing_factor
    )
    return jsonify(scenarios_data)

@app.route("/api/recommend", methods=["POST", "GET"])
def api_recommend():
    """
    Personalized Recommendation Engine (Task 5).
    Accepts JSON body or query parameters and returns ranked job matches.
    """
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
    else:
        data = request.args

    query = data.get("query", "Software Developer")
    category = data.get("category", "All")
    country = data.get("country", "All")
    seniority = data.get("seniority", "All")
    min_rate = data.get("min_rate")
    max_rate = data.get("max_rate")
    is_hourly = data.get("is_hourly")
    top_k = int(data.get("top_k", 10))

    if min_rate is not None:
        try:
            min_rate = float(min_rate)
        except (ValueError, TypeError):
            min_rate = None

    if max_rate is not None:
        try:
            max_rate = float(max_rate)
        except (ValueError, TypeError):
            max_rate = None

    recommender = get_recommender()
    recommendations = recommender.recommend(
        query=query,
        category=category,
        country=country,
        min_rate=min_rate,
        max_rate=max_rate,
        is_hourly=is_hourly,
        seniority=seniority,
        top_k=top_k
    )

    return jsonify({
        "status": "success",
        "query_echo": query,
        "filters_applied": {
            "category": category,
            "country": country,
            "seniority": seniority,
            "is_hourly": is_hourly,
            "min_rate": min_rate,
            "max_rate": max_rate
        },
        "count": len(recommendations),
        "recommendations": recommendations
    })

@app.route("/api/jobs", methods=["GET"])
def api_jobs():
    """SQL search and pagination across SQLite database."""
    keyword = request.args.get("keyword")
    category = request.args.get("category")
    country = request.args.get("country")
    min_rate = request.args.get("min_rate", type=float)
    max_rate = request.args.get("max_rate", type=float)
    is_hourly_param = request.args.get("is_hourly")
    
    is_hourly = None
    if is_hourly_param is not None:
        is_hourly = is_hourly_param.lower() in ("true", "1")

    limit = min(request.args.get("limit", default=25, type=int), 100)
    offset = request.args.get("offset", default=0, type=int)

    results = query_jobs(
        keyword=keyword,
        category=category,
        country=country,
        min_rate=min_rate,
        max_rate=max_rate,
        is_hourly=is_hourly,
        limit=limit,
        offset=offset
    )
    return jsonify(results)

if __name__ == "__main__":
    logger.info(f"Starting WorkPulse server on {config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.DEBUG)
