# WikiVerify Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ (or Docker)
- Internet connection (for Wikipedia API and external services)

## Installation

### 1. Install Python Dependencies

```bash
cd wiki-verify
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Database

**Option A: Using Docker (Easiest)**

```bash
docker-compose up -d
```

Wait a few seconds for PostgreSQL to start, then:

```bash
psql -h localhost -U wikiverify -d wikiverify -f schema.sql
# Password: wikiverify
```

**Option B: Manual PostgreSQL Setup**

```bash
createdb wikiverify
psql wikiverify < schema.sql
```

### 3. Configure Environment

Create a `.env` file in the `wiki-verify` directory:

```bash
# Database
DATABASE_URL=postgresql://wikiverify:wikiverify@localhost:5432/wikiverify

# Wikipedia API
WIKIPEDIA_USER_AGENT=WikiVerify/1.0 (your-email@example.com)

# Optional: For PubMed/CrossRef APIs
PUBMED_EMAIL=your-email@example.com

# Rate Limiting
RATE_LIMIT_DELAY=1
CHECK_TIMEOUT=10
```

## Quick Test

### 1. Import Some Articles

```bash
python scripts/initial_import.py
```

This will import a few test articles (Aspirin, Diabetes, etc.) and their citations.

### 2. Run an Agent

**Broken Link Agent:**
```bash
python -m agents.broken_link_agent
```

**Retraction Agent:**
```bash
python -m agents.retraction_agent
```

**Source Change Agent:**
```bash
python -m agents.source_change_agent
```

### 3. Run All Agents (Test Mode)

```bash
python scripts/scheduler.py --run-now
```

## Production Usage

### Start the Scheduler

The scheduler will run agents automatically:

```bash
python scripts/scheduler.py
```

**Schedule:**
- Broken Link Agent: Daily at 3:00 AM
- Retraction Agent: Daily at 4:00 AM  
- Source Change Agent: Weekly on Sunday at 2:00 AM

### Check Logs

Logs are written to `wiki-verify.log` and also printed to console.

## What Each Agent Does

### Broken Link Agent
- Checks if citation URLs are still accessible
- Detects 404 errors, timeouts, and broken redirects
- Checks Internet Archive for archived versions

### Retraction Agent
- Matches citations against retraction databases
- Checks Retraction Watch database (cached)
- Optionally checks PubMed and CrossRef APIs

### Source Change Agent
- Compares current source content with archived snapshots
- Flags significant content changes (>20% difference)
- Creates snapshots for new citations

## Troubleshooting

**Database Connection Error:**
```bash
# Check if PostgreSQL is running
psql -h localhost -U wikiverify -d wikiverify -c "SELECT 1;"
```

**Import Errors:**
- Make sure you have internet connection
- Check rate limiting (1 request/second to Wikipedia)
- Verify article titles are correct

**Agent Errors:**
- Ensure database schema is set up: `psql wikiverify < schema.sql`
- Check that citations exist before running agents
- Review logs in `wiki-verify.log`

## Next Steps

1. **Import More Articles**: Edit `scripts/initial_import.py` to add more article titles
2. **Customize Schedule**: Edit `scripts/scheduler.py` to change run times
3. **Add Output**: Implement Wikipedia bot in `output/wiki_notify.py` (see IMPLEMENTATION_PLAN.md)
4. **Add LLM Analysis**: Implement Evidence Agent (requires API keys)

## Files Created

After running agents, check the database:

```sql
-- View all findings
SELECT * FROM findings ORDER BY found_date DESC LIMIT 10;

-- View citations
SELECT wikipedia_article, COUNT(*) as citation_count 
FROM citations 
GROUP BY wikipedia_article;
```
