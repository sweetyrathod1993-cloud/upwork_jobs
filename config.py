"""
Configuration settings for Job Market Analysis and Recommendation System.
"""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models" / "saved"
REPORTS_DIR = BASE_DIR / "reports"
STATIC_CHARTS_DIR = BASE_DIR / "static" / "charts"

# Ensure directories exist
for directory in [DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR, STATIC_CHARTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Dataset file paths
RAW_DATA_PATH = BASE_DIR / "all_upwork_jobs.csv"
PROCESSED_PARQUET_PATH = PROCESSED_DATA_DIR / "upwork_jobs_cleaned.parquet"
DATABASE_PATH = DATA_DIR / "upwork_jobs.db"
TFIDF_MODEL_PATH = MODELS_DIR / "tfidf_recommender.joblib"
FORECAST_MODELS_PATH = MODELS_DIR / "demand_forecasts.joblib"
METRICS_CACHE_PATH = PROCESSED_DATA_DIR / "analysis_metrics.json"

# Job Categorization Taxonomy
CATEGORIES_TAXONOMY = {
    "AI & Machine Learning": [
        r"\bai\b", r"machine learning", r"deep learning", r"\bllm\b", r"gpt", 
        r"computer vision", r"\bnlp\b", r"openai", r"generative ai", r"stable diffusion", 
        r"langchain", r"chatbot", r"prompt engineer", r"hugging face", r"anthropic",
        r"gemini", r"neural network", r"rag\b", r"vector database"
    ],
    "Data Science & Analytics": [
        r"data science", r"data analyst", r"data analytics", r"power bi", r"tableau", 
        r"data engineer", r"\betl\b", r"bigquery", r"snowflake", r"databricks", 
        r"looker", r"business intelligence", r"data mining", r"sql analyst", r"dbt\b"
    ],
    "Software & Web Development": [
        r"full stack", r"frontend", r"backend", r"software engineer", r"web developer", 
        r"\bpython\b", r"react", r"vue", r"angular", r"node\.js", r"next\.js", 
        r"django", r"flask", r"fastapi", r"java\b", r"c\#", r"c\+\+", r"\.net", 
        r"php", r"laravel", r"wordpress", r"javascript", r"typescript", r"ruby", 
        r"\bapi\b", r"\bgolang\b", r"\brust\b", r"graphql"
    ],
    "Mobile App Development": [
        r"flutter", r"react native", r"ios", r"android", r"swift", r"kotlin", 
        r"mobile app", r"app development", r"swiftui", r"xamarin"
    ],
    "Cloud, DevOps & Security": [
        r"\baws\b", r"azure", r"\bgcp\b", r"devops", r"docker", r"kubernetes", 
        r"ci/cd", r"cybersecurity", r"infosec", r"sysadmin", r"cloud architect", 
        r"linux admin", r"penetration test", r"terraform", r"soc 2", r"ansible"
    ],
    "UI/UX & Creative Design": [
        r"ui/ux", r"figma", r"graphic design", r"logo design", r"product design", 
        r"user interface", r"user experience", r"illustrator", r"photoshop", 
        r"canva", r"3d model", r"blender", r"cad\b", r"banner", r"wireframe", r"prototyping"
    ],
    "Video Production & Animation": [
        r"video edit", r"video editing", r"video editor", r"youtube", r"premiere pro", 
        r"after effects", r"motion graphic", r"animation", r"reels", r"tiktok", 
        r"davinci", r"shorts", r"capcut", r"video producer"
    ],
    "Digital Marketing & SEO": [
        r"\bseo\b", r"digital marketing", r"google ads", r"facebook ads", r"meta ads", 
        r"media buyer", r"social media", r"\bsmm\b", r"\bppc\b", r"email marketing", 
        r"klaviyo", r"marketing strategy", r"sem\b", r"influencer marketing"
    ],
    "Sales & Lead Generation": [
        r"lead gen", r"b2b sales", r"cold call", r"cold email", r"appointment set", 
        r"telemarketing", r"business development", r"outreach", r"sales rep", 
        r"closer", r"crm", r"hubspot"
    ],
    "Content & Copywriting": [
        r"content writer", r"copywriter", r"blog", r"article", r"ghostwriter", 
        r"copywriting", r"proofread", r"script", r"technical writer", r"creative writing"
    ],
    "Virtual Assistance & Support": [
        r"virtual assistant", r"\bva\b", r"data entry", r"customer support", 
        r"admin assistant", r"customer service", r"executive assistant", r"zendesk", 
        r"live chat", r"technical support"
    ],
    "E-Commerce Operations": [
        r"shopify", r"amazon", r"dropshipping", r"woocommerce", r"product listing", 
        r"etsy", r"ebay", r"e-commerce", r"ecommerce", r"walmart"
    ],
    "Translation & Audio": [
        r"translat", r"voice over", r"voice actor", r"audio edit", r"podcast", 
        r"transcription", r"voiceover", r"audio engineer"
    ],
    "Finance, Legal & Accounting": [
        r"bookkeep", r"quickbooks", r"accountan", r"financial model", r"\bcfo\b", 
        r"\btax\b", r"legal", r"contract", r"paralegal", r"compliance"
    ],
    "Blockchain & Web3": [
        r"blockchain", r"web3", r"smart contract", r"solidity", r"crypto", 
        r"\bnft\b", r"ethereum", r"dapp", r"solana"
    ]
}

# Seniority Levels
SENIORITY_PATTERNS = {
    "Lead / Principal / Architect": [r"\blead\b", r"\bprincipal\b", r"\barchitect\b", r"\bdirector\b", r"\bhead of\b", r"\bvp\b", r"\bchief\b"],
    "Senior": [r"\bsenior\b", r"\bsr\.\b", r"\bsr\b", r"experienced", r"advanced"],
    "Intermediate / Mid": [r"\bmid\b", r"intermediate", r"mid-level", r"specialist"],
    "Junior / Entry": [r"\bjunior\b", r"\bjr\.\b", r"\bjr\b", r"entry level", r"beginner", r"intern", r"novice"]
}

# Key Tech Skills for Salary & Correlation Tracking
KEY_TECH_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Node.js", "Django", "Vue", "Angular",
    "Next.js", "PHP", "WordPress", "Laravel", "AWS", "Azure", "GCP", "Docker", "Kubernetes",
    "Machine Learning", "AI", "LLM", "Data Science", "SQL", "Power BI", "Tableau",
    "Flutter", "React Native", "iOS", "Android", "Swift", "Kotlin", "Solidity", "Blockchain",
    "Shopify", "SEO", "Google Ads", "Figma", "UI/UX", "Video Editing", "Content Writing"
]

# Flask App Configuration
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
SECRET_KEY = os.environ.get("SECRET_KEY", "job-market-analysis-super-secret-key-2024")
