import os
import sys

import pandas as pd
from dotenv import load_dotenv

from app.database.db import initialize_database, upsert_influencer
from app.discovery.youtube import discover_channels
from app.enrichment.profile import enrich_dataframe
from app.filtering.classifier import classify_dataframe
from app.personalization.generator import generate_for_dataframe

load_dotenv()


def main():
    initialize_database()

    reuse_data = "--reuse-data" in sys.argv

    if reuse_data:
        enriched_path = "data/influencers_enriched.csv"

        if not os.path.exists(enriched_path):
            raise FileNotFoundError(
                f"{enriched_path} was not found. Run the full pipeline first."
            )

        enriched = pd.read_csv(enriched_path)

        if enriched.empty:
            raise RuntimeError("The existing enriched dataset is empty.")

        if "content_themes" in enriched.columns:
            enriched["content_themes"] = enriched["content_themes"].apply(
                lambda x: x.split(", ") if isinstance(x, str) and x else []
            )

        messages = generate_for_dataframe(enriched)

        for _, row in enriched.iterrows():
            upsert_influencer(row)

        print(f"Reused existing influencers: {len(enriched)}")
        print(f"Messages generated: {len(messages)}")
        print("YouTube discovery was skipped.")
        print("Sending was not triggered. Review messages in the Streamlit app.")

        return

    target = int(os.getenv("TARGET_INFLUENCERS", "60"))

    raw = discover_channels(target)
    filtered = classify_dataframe(raw)
    qualified = filtered[
        filtered["qualification_status"] == "Qualified"
    ].copy()
    enriched = enrich_dataframe(qualified)

    if enriched.empty:
        raise RuntimeError("No qualified influencers were available after filtering.")

    messages = generate_for_dataframe(enriched)

    for _, row in enriched.iterrows():
        upsert_influencer(row)

    print(f"Discovered: {len(raw)}")
    print(f"Qualified: {len(enriched)}")
    print(f"Messages generated: {len(messages)}")
    print("Sending was not triggered. Review messages in the Streamlit app.")


if __name__ == "__main__":
    main()