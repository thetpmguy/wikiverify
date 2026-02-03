# WikiVerify Setup Instructions

## Step-by-Step Setup Guide

### Step 1: Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

### Step 2: Create Database

```bash
# Create database
createdb wikiverify

# Or using psql
psql postgres
CREATE DATABASE wikiverify;
\q
```

### Step 3: Set Up Schema

```bash
cd wiki-verify
psql wikiverify < schema.sql
```

Or use the setup script:
```bash
./setup_database.sh
```

### Step 4: Configure Environment

The `.env` file has been created with default values. Update it with your database credentials:

```bash
# Edit .env file
nano .env  # or use your preferred editor
```

Update these values:
- `DATABASE_URL`: Your PostgreSQL connection string
- `WIKIPEDIA_USER_AGENT`: Your email address
- `PUBMED_EMAIL`: Your email (recommended for PubMed API)

### Step 5: Install Python Dependencies

```bash
cd wiki-verify
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 6: Verify Setup

```bash
python scripts/verify_setup.py
```

This will check:
- ✓ All imports work
- ✓ Configuration is set
- ✓ Database connection works
- ✓ Database schema exists

### Step 7: Test the System

```bash
# Import some test articles
python scripts/initial_import.py

# Run a test agent
python -m agents.broken_link_agent

# Or run all agents in test mode
python scripts/scheduler.py --run-now
```

## Alternative: Using Docker

If you have Docker installed:

```bash
# Start PostgreSQL container
docker-compose up -d

# Wait a few seconds for it to start, then:
psql -h localhost -U wikiverify -d wikiverify -f schema.sql
# Password: wikiverify
```

Update `.env`:
```
DATABASE_URL=postgresql://wikiverify:wikiverify@localhost:5432/wikiverify
```

## Troubleshooting

### Database Connection Issues

**Error: "connection refused"**
- Make sure PostgreSQL is running: `pg_isready` or `brew services list`
- Check if PostgreSQL is listening: `lsof -i :5432`

**Error: "database does not exist"**
- Create it: `createdb wikiverify`

**Error: "relation does not exist"**
- Run schema: `psql wikiverify < schema.sql`

### Python Import Errors

**Error: "No module named 'psycopg2'"**
- Install dependencies: `pip install -r requirements.txt`

**Error: "No module named 'core'"**
- Make sure you're in the wiki-verify directory
- Activate virtual environment: `source venv/bin/activate`

### Permission Issues

**Error: "permission denied"**
- Make sure you have PostgreSQL user permissions
- Try: `psql -U postgres` (superuser)

## Quick Test Commands

```bash
# Check PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep wikiverify

# Check tables exist
psql wikiverify -c "\dt"

# Count citations
psql wikiverify -c "SELECT COUNT(*) FROM citations;"

# View recent findings
psql wikiverify -c "SELECT * FROM findings ORDER BY found_date DESC LIMIT 5;"
```

## Next Steps

Once setup is complete:

1. **Import Articles**: Edit `scripts/initial_import.py` to add more article titles
2. **Run Agents**: Use the scheduler or run agents individually
3. **Monitor**: Check `wiki-verify.log` for agent activity
4. **View Results**: Query the database to see findings

## Getting Help

- Check logs: `tail -f wiki-verify.log`
- Run verification: `python scripts/verify_setup.py`
- Review documentation: `README.md`, `QUICKSTART.md`
