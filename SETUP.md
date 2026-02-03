# WikiVerify Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd wiki-verify
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Database

**Option A: Using Docker (Recommended)**

```bash
docker-compose up -d
```

This will start a PostgreSQL database on port 5432.

**Option B: Manual Setup**

```bash
createdb wikiverify
psql wikiverify < schema.sql
```

### 3. Configure Environment

Create a `.env` file in the `wiki-verify` directory:

```bash
# Database Configuration
DATABASE_URL=postgresql://wikiverify:wikiverify@localhost:5432/wikiverify

# Wikipedia API Configuration
WIKIPEDIA_USER_AGENT=WikiVerify/1.0 (contact@example.com)

# Rate Limiting
RATE_LIMIT_DELAY=1
CHECK_TIMEOUT=10
```

### 4. Test the Setup

```bash
# Import some test articles
python scripts/initial_import.py

# Run the broken link agent
python -m agents.broken_link_agent
```

## Project Structure

```
wiki-verify/
├── agents/              # Verification agents
│   ├── base_agent.py
│   ├── broken_link_agent.py
│   └── retraction_agent.py
├── core/                # Core functionality
│   ├── config.py        # Configuration management
│   ├── database.py      # Database operations
│   └── parser.py        # Citation parsing
├── integrations/        # External API integrations
│   ├── wikipedia_api.py
│   ├── internet_archive.py
│   └── retraction_watch.py
├── scripts/             # Utility scripts
│   └── initial_import.py
├── schema.sql           # Database schema
├── requirements.txt     # Python dependencies
└── docker-compose.yml   # Docker setup
```

## What's Implemented

✅ **Phase 0: Foundation**
- Project structure
- Configuration system
- Database connection layer
- Database schema

✅ **Phase 1: Wikipedia Parser**
- Wikipedia API integration
- Citation parser (mwparserfromhell)
- Initial import script

✅ **Phase 2: Broken Link Agent**
- URL checking (HEAD/GET requests)
- Error detection (404, 500, timeouts)
- Homepage redirect detection
- Internet Archive integration

✅ **Phase 3: Retraction Agent (Partial)**
- Retraction Watch integration
- DOI matching
- Database caching

## Next Steps

🚧 **To Be Implemented:**
- PubMed integration
- CrossRef integration
- Source Change Agent
- Evidence Agent
- Output formatters
- Wikipedia bot
- Scheduler

## Troubleshooting

**Database Connection Error:**
- Make sure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify database exists: `psql -l | grep wikiverify`

**Import Errors:**
- Check internet connection (Wikipedia API requires network)
- Verify rate limiting is working (1 request/second)

**Agent Errors:**
- Ensure database schema is set up: `psql wikiverify < schema.sql`
- Check that citations exist in database before running agents
