import os
import sqlite3
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(os.getenv("DATABASE_PATH", "data/outreach.db"))


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as conn:
        conn.executescript(
            '''
            CREATE TABLE IF NOT EXISTS influencers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                profile_url TEXT NOT NULL UNIQUE,
                follower_count INTEGER NOT NULL,
                engagement_rate TEXT NOT NULL,
                niche TEXT NOT NULL,
                content_themes TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                qualification_status TEXT NOT NULL,
                qualification_reason TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                profile_url TEXT NOT NULL,
                email_subject TEXT NOT NULL,
                email_body TEXT NOT NULL,
                instagram_dm TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS outreach (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_url TEXT NOT NULL,
                channel TEXT NOT NULL,
                destination TEXT NOT NULL,
                status TEXT NOT NULL,
                message_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(profile_url, channel)
            );
            '''
        )


def upsert_influencer(row):
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO influencers
            (name, platform, profile_url, follower_count, engagement_rate, niche,
             content_themes, contact_email, qualification_status, qualification_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(profile_url) DO UPDATE SET
                name=excluded.name,
                follower_count=excluded.follower_count,
                engagement_rate=excluded.engagement_rate,
                niche=excluded.niche,
                content_themes=excluded.content_themes,
                contact_email=excluded.contact_email,
                qualification_status=excluded.qualification_status,
                qualification_reason=excluded.qualification_reason
            ''',
            (
                row["name"],
                row["platform"],
                row["profile_url"],
                int(row["follower_count"]),
                row["engagement_rate"],
                row["niche"],
                ", ".join(row["content_themes"]),
                row["contact_email"],
                row["qualification_status"],
                row["qualification_reason"],
            ),
        )


def save_message(profile_url, message):
    message_id = str(uuid4())
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO messages
            (id, profile_url, email_subject, email_body, instagram_dm)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                message_id,
                profile_url,
                message["email_subject"],
                message["email_body"],
                message["instagram_dm"],
            ),
        )
    return message_id


def outreach_already_sent(profile_url, channel):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM outreach WHERE profile_url = ? AND channel = ? AND status = 'sent'",
            (profile_url, channel),
        ).fetchone()
    return row is not None


def record_outreach(profile_url, channel, destination, status, message_id=None):
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO outreach(profile_url, channel, destination, status, message_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(profile_url, channel) DO UPDATE SET
                destination=excluded.destination,
                status=excluded.status,
                message_id=excluded.message_id
            ''',
            (profile_url, channel, destination, status, message_id),
        )


def get_outreach_rows():
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM outreach ORDER BY created_at DESC"
        ).fetchall()
