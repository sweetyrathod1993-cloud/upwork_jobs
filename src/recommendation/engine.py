"""
Task 5: Personalized Job Recommendation Engine.
Features TF-IDF vectorization, cosine similarity ranking, multi-criteria filtering,
and match scoring for job seekers.
"""
from typing import Dict, Any, List, Optional
import re
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import config
from src.data.loader import load_jobs_data

class JobRecommendationEngine:
    def __init__(self, model_path=config.TFIDF_MODEL_PATH):
        self.model_path = model_path
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.jobs_corpus: Optional[pd.DataFrame] = None
        self.is_initialized = False

    def build_and_save_index(self, df: Optional[pd.DataFrame] = None, max_jobs: int = 50000):
        """
        Builds the TF-IDF index on the most recent/representative job postings
        and serializes it for instant recommendations.
        """
        if df is None:
            df = load_jobs_data()

        print("Building recommendation engine index...")
        # Use recent jobs
        working_df = df.copy()
        if "id" not in working_df.columns:
            working_df = working_df.reset_index().rename(columns={"index": "id"})
        sorted_df = working_df.sort_values(by="id", ascending=False).head(max_jobs).copy().reset_index(drop=True)
        
        # Combine title, category, and skills for rich semantic context
        corpus_text = (
            sorted_df["title_clean"].fillna("") + " " +
            sorted_df["category"].fillna("") + " " +
            sorted_df["skills_str"].fillna("")
        )

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=30000,
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus_text)

        metadata_cols = [
            "id", "title_clean", "link", "published_date", "is_hourly",
            "hourly_rate", "hourly_low", "hourly_high", "budget_clean",
            "country", "category", "seniority", "skills_str"
        ]
        self.jobs_corpus = sorted_df[metadata_cols].copy()

        # Save to disk
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "vectorizer": self.vectorizer,
            "tfidf_matrix": self.tfidf_matrix,
            "jobs_corpus": self.jobs_corpus
        }, self.model_path)
        
        self.is_initialized = True
        print(f"Recommendation index built with {len(self.jobs_corpus):,} jobs and saved to {self.model_path}")

    def load_index(self):
        """Loads the pre-computed TF-IDF index from disk."""
        if not self.model_path.exists():
            self.build_and_save_index()
            return

        print(f"Loading recommendation index from {self.model_path}...")
        data = joblib.load(self.model_path)
        self.vectorizer = data["vectorizer"]
        self.tfidf_matrix = data["tfidf_matrix"]
        self.jobs_corpus = data["jobs_corpus"]
        self.is_initialized = True

    def recommend(
        self,
        query: str,
        category: Optional[str] = None,
        country: Optional[str] = None,
        min_rate: Optional[float] = None,
        max_rate: Optional[float] = None,
        is_hourly: Optional[bool] = None,
        seniority: Optional[str] = None,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generates personalized job recommendations based on candidate profile/query
        and optional multi-faceted filters.
        """
        if not self.is_initialized or self.vectorizer is None:
            self.load_index()

        query_clean = query.strip() if query else ""
        if not query_clean and not category:
            query_clean = "software developer python react"

        # Transform candidate query
        query_vec = self.vectorizer.transform([query_clean])
        sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Candidate pool
        scores_series = pd.Series(sim_scores, index=self.jobs_corpus.index)
        
        # Apply filters
        filtered_indices = self.jobs_corpus.index

        if category and category != "All":
            cat_mask = self.jobs_corpus["category"] == category
            filtered_indices = filtered_indices.intersection(self.jobs_corpus[cat_mask].index)

        if country and country != "All":
            country_mask = self.jobs_corpus["country"] == country
            filtered_indices = filtered_indices.intersection(self.jobs_corpus[country_mask].index)

        if is_hourly is not None:
            hourly_mask = self.jobs_corpus["is_hourly"] == is_hourly
            filtered_indices = filtered_indices.intersection(self.jobs_corpus[hourly_mask].index)

        if seniority and seniority != "All":
            sen_mask = self.jobs_corpus["seniority"] == seniority
            filtered_indices = filtered_indices.intersection(self.jobs_corpus[sen_mask].index)

        if min_rate is not None:
            rate_mask = (self.jobs_corpus["hourly_rate"] >= min_rate) | (self.jobs_corpus["budget_clean"] >= min_rate)
            filtered_indices = filtered_indices.intersection(self.jobs_corpus[rate_mask].index)

        if max_rate is not None:
            rate_mask = (self.jobs_corpus["hourly_rate"] <= max_rate) | (self.jobs_corpus["budget_clean"] <= max_rate)
            filtered_indices = filtered_indices.intersection(self.jobs_corpus[rate_mask].index)

        if len(filtered_indices) == 0:
            # Fallback to unfiltered top matches if filtering was too aggressive
            filtered_indices = self.jobs_corpus.index

        # Rank filtered jobs by similarity
        sub_scores = scores_series.loc[filtered_indices]
        top_indices = sub_scores.sort_values(ascending=False).head(top_k).index

        query_tokens = set(re.findall(r"\w+", query_clean.lower()))

        results = []
        for idx in top_indices:
            row = self.jobs_corpus.loc[idx]
            sim = float(scores_series[idx])
            
            # Match score scaled to 0-100%
            match_score = min(100.0, round(sim * 100.0 * 1.5, 1))
            if match_score < 10.0 and len(query_tokens) > 0:
                match_score = round(max(sim * 100.0, 15.0), 1)

            # Detect matched keywords
            title_tokens = set(re.findall(r"\w+", row["title_clean"].lower()))
            matched_skills = list(query_tokens.intersection(title_tokens))

            # Format compensation display
            if row["is_hourly"]:
                rate_str = f"${row['hourly_rate']:.2f}/hr" if pd.notna(row['hourly_rate']) else "Hourly"
            else:
                rate_str = f"${row['budget_clean']:.0f} Fixed" if pd.notna(row['budget_clean']) else "Fixed Price"

            results.append({
                "id": int(row["id"]),
                "title": row["title_clean"],
                "category": row["category"],
                "country": row["country"],
                "is_hourly": bool(row["is_hourly"]),
                "compensation": rate_str,
                "hourly_rate": float(row["hourly_rate"]) if pd.notna(row["hourly_rate"]) else None,
                "budget": float(row["budget_clean"]) if pd.notna(row["budget_clean"]) else None,
                "seniority": row["seniority"],
                "skills": row["skills_str"],
                "matched_keywords": matched_skills,
                "match_score": match_score,
                "published_date": str(row["published_date"])[:10],
                "link": row["link"]
            })

        return results

# Singleton instance
_recommender: Optional[JobRecommendationEngine] = None

def get_recommender() -> JobRecommendationEngine:
    global _recommender
    if _recommender is None:
        _recommender = JobRecommendationEngine()
        _recommender.load_index()
    return _recommender

if __name__ == "__main__":
    engine = JobRecommendationEngine()
    engine.build_and_save_index()
    recs = engine.recommend("Python machine learning data scientist", top_k=3)
    print("=== Task 5 Recommendation Sample ===")
    for r in recs:
        print(f"Match: {r['match_score']}% | {r['title']} | {r['compensation']} | {r['country']}")
