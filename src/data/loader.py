"""
Data loader module with caching and SQL query capabilities.
"""
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

import config
from src.data.preprocessor import preprocess_dataset

_CACHED_DF: Optional[pd.DataFrame] = None

def get_connection(db_path: Path = config.DATABASE_PATH) -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    if not db_path.exists():
        load_jobs_data()
    return sqlite3.connect(db_path)

def load_jobs_data(force_reload: bool = False) -> pd.DataFrame:
    """Loads the preprocessed jobs dataframe from Parquet (or creates it if missing)."""
    global _CACHED_DF
    if _CACHED_DF is not None and not force_reload:
        return _CACHED_DF

    if config.PROCESSED_PARQUET_PATH.exists() and not force_reload:
        df = pd.read_parquet(config.PROCESSED_PARQUET_PATH)
    else:
        df = preprocess_dataset()

    _CACHED_DF = df
    return _CACHED_DF

def query_jobs(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    country: Optional[str] = None,
    min_rate: Optional[float] = None,
    max_rate: Optional[float] = None,
    is_hourly: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """Queries jobs from SQLite with dynamic filtering and pagination."""
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if keyword:
        conditions.append("(title_clean LIKE ? OR skills_str LIKE ?)")
        search_term = f"%{keyword}%"
        params.extend([search_term, search_term])

    if category and category != "All":
        conditions.append("category = ?")
        params.append(category)

    if country and country != "All":
        conditions.append("country = ?")
        params.append(country)

    if is_hourly is not None:
        conditions.append("is_hourly = ?")
        params.append(1 if is_hourly else 0)

    if min_rate is not None:
        conditions.append("(hourly_rate >= ? OR budget_clean >= ?)")
        params.extend([min_rate, min_rate])

    if max_rate is not None:
        conditions.append("(hourly_rate <= ? OR budget_clean <= ?)")
        params.extend([max_rate, max_rate])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # Count query
    count_sql = f"SELECT COUNT(*) FROM jobs {where_clause}"
    cursor.execute(count_sql, params)
    total_count = cursor.fetchone()[0]

    # Data query
    data_sql = f"""
        SELECT id, title_clean, link, published_date, is_hourly, 
               hourly_rate, hourly_low, hourly_high, budget_clean, country, category, seniority, skills_str
        FROM jobs {where_clause}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """
    cursor.execute(data_sql, params + [limit, offset])
    rows = cursor.fetchall()

    columns = [
        "id", "title", "link", "published_date", "is_hourly",
        "hourly_rate", "hourly_low", "hourly_high", "budget", "country", "category", "seniority", "skills"
    ]
    results = [dict(zip(columns, r)) for r in rows]
    conn.close()

    return {
        "total": total_count,
        "limit": limit,
        "offset": offset,
        "jobs": results
    }
