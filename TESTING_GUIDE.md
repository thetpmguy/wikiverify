# WikiVerify Testing Guide

## Quick Test Sequence

Follow these steps to test WikiVerify from start to finish.

### Step 1: Verify Setup

```bash
cd /Users/rk/Documents/wiki/wiki-verify
source venv/bin/activate
python scripts/verify_setup.py
```

**Expected Output:**
- ✓ All imports successful
- ✓ Configuration looks good
- ✓ Database connection successful
- ✓ All required tables exist

### Step 2: Test Article Import

Import a test article to populate the database:

```bash
python scripts/test_import.py Aspirin
```

**What it does:**
- Fetches the "Aspirin" Wikipedia article
- Parses all citations
- Saves them to the database

**Expected Output:**
```
Testing import for article: Aspirin
==================================================
1. Fetching article from Wikipedia...
✓ Article fetched: Aspirin
2. Parsing citations...
✓ Found X citations
3. Saving citations to database...
✓ Saved X citations
4. Verifying in database...
✓ Found X citations in database for this article
```

### Step 3: Test Broken Link Agent

Check if the agent can detect broken links:

```bash
python -m agents.broken_link_agent
```

**What it does:**
- Checks URLs from citations in the database
- Detects broken links (404, timeouts, etc.)
- Saves findings to the database

**Expected Output:**
```
[broken_link_agent] Starting Broken Link Agent
[broken_link_agent] Found X citations to check
[broken_link_agent] Checking citation 1: https://...
[broken_link_agent] Completed: Checked X citations, found Y broken links
```

### Step 4: Test Retraction Agent

Check if the agent can detect retracted papers:

```bash
python -m agents.retraction_agent
```

**What it does:**
- Updates retraction cache from Retraction Watch
- Checks citations against retraction database
- Saves findings for retracted papers

**Expected Output:**
```
[retraction_agent] Starting Retraction Agent
[retraction_agent] Updating retraction cache...
[retraction_agent] Updated X retraction records
[retraction_agent] Found X citations with DOIs to check
[retraction_agent] Completed: Checked X citations, found Y retractions
```

### Step 5: View Results in Database

Check what was found:

```bash
# Add PostgreSQL to PATH
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# View citations
psql wikiverify -c "SELECT wikipedia_article, COUNT(*) as count FROM citations GROUP BY wikipedia_article;"

# View findings
psql wikiverify -c "SELECT problem_type, COUNT(*) as count FROM findings GROUP BY problem_type;"

# View recent findings
psql wikiverify -c "SELECT wikipedia_article, problem_type, severity, found_date FROM findings ORDER BY found_date DESC LIMIT 10;"
```

### Step 6: Test Source Change Agent (Optional)

This requires citations with snapshots. It will:
- Compare current source content with archived versions
- Detect significant content changes

```bash
python -m agents.source_change_agent
```

### Step 7: Test Output Formatters

Test how findings are formatted:

```python
# In Python shell
source venv/bin/activate
python

>>> from core.database import execute_query
>>> from output.formatters import FindingFormatter
>>> 
>>> # Get a finding
>>> findings = execute_query("SELECT * FROM findings LIMIT 1")
>>> if findings:
...     finding = findings[0]
...     print(FindingFormatter.format_finding(finding))
```

## Complete Test Run

Run all agents at once:

```bash
python scripts/scheduler.py --run-now
```

This runs all agents in test mode without waiting for the schedule.

## Testing Different Articles

Test with different types of articles:

```bash
# Medical article
python scripts/test_import.py "Diabetes"

# Science article
python scripts/test_import.py "Quantum mechanics"

# Biography
python scripts/test_import.py "Albert Einstein"
```

## Verify Database Contents

```bash
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# Count citations
psql wikiverify -c "SELECT COUNT(*) as total_citations FROM citations;"

# Count findings
psql wikiverify -c "SELECT COUNT(*) as total_findings FROM findings;"

# View citation details
psql wikiverify -c "SELECT id, wikipedia_article, citation_number, source_url, source_doi FROM citations LIMIT 5;"

# View finding details
psql wikiverify -c "SELECT id, wikipedia_article, problem_type, severity, details FROM findings LIMIT 5;"
```

## Expected Test Results

### After Import
- ✅ Citations table has entries
- ✅ Each citation has article name, URL, DOI (if available)
- ✅ Citation numbers are assigned

### After Broken Link Agent
- ✅ Findings table may have entries (if broken links found)
- ✅ Problem type: "broken_link"
- ✅ Details include error information

### After Retraction Agent
- ✅ Retractions_cache table has entries
- ✅ Findings table may have entries (if retracted papers found)
- ✅ Problem type: "retraction"
- ✅ Severity: "high"

## Troubleshooting Tests

### "No citations found"
- Article might not have citations
- Try a different article: `python scripts/test_import.py "Aspirin"`

### "Database connection failed"
- Check PostgreSQL is running: `brew services list | grep postgresql`
- Verify .env file has correct DATABASE_URL

### "Module not found"
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### "No findings created"
- This is normal! Not all citations will have problems
- Try importing more articles
- Check that citations have URLs (for broken link agent) or DOIs (for retraction agent)

## Next Steps After Testing

Once testing is successful:

1. **Import more articles**: Edit `scripts/initial_import.py` to add more articles
2. **Set up scheduler**: Run `python scripts/scheduler.py` to start automated checking
3. **Monitor logs**: Check `wiki-verify.log` for agent activity
4. **View results**: Query database regularly to see findings

## Quick Test Checklist

- [ ] Setup verification passes
- [ ] Can import at least one article
- [ ] Citations are saved to database
- [ ] Broken link agent runs without errors
- [ ] Retraction agent runs without errors
- [ ] Can query database and see results
- [ ] Findings are created (if problems exist)
