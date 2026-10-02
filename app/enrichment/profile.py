import re
from pathlib import Path

import pandas as pd

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_PATTERN = re.compile(r"https?://[^\s<>\"]+")

THEMES = {
    "Generative AI": ["generative ai", "genai", "chatgpt", "gemini", "claude"],
    "LLMs": ["llm", "large language model", "language model"],
    "Machine Learning": ["machine learning", "deep learning", "neural network"],
    "AI Agents": ["ai agent", "ai agents", "agentic ai", "agents"],
    "Developer Tools": ["python", "developer", "coding", "software", "programming"],
    "RAG": ["rag", "retrieval augmented generation"],
    "Data Science": ["data science", "data analytics", "data scientist"],
}

OUTPUT = Path("data/influencers_enriched.csv")


def extract_email(text):
    match = EMAIL_PATTERN.search(text or "")
    return match.group(0) if match else "Not Found"


def extract_urls(text):
    return URL_PATTERN.findall(text or "")


def infer_themes(text):
    lowered = (text or "").lower()
    themes = [theme for theme, terms in THEMES.items() if any(term in lowered for term in terms)]
    return themes[:5] or ["AI / Technology"]


def enrich_dataframe(df):
    result = df.copy()
    result["contact_email"] = result["description"].apply(extract_email)
    result["content_themes"] = result["description"].apply(infer_themes)
    result["engagement_rate"] = result["engagement_rate"].fillna("Not Available")
    result["engagement_rate"] = result["engagement_rate"].replace("", "Not Available")
    result["public_website"] = result["description"].apply(
        lambda value: extract_urls(value)[0] if extract_urls(value) else "Not Found"
    )
    result = result.drop(columns=["description"], errors="ignore")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    return result
