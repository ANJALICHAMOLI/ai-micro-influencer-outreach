import ast
import json
import os
import re
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

OUTPUT = Path("data/personalized_messages.csv")


def word_count(text):
    return len(re.findall(r"\b\S+\b", text.strip()))


def get_themes(row):
    themes = row.get("content_themes", [])

    if isinstance(themes, list):
        return themes[:2]

    if isinstance(themes, str):
        try:
            parsed = ast.literal_eval(themes)
            if isinstance(parsed, list):
                return parsed[:2]
        except (ValueError, SyntaxError):
            pass

        return [themes]

    return ["AI and technology"]


def safe_theme_text(row):
    themes = get_themes(row)
    cleaned = [str(theme).strip(" []'\"") for theme in themes if str(theme).strip()]

    if not cleaned:
        return "AI and technology"

    return ", ".join(cleaned[:2])


def fallback_personalization(row):
    themes = safe_theme_text(row)
    return f"Your channel focuses on {themes}, which is relevant to the creator collaborations we're exploring."


def generate_personalization_with_groq(row):
    key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not key:
        return fallback_personalization(row)

    client = Groq(api_key=key)

    facts = {
        "creator_name": row["name"],
        "platform": row["platform"],
        "follower_count": int(row["follower_count"]),
        "niche": row["niche"],
        "content_themes": get_themes(row),
    }

    system = (
        "Generate exactly one factual personalization sentence for creator outreach. "
        "Use ONLY the supplied facts. "
        "The sentence may mention the creator's name, platform, follower count, niche, "
        "or supplied content themes. "
        "Do not mention anything about EDXSO's products, services, mission, audience, "
        "resources, benefits, features, or capabilities. "
        "Do not claim the creator is leading, popular, influential, highly engaging, or successful. "
        "Do not claim that the sender enjoyed, liked, watched, reviewed, or followed the creator's content. "
        "Do not mention recent posts or achievements. "
        "Return JSON with exactly one field: personalization."
    )

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "personalization",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "personalization": {"type": "string"}
                    },
                    "required": ["personalization"],
                    "additionalProperties": False,
                },
            },
        },
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": json.dumps(facts, ensure_ascii=False),
            },
        ],
    )

    result = json.loads(response.choices[0].message.content)
    personalization = result["personalization"].strip()

    banned_phrases = [
        "i enjoyed",
        "i love",
        "i liked",
        "we enjoyed",
        "we love",
        "we liked",
        "leading",
        "top creator",
        "popular creator",
        "highly engaging",
        "your audience",
        "our mission",
        "our community",
        "our product",
        "our products",
        "our services",
        "our resources",
        "we specialize",
        "edxso specializes",
        "edxso provides",
        "edxso offers",
        "edxso empowers",
    ]

    lowered = personalization.lower()

    if any(phrase in lowered for phrase in banned_phrases):
        return fallback_personalization(row)

    return personalization


def build_message(row):
    name = str(row["name"]).strip()
    dm_name = name.split(" - ")[0].strip()

    if len(dm_name.split()) > 5:
        dm_name = " ".join(dm_name.split()[:5])
    brand = os.getenv("BRAND_NAME", "EDXSO")
    follower_count = int(row["follower_count"])

    personalization = generate_personalization_with_groq(row)

    email_body = (
        f"Hi {name},\n\n"
        f"I'm reaching out from {brand}. {personalization} "
        f"With {follower_count:,} subscribers, your channel is within the creator group "
        "we're exploring for potential collaborations. We'd love to see whether a "
        "collaboration could be relevant to your content. If you're open to hearing more, "
        "I can share the collaboration details, expected deliverables, and next steps. "
        "Thanks for your time, and I look forward to connecting.\n\n"
        f"Best,\n{brand}"
    )

    dm = (
        f"Hi {dm_name}! I came across your {safe_theme_text(row)} content and would love "
        f"to explore a potential {brand} collaboration. Interested in hearing more?"
    )

    return {
        "influencer_name": name,
        "email_subject": f"Potential {brand} Collaboration with {name}",
        "email_body": email_body,
        "instagram_dm": dm,
    }


def generate_message(row):
    try:
        message = build_message(row)

        email_words = word_count(message["email_body"])
        dm_words = word_count(message["instagram_dm"])

        if 60 <= email_words <= 90 and 15 <= dm_words <= 30:
            return {
                **message,
                "email_word_count": email_words,
                "dm_word_count": dm_words,
            }

    except Exception:
        pass

    brand = os.getenv("BRAND_NAME", "EDXSO")
    name = str(row["name"]).strip()
    themes = safe_theme_text(row)
    follower_count = int(row["follower_count"])

    email_body = (
        f"Hi {name},\n\n"
        f"I'm reaching out from {brand}. Your channel focuses on {themes}, "
        f"and you currently have {follower_count:,} subscribers. We're exploring "
        "potential creator collaborations and would be interested in discussing "
        "whether there could be a fit with your content. If you're open to hearing "
        "more, I can share the collaboration details, expected deliverables, and "
        "next steps. Thanks for your time, and I look forward to connecting.\n\n"
        f"Best,\n{brand}"
    )

    dm_name = name.split(" - ")[0].strip()

    if len(dm_name.split()) > 5:
        dm_name = " ".join(dm_name.split()[:4])

    dm = (
        f"Hi {dm_name}! I came across your {themes} content and would love to explore "
        f"a potential {brand} collaboration. Interested in hearing more?"
    )

    return {
        "influencer_name": name,
        "email_subject": f"Potential {brand} Collaboration with {name}",
        "email_body": email_body,
        "instagram_dm": dm,
        "email_word_count": word_count(email_body),
        "dm_word_count": word_count(dm),
    }


def generate_for_dataframe(df):
    rows = []

    for _, row in df.iterrows():
        rows.append(generate_message(row))

    result = pd.DataFrame(rows)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)

    return result