import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.database.db import (
    get_outreach_rows,
    initialize_database,
    outreach_already_sent,
    record_outreach,
    save_message,
)

load_dotenv()
initialize_database()

st.set_page_config(page_title="EDXSO Influencer Outreach", layout="wide")
st.title("EDXSO Micro Influencer Outreach")
st.caption("Discovery, qualification, enrichment, personalization, review, and simulated outreach")

raw_path = Path("data/influencers_raw.csv")
enriched_path = Path("data/influencers_enriched.csv")
messages_path = Path("data/personalized_messages.csv")

if not raw_path.exists() or not enriched_path.exists() or not messages_path.exists():
    st.warning("Run `python run_pipeline.py` before opening the dashboard.")
    st.stop()

raw = pd.read_csv(raw_path)
enriched = pd.read_csv(enriched_path)
messages = pd.read_csv(messages_path)

col1, col2, col3 = st.columns(3)
col1.metric("Discovered", len(raw))
col2.metric("Qualified", len(enriched))
col3.metric("Messages", len(messages))

st.subheader("Qualified Influencers")
display_cols = [
    "name",
    "platform",
    "follower_count",
    "engagement_rate",
    "niche",
    "content_themes",
    "contact_email",
    "profile_url",
    "qualification_reason",
]
st.dataframe(enriched[display_cols], use_container_width=True)

st.subheader("Message Review")
selected = st.selectbox("Select creator", enriched["name"].tolist())
row = enriched[enriched["name"] == selected].iloc[0]
message = messages[messages["influencer_name"] == selected].iloc[0]

st.write(f"**Profile:** {row['profile_url']}")
st.write(f"**Email:** {row['contact_email']}")
st.write(f"**Themes:** {row['content_themes']}")
st.write(f"**Qualification:** {row['qualification_reason']}")
st.text_area("Email subject", message["email_subject"], height=70)
st.text_area("Email body", message["email_body"], height=220)
st.text_area("Instagram DM", message["instagram_dm"], height=130)

if st.button("Simulate Email Send"):
    if row["contact_email"] == "Not Found":
        st.error("No public email was found for this creator.")
    elif outreach_already_sent(row["profile_url"], "email"):
        st.warning("Duplicate blocked: email outreach already exists.")
    else:
        message_id = save_message(row["profile_url"], message.to_dict())
        record_outreach(row["profile_url"], "email", row["contact_email"], "sent", message_id)
        st.success("Email simulated and logged.")

if st.button("Simulate Instagram DM"):
    if outreach_already_sent(row["profile_url"], "instagram"):
        st.warning("Duplicate blocked: Instagram outreach already exists.")
    else:
        message_id = save_message(row["profile_url"], message.to_dict())
        record_outreach(row["profile_url"], "instagram", "Manual Instagram DM", "sent", message_id)
        st.success("Instagram DM simulated and logged.")

st.subheader("Outreach Tracker")
rows = get_outreach_rows()
if rows:
    st.dataframe(pd.DataFrame([dict(row) for row in rows]), use_container_width=True)
else:
    st.info("No outreach has been simulated yet.")

st.subheader("Sending Policy")
st.write(
    "This version uses simulation only. Email and Instagram actions are logged without contacting creators. "
    "Instagram is treated as a manual channel."
)
