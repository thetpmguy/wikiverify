# WikiVerify

AI agents that monitor Wikipedia citations and alert editors when cited papers are retracted.

## Overview

WikiVerify is a system of automated agents that monitor Wikipedia citations for problems. The system uses a combination of ML models for detection, external APIs for data collection, and LLMs for generating human-readable notifications. It operates on a periodic schedule with three distinct cycles: monthly data updates, weekly citation imports, and daily verification runs.

### Key Features

- **Synthesizer Agent**: Orchestrates retraction checking using ML models (citation extractor, paper matcher, severity classifier)
- **ML-Based Detection**: Uses trained models for citation extraction and retraction matching
- **Local-First Architecture**: Daily verification uses local data only; external APIs called only during scheduled refresh cycles

## Architecture

WikiVerify operates on three independent cycles:

### Monthly Cycle
- Downloads retraction database from CrossRef and PubMed APIs
- Precomputes embeddings for all retracted papers
- Updates local data files

### Weekly Cycle
- Imports new/changed citations from Wikipedia articles
- Updates PostgreSQL database with citation data

### Daily Cycle
- Synthesizer Agent checks citations against local retraction data
- Uses ML models for citation extraction and matching
- Generates notifications for retracted citations
- No external API calls (except LLM for notification text)

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Project Structure

```
wiki-verify/
├── agents/
│   ├── base_agent.py              # Abstract base class for all agents
│   └── synthesizer_agent.py       # Orchestrates retraction checking and notifications
│
├── core/
│   ├── config.py                  # Configuration management
│   ├── constants.py               # Constants and enums (ProblemType, Severity)
│   ├── database.py                # Database operations with context manager
│   ├── logger.py                  # Structured logging system
│   ├── parser.py                  # Wikipedia citation parsing
│   └── utils.py                   # Shared HTTP client, rate limiter
│
├── integrations/
│   ├── crossref.py                # CrossRef API client
│   ├── pubmed.py                  # PubMed API client
│   ├── retraction_watch.py        # Retraction Watch integration
│   └── wikipedia_api.py           # Wikipedia API client
│
├── ml/
│   ├── citation_extractor.py      # Loads and runs NER model (Model A)
│   ├── paper_matcher.py           # Loads sentence transformer + embeddings (Model C)
│   └── severity_classifier.py     # Loads and runs severity model (Model B)
│
├── checkers/
│   └── retraction_checker.py      # Main retraction checking logic
│
├── llm/
│   └── llm_triage.py              # LLM integration for triage and notifications
│
├── output/
│   ├── formatters.py              # Output formatting for findings
│   └── wiki_bot.py                # Wikipedia Talk page bot (future)
│
├── scripts/
│   ├── initial_import.py                      # Import Wikipedia articles
│   ├── download_retraction_database.py        # Download retractions from APIs
│   ├── precompute_retraction_embeddings.py    # Generate embeddings file
│   ├── build_ner_dataset.py                   # Build NER training data
│   └── scheduler.py                           # Runs all cycles on schedule
│
└── tests/
    ├── test_retraction_checker.py
    ├── test_citation_extractor.py
    ├── test_paper_matcher.py
    └── test_severity_classifier.py
```

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Docker (optional, for database)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/thetpmguy/wikiverify.git
cd wikiverify
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
# Using Docker
docker-compose up -d

# Or manually
createdb wikiverify
psql wikiverify < schema.sql
```

5. Configure environment variables:
```bash
cp env_template.txt .env
# Edit .env with your settings
```

### Initial Setup (One-Time)

1. **Download retraction database** (monthly cycle):
```bash
python scripts/download_retraction_database.py
```

2. **Precompute embeddings** (monthly cycle):
```bash
python scripts/precompute_retraction_embeddings.py
```

3. **Import Wikipedia articles** (weekly cycle):
```bash
python scripts/initial_import.py
```

## Usage

### Running the Synthesizer Agent

```bash
# Synthesizer Agent (daily retraction checking)
python -m agents.synthesizer_agent

# Run scheduler (production)
python scripts/scheduler.py
```

### Scheduler

The scheduler manages all three cycles:

- **Monthly** (1st of each month): Downloads retraction database and precomputes embeddings
- **Weekly** (every Monday): Imports new/changed citations from Wikipedia
- **Daily** (every day at 6 AM): Runs synthesizer agent to check citations

## ML Models

WikiVerify uses three ML models for retraction detection:

1. **Citation Extractor (Model A)**: Extracts structured fields from unstructured citation text
   - Base: SciBERT fine-tuned for NER
   - Size: ~400 MB
   - Used when citations lack DOI or structured fields

2. **Severity Classifier (Model B)**: Classifies retraction severity
   - Base: DistilBERT fine-tuned for classification
   - Size: ~250 MB
   - Severity levels: critical, major, minor, corrected

3. **Paper Matcher (Model C)**: Matches citations to retracted papers using embeddings
   - Base: all-MiniLM-L6-v2 sentence transformer
   - Size: ~80 MB
   - Uses precomputed embeddings for fast comparison

Models are loaded once at startup and stay in memory for the entire daily run.

## Development Status

✅ **Completed:**
- Project structure and core infrastructure
- Core configuration and database layer
- Wikipedia API integration and citation parser
- LLM triage integration
- Output formatters
- Scheduler system

🚧 **In Progress:**
- Synthesizer Agent implementation
- Retraction Checker implementation
- ML model integration (citation extractor, paper matcher, severity classifier)
- Monthly/weekly cycle scripts

🚧 **Future Enhancements:**
- Wikipedia bot (automated Talk page posting)
- Wikipedia gadget (browser extension)
- Evidence Agent (LLM-based claim verification)

## License

MIT License
