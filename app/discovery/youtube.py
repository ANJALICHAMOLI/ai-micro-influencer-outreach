import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

QUERIES = [
    "AI tools",
    "generative AI",
    "machine learning",
    "large language models",
    "LLM",
    "AI agents",
    "LangChain",
    "AI development",
    "machine learning projects",
    "artificial intelligence",
    "Python AI",
    "developer AI",
]

OUTPUT = Path("data/influencers_raw.csv")


def _youtube_client():
    key = os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is missing from .env")
    return build("youtube", "v3", developerKey=key)


def discover_channels(target_count=60):
    youtube = _youtube_client()
    min_subs = int(os.getenv("MIN_SUBSCRIBERS", "5000"))
    max_subs = int(os.getenv("MAX_SUBSCRIBERS", "100000"))
    found = {}
    max_pages_per_query = 2

    for query in QUERIES:
        token = None
        for _ in range(max_pages_per_query):
            response = youtube.search().list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=50,
                pageToken=token,
            ).execute()

            ids = [
                item["snippet"]["channelId"]
                for item in response.get("items", [])
                if item.get("snippet", {}).get("channelId")
            ]

            for start in range(0, len(ids), 50):
                batch = ids[start:start + 50]
                if not batch:
                    continue
                channel_response = youtube.channels().list(
                    part="snippet,statistics",
                    id=",".join(batch),
                    maxResults=50,
                ).execute()

                for channel in channel_response.get("items", []):
                    statistics = channel.get("statistics", {})
                    snippet = channel.get("snippet", {})
                    if statistics.get("hiddenSubscriberCount"):
                        continue
                    try:
                        subscribers = int(statistics.get("subscriberCount", 0))
                    except (TypeError, ValueError):
                        continue
                    if not min_subs <= subscribers <= max_subs:
                        continue
                    channel_id = channel["id"]
                    found[channel_id] = {
                        "name": snippet.get("title", ""),
                        "platform": "YouTube",
                        "profile_url": f"https://www.youtube.com/channel/{channel_id}",
                        "follower_count": subscribers,
                        "engagement_rate": "Not Available",
                        "niche": "AI / Technology",
                        "content_themes": [],
                        "contact_email": "Not Found",
                        "qualification_status": "Pending",
                        "qualification_reason": "",
                        "source_query": query,
                        "description": snippet.get("description", ""),
                    }
                    if len(found) >= target_count:
                        break
                if len(found) >= target_count:
                    break

            if len(found) >= target_count:
                break
            token = response.get("nextPageToken")
            if not token:
                break
        if len(found) >= target_count:
            break

    df = pd.DataFrame(found.values())
    if df.empty:
        raise RuntimeError("No channels were discovered. Check the API key, quota, and search terms.")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    return df
