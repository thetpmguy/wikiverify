# WikiVerify

AI agents that monitor Wikipedia citations and alert editors when sources break, get retracted, or change.

## Overview

WikiVerify is a system of automated agents that continuously check Wikipedia's citations for problems:
- **Broken Link Agent**: Detects when source URLs no longer work
- **Retraction Agent**: Finds when cited papers have been retracted
- **Source Change Agent**: Monitors when source content changes significantly
- **Evidence Agent**: Assesses how well claims are supported by research

## Project Structure

```
wiki-verify/
├── agents/              # Verification agents
├── core/                # Core functionality (config, database, parser)
├── integrations/        # External API integrations
├── llm/                 # LLM integration for analysis
├── output/              # Output formatters and Wikipedia bot
├── scripts/             # Utility scripts
└── tests/               # Tests
```

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Docker (optional, for database)

### Installation

1. Clone the repository:
```bash
cd wiki-verify
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
psql wikiverify < schema.sql  # (schema to be created)
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

### Database Schema

Run the SQL commands from `IMPLEMENTATION_PLAN.md` Step 3 to create the database schema, or use the provided schema file (to be created).

## Usage

### Import Articles

```bash
python scripts/initial_import.py
```

### Run Agents

```bash
# Broken Link Agent
python -m agents.broken_link_agent

# Retraction Agent
python -m agents.retraction_agent

# Source Change Agent
python -m agents.source_change_agent

# Run all agents (test mode)
python scripts/scheduler.py --run-now

# Start scheduler (production)
python scripts/scheduler.py
```

## Development Status

✅ **Completed:**
- Project structure
- Core configuration and database layer
- Wikipedia API integration and citation parser
- Initial import script
- **Broken Link Agent** - Detects broken URLs
- **Retraction Agent** - Detects retracted papers (Retraction Watch, PubMed, CrossRef)
- **Source Change Agent** - Detects content changes
- Internet Archive integration
- Snapshot system
- Content extraction and comparison
- Output formatters
- Scheduler system

🚧 **To Be Implemented:**
- Evidence Agent (LLM-based analysis)
- Wikipedia bot (Talk page posting)
- Wikipedia gadget (browser extension)

## License

MIT License
