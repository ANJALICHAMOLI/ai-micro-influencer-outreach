from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class Influencer(BaseModel):
    name: str
    platform: str
    profile_url: str
    follower_count: int = Field(ge=0)
    engagement_rate: str
    niche: str
    content_themes: list[str]
    contact_email: str
    qualification_status: str
    qualification_reason: str
    source_query: str = ""


class PersonalizedMessage(BaseModel):
    influencer_name: str
    email_subject: str
    email_body: str
    instagram_dm: str
    email_word_count: int
    dm_word_count: int


class OutreachRecord(BaseModel):
    influencer_name: str
    channel: str
    destination: str
    status: str
    message_id: Optional[str] = None
