"""
Data Preprocessing and Feature Engineering module.
Loads, cleans, categorizes, and prepares job posting data for analysis and modeling.
"""
import re
import html
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List, Dict

import config

def clean_text(text: str) -> str:
    """Decodes HTML entities and normalizes whitespace."""
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def classify_category(title: str, taxonomy: Dict[str, List[str]] = config.CATEGORIES_TAXONOMY) -> str:
    """Assigns the best matching category based on title keyword patterns."""
    if not isinstance(title, str):
        return "Other / General"
    t_lower = title.lower()
    for cat, patterns in taxonomy.items():
        for pat in patterns:
            if re.search(pat, t_lower):
                return cat
    return "Other / General"

def extract_seniority(title: str) -> str:
    """Extracts seniority level from job title."""
    if not isinstance(title, str):
        return "Not Specified"
    t_lower = title.lower()
    for level, patterns in config.SENIORITY_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, t_lower):
                return level
    return "Mid / Standard"

def extract_skills(title: str, skill_list: List[str] = config.KEY_TECH_SKILLS) -> List[str]:
    """Identifies mentioned skills in the job title."""
    if not isinstance(title, str):
        return []
    t_lower = title.lower()
    found = []
    for skill in skill_list:
        # Match word boundary
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, t_lower):
            found.append(skill)
    return found

def clean_hourly_rate(row: pd.Series) -> Optional[float]:
    """Computes a realistic average hourly rate from hourly_low and hourly_high."""
    if not row.get("is_hourly", False):
        return np.nan
    low = row.get("hourly_low")
    high = row.get("hourly_high")
    
    val = np.nan
    if pd.notna(low) and pd.notna(high):
        val = (low + high) / 2.0
    elif pd.notna(low):
        val = low
    elif pd.notna(high):
        val = high
        
    # Filter extreme outliers ($3 to $250/hr is standard Upwork range)
    if pd.notna(val) and 3.0 <= val <= 350.0:
        return round(val, 2)
    return np.nan

def clean_budget(budget: float) -> Optional[float]:
    """Cleans fixed price budget removing extreme noise."""
    if pd.isna(budget):
        return np.nan
    if 5.0 <= budget <= 100000.0:
        return round(budget, 2)
    return np.nan

def preprocess_dataset(
    input_csv: Path = config.RAW_DATA_PATH,
    output_parquet: Path = config.PROCESSED_PARQUET_PATH,
    output_db: Path = config.DATABASE_PATH,
    sample_size: Optional[int] = None
) -> pd.DataFrame:
    """
    Full preprocessing pipeline:
    1. Loads raw CSV data.
    2. Cleans titles and links.
    3. Normalizes datetime and creates time-series features.
    4. Calculates realistic hourly rates and cleaned budgets.
    5. Categorizes jobs and assigns seniority.
    6. Extracts key skills.
    7. Saves to Parquet and SQLite for maximum performance.
    """
    print(f"Loading raw dataset from {input_csv}...")
    df = pd.read_csv(input_csv, nrows=sample_size)
    print(f"Loaded {len(df):,} records. Cleaning and enriching...")

    # Drop records with null titles
    df = df.dropna(subset=["title"]).copy()
    
    # Clean text
    df["title_clean"] = df["title"].apply(clean_text)
    
    # Parse timestamps
    df["published_date"] = pd.to_datetime(df["published_date"], errors="coerce")
    df = df.dropna(subset=["published_date"]).copy()
    
    df["date"] = df["published_date"].dt.date
    df["year"] = df["published_date"].dt.year
    df["month"] = df["published_date"].dt.month
    df["year_month"] = df["published_date"].dt.strftime("%Y-%m")
    df["day_of_week"] = df["published_date"].dt.day_name()
    df["is_weekend"] = df["published_date"].dt.dayofweek.isin([5, 6])
    
    # Hourly rates & budgets
    df["hourly_rate"] = df.apply(clean_hourly_rate, axis=1)
    df["budget_clean"] = df["budget"].apply(clean_budget)
    
    # Country cleaning
    df["country"] = df["country"].fillna("Unknown").str.strip()
    
    # Categorization
    print("Classifying job categories and seniorities...")
    df["category"] = df["title_clean"].apply(classify_category)
    df["seniority"] = df["title_clean"].apply(extract_seniority)
    
    # Skills extraction
    df["skills_matched"] = df["title_clean"].apply(extract_skills)
    df["skills_str"] = df["skills_matched"].apply(lambda s: ", ".join(s) if s else "")

    # Save to Parquet
    print(f"Saving preprocessed data to {output_parquet}...")
    output_parquet.parent.mkdir(parents=True, exist_ok=True)
    # Save selected columns to parquet
    columns_to_save = [
        "title", "title_clean", "link", "published_date", "date", "year_month",
        "day_of_week", "is_hourly", "hourly_low", "hourly_high", "hourly_rate",
        "budget", "budget_clean", "country", "category", "seniority", "skills_str"
    ]
    # Convert date to string for parquet serialization compatibility
    df_save = df[columns_to_save].copy()
    df_save["date"] = df_save["date"].astype(str)
    df_save.to_parquet(output_parquet, index=False, engine="pyarrow")
    
    # Save to SQLite database for fast web queries
    print(f"Syncing to SQLite database at {output_db}...")
    output_db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(output_db)
    
    # We save a lightweight indexed table
    df_save.to_sql("jobs", conn, if_exists="replace", index=True, index_label="id")
    
    # Create indexes for fast filtering
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON jobs (category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_country ON jobs (country);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_hourly ON jobs (is_hourly);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON jobs (date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_month ON jobs (year_month);")
    conn.commit()
    conn.close()
    
    print(f"Preprocessing complete! {len(df):,} jobs processed and indexed.")
    return df

if __name__ == "__main__":
    preprocess_dataset()
