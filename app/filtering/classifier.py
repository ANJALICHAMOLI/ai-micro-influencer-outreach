from pathlib import Path

import pandas as pd

KEYWORDS = [
    "ai",
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "llm",
    "large language model",
    "generative ai",
    "langchain",
    "rag",
    "retrieval augmented generation",
    "ai agent",
    "ai agents",
    "data science",
    "python",
    "developer",
    "software development",
]

OUTPUT = Path("data/influencers_filtered.csv")


def classify_dataframe(df):
    result = df.copy()
    statuses = []
    reasons = []

    for _, row in result.iterrows():
        text = f"{row.get('name', '')} {row.get('description', '')}".lower()
        matches = [keyword for keyword in KEYWORDS if keyword in text]
        within_range = 5000 <= int(row.get("follower_count", 0)) <= 100000

        if matches and within_range:
            statuses.append("Qualified")
            reasons.append(
                "Matched AI/technology relevance signals in the public channel profile: "
                + ", ".join(matches[:5])
            )
        else:
            statuses.append("Rejected")
            if not within_range:
                reasons.append("Outside the 5K-100K follower range")
            else:
                reasons.append(
                    "No strong AI/technology relevance signal found in the public channel profile"
                )

    result["qualification_status"] = statuses
    result["qualification_reason"] = reasons

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    return result