# AI-Powered Micro-Influencer Outreach System

````markdown
> A modular, reusable AI pipeline for discovering, filtering, enriching, personalizing, and tracking outreach to micro-influencers.

This system is designed to be reusable across creator-outreach campaigns by keeping the brand name and other campaign settings configurable through environment variables.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Data Flow](#data-flow)
- [Setup](#setup)
- [API Setup](#api-setup)
- [Configuration](#configuration)
- [Running the Pipeline](#running-the-pipeline)
- [Streamlit Demo](#streamlit-demo)
- [Testing](#testing)
- [Data Quality](#data-quality)
- [Generated Outputs](#generated-outputs)
- [Cost Considerations](#cost-considerations)
- [Design Decisions](#design-decisions)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [License](#license)

## Features

- Discover micro-influencers using the YouTube Data API
- Filter creators by subscriber range and niche relevance
- Enrich creator profiles using publicly available information
- Identify publicly listed contact emails without guessing missing addresses
- Generate personalized outreach using Groq
- Generate both email and Instagram DM copy
- Validate generated message length
- Simulate outreach before any real communication
- Track outreach activity using SQLite
- Prevent duplicate outreach
- Provide a Streamlit interface for reviewing creators and messages
- Reuse previously collected data without making new discovery API calls

## Architecture

```text
YouTube Data API
       |
       v
   Discovery
       |
       v
    Filtering
       |
       v
   Enrichment
       |
       v
  Personalization
       |
       v
  Message Review
       |
       v
 Simulated Sending
       |
       v
 SQLite Tracking
```

## Tech Stack

- **Python**
- **YouTube Data API v3** - Creator discovery
- **Groq API** - AI personalization
- **GPT-OSS 20B on Groq** - Outreach generation
- **Pandas** - Data processing
- **Pydantic** - Data validation
- **BeautifulSoup + Requests** - Profile enrichment
- **SQLite** - Outreach tracking
- **Streamlit** - Review interface
- **Pytest** - Testing

## Project Structure

```text
.
├── app/
│   ├── database/
│   │   └── db.py
│   ├── discovery/
│   │   └── youtube.py
│   ├── enrichment/
│   │   └── profile.py
│   ├── filtering/
│   │   └── classifier.py
│   ├── personalization/
│   │   └── generator.py
│   ├── sending/
│   │   └── sender.py
│   └── models.py
├── data/
│   ├── influencers_raw.csv
│   ├── influencers_filtered.csv
│   ├── influencers_enriched.csv
│   ├── personalized_messages.csv
│   └── outreach.db
├── tests/
│   └── test_validation.py
├── run_pipeline.py
├── streamlit_app.py
├── requirements.txt
├── .env.example
└── README.md
```

## Data Flow

### 1. Discovery
The discovery layer uses YouTube Data API v3 to find relevant creator channels.

Search queries cover areas such as:
- Artificial Intelligence
- Generative AI
- Machine Learning
- LLMs
- AI Agents
- AI Development
- LangChain

The system collects channel information and removes duplicate channels.

### 2. Filtering
Creators are filtered using configurable subscriber limits and content relevance.

Default range:
- **5,000 - 100,000 subscribers**

Creators outside the configured range or without sufficient relevance are excluded.

### 3. Enrichment
The enrichment layer collects publicly available information such as:
- Creator name
- Platform
- Profile URL
- Subscriber count
- Niche
- Content themes
- Public contact email

Rules:
- If an email cannot be found publicly, the value is recorded as `Not Found`
- Unavailable engagement information is recorded as `Not Available`

The system does not guess or fabricate contact information or engagement metrics.

### 4. AI Personalization
Groq is used to generate a factual personalization component based only on the supplied creator information.

The final outreach message is assembled programmatically to maintain consistent structure and prevent unsupported claims.

Default model:
```text
openai/gpt-oss-20b
```

This is a GPT-OSS model served through Groq's API and does not require the OpenAI Python SDK.

### 5. Outreach
The system generates:
- Personalized email
- Instagram DM

Validation:
- Email messages: **60-90 words**
- Instagram DMs: **15-30 words**

### 6. Sending and Tracking
The current implementation uses **simulated sending**.
No creator is contacted automatically.

Each simulated action is stored in SQLite with:
- Influencer
- Channel
- Destination
- Status
- Timestamp

Duplicate checks prevent the same outreach channel from being logged more than once for the same creator.

Instagram is treated as a manual/simulated channel because automated Instagram messaging requires platform-specific permissions and access.

## Setup

1. Clone the repository and enter the project directory.

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create the environment file:
```bash
cp .env.example .env
```

5. Add the required API keys and configuration values to `.env`:
```env
YOUTUBE_API_KEY=YOUR_YOUTUBE_API_KEY
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-20b
BRAND_NAME=YOUR_BRAND_NAME

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SENDER_EMAIL=

MIN_SUBSCRIBERS=5000
MAX_SUBSCRIBERS=100000
TARGET_INFLUENCERS=60
```

> API keys should never be committed to GitHub.

## API Setup

### YouTube Data API
1. Create a project in Google Cloud
2. Enable YouTube Data API v3
3. Create an API key
4. Add the key to `YOUTUBE_API_KEY`

The discovery process is designed to limit unnecessary API usage and deduplicate discovered channels.

### Groq
1. Create a Groq API key
2. Add it to `GROQ_API_KEY`
3. The model can be configured through `GROQ_MODEL`

Default configuration uses `openai/gpt-oss-20b`.

## Configuration

| Variable | Description | Example / Default |
|---|---|---|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | `YOUR_YOUTUBE_API_KEY` |
| `GROQ_API_KEY` | Groq API key | `YOUR_GROQ_API_KEY` |
| `GROQ_MODEL` | Personalization model | `openai/gpt-oss-20b` |
| `BRAND_NAME` | Brand name used in outreach | `YOUR_BRAND_NAME` |
| `MIN_SUBSCRIBERS` | Minimum subscribers | `5000` |
| `MAX_SUBSCRIBERS` | Maximum subscribers | `100000` |
| `TARGET_INFLUENCERS` | Target number of creators | `60` |

To reuse this system for a new campaign, just change `BRAND_NAME` and the subscriber limits no code changes required.

## Running the Pipeline

Run the complete pipeline:
```bash
python run_pipeline.py
```

This performs:
```text
Discovery → Filtering → Enrichment → Personalization → Database Tracking
```

Generated files are stored in the `data/` directory.

### Reusing Existing Data

To regenerate personalized messages without making new YouTube discovery requests:
```bash
python run_pipeline.py --reuse-data
```

This loads the existing enriched dataset and skips the discovery stage. This is useful when experimenting with personalization without consuming additional discovery API quota.

## Streamlit Demo

Launch the interface:
```bash
streamlit run streamlit_app.py
```

The interface allows creators and generated outreach messages to be reviewed before simulated sending.

The demo also shows outreach tracking and duplicate-prevention behavior.

## Testing

Run the test suite with:
```bash
pytest
```

## Data Quality

The system follows these rules:
- No invented follower counts
- No guessed email addresses
- Missing emails are recorded as `Not Found`
- Missing engagement data is recorded as `Not Available`
- Personalization is generated from supplied creator facts
- Outreach messages are length-validated
- Duplicate outreach is prevented through database checks
- Sending is simulated by default

## Generated Outputs

The pipeline produces:
- `data/influencers_raw.csv`
- `data/influencers_filtered.csv`
- `data/influencers_enriched.csv`
- `data/personalized_messages.csv`
- `data/outreach.db`

These outputs make it possible to inspect each stage of the pipeline independently.

## Cost Considerations

The project is designed to minimize external costs. YouTube uses standard API quota, while Groq availability and usage limits depend on the account tier and current provider policies.

The application processes creators sequentially and uses relatively short prompts for personalization. The sending layer is simulation-only by default, so no paid email provider is required.

Provider pricing, quotas, and free-tier policies can change over time.

## Design Decisions

The project separates discovery, filtering, enrichment, personalization, sending, and persistence into independent modules.

This makes it possible to replace individual components without rewriting the entire pipeline.

For example:
- YouTube discovery can be extended with additional compliant data sources
- SQLite can be replaced with PostgreSQL
- Groq can be replaced with another LLM provider
- Simulated sending can be connected to an approved email provider
- Additional social platforms can be added as separate discovery or outreach modules

## Limitations

- Discovery currently focuses on YouTube
- Instagram outreach is manual/simulated
- Publicly available contact information may be incomplete
- Engagement metrics may not be available for every creator
- Real email delivery is not enabled by default
- API quotas and provider limits apply

## Future Improvements

Possible extensions include:
- Multi platform creator discovery
- More advanced creator scoring
- Campaign level analytics
- Email delivery integration
- Response tracking
- PostgreSQL-based persistence
- Background job processing
- Automated evaluation of generated outreach
- Additional personalization signals

## License

This project is intended as a portfolio and learning project demonstrating an AI-powered outreach workflow.
