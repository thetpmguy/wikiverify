# End-to-End Testing Guide

This guide walks you through testing WikiVerify from start to finish.

## Prerequisites

Before starting, ensure:
- ✅ PostgreSQL is running
- ✅ Database is created and schema is applied
- ✅ Python virtual environment is activated
- ✅ Dependencies are installed
- ✅ `.env` file is configured

## Quick E2E Test (Automated)

Run the automated E2E test script:

```bash
cd /Users/rk/Documents/wiki/wiki-verify
source venv/bin/activate
python scripts/e2e_test.py
```

This will:
1. Verify setup
2. Import test articles
3. Run all agents
4. Check results
5. Display summary

## Manual E2E Test (Step-by-Step)

### Step 1: Verify Setup

```bash
cd /Users/rk/Documents/wiki/wiki-verify
source venv/bin/activate
python scripts/verify_setup.py
```

**Expected Output:**
```
✅ All imports successful
✅ Configuration looks good
✅ Database connection successful
✅ All required tables exist
```

### Step 2: Clear Previous Test Data (Optional)

If you want a clean slate:

```bash
psql wikiverify -c "TRUNCATE citations, findings, retractions_cache CASCADE;"
```

### Step 3: Import Test Articles

Import some Wikipedia articles to test with:

```bash
# Import a single article
python scripts/test_import.py Aspirin

# Or import multiple articles
python scripts/test_import.py "Diabetes"
python scripts/test_import.py "COVID-19"
python scripts/test_import.py "Machine learning"
```

**Expected Output:**
```
Testing import for article: Aspirin
==================================================
1. Fetching article from Wikipedia...
✓ Article fetched: Aspirin
2. Parsing citations...
✓ Found 45 citations
3. Saving citations to database...
✓ Saved 5 citations
4. Verifying in database...
✓ Found 5 citations in database for this article
```

### Step 4: Verify Citations in Database

```bash
python -c "
from core.database import execute_query
result = execute_query('SELECT COUNT(*) as count FROM citations')
print(f'Total citations: {result[0][\"count\"] if result else 0}')
"
```

### Step 5: Run Broken Link Agent

Test the broken link detection:

```bash
python -m agents.broken_link_agent
```

Or with custom parameters:

```bash
python -c "
from agents.broken_link_agent import BrokenLinkAgent
agent = BrokenLinkAgent()
agent.run(days=365, limit=10)  # Check 10 citations
"
```

**Expected Output:**
```
[broken_link_agent] Starting Broken Link Agent
[broken_link_agent] Found 10 citations to check
[broken_link_agent] Checking citation 1: https://...
[broken_link_agent] Found broken link: https://...
[broken_link_agent] Completed: Checked 10 citations, found 2 broken links
```

### Step 6: Run Retraction Agent

Test retraction detection:

```bash
python -m agents.retraction_agent
```

Or with custom parameters:

```bash
python -c "
from agents.retraction_agent import RetractionAgent
agent = RetractionAgent()
agent.run(update_cache=True, use_apis=False)
"
```

**Expected Output:**
```
[retraction_agent] Starting Retraction Agent
[retraction_agent] Updating retraction cache...
[retraction_agent] Updated 15000 retraction records
[retraction_agent] Found 25 citations with DOIs to check
[retraction_agent] Completed: Checked 25 citations, found 0 retractions
```

### Step 7: Run Source Change Agent

Test source change detection:

```bash
python -m agents.source_change_agent
```

Or with custom parameters:

```bash
python -c "
from agents.source_change_agent import SourceChangeAgent
agent = SourceChangeAgent()
agent.run(limit=10)  # Check 10 citations
"
```

**Expected Output:**
```
[source_change_agent] Starting Source Change Agent
[source_change_agent] Found 10 citations with snapshots to check
[source_change_agent] Checking citation 1: https://...
[source_change_agent] Completed: Checked 10 citations, found 1 content changes
```

### Step 8: Run All Agents at Once

Test all agents together:

```bash
python scripts/scheduler.py --run-now
```

**Expected Output:**
```
[INFO] Running all agents now...
[INFO] Starting scheduled run: Broken Link Agent
[broken_link_agent] Starting Broken Link Agent
...
[INFO] Completed: Broken Link Agent
[INFO] Starting scheduled run: Retraction Agent
...
[INFO] All agents completed
```

### Step 9: Check Results

View findings in the database:

```bash
python -c "
from core.database import execute_query

# Total findings
findings = execute_query('SELECT COUNT(*) as count FROM findings')
print(f'Total findings: {findings[0][\"count\"] if findings else 0}')

# Breakdown by type
breakdown = execute_query('''
    SELECT problem_type, COUNT(*) as count 
    FROM findings 
    GROUP BY problem_type
''')
print('\nFindings by type:')
for item in breakdown:
    print(f'  - {item[\"problem_type\"]}: {item[\"count\"]}')

# Recent findings
recent = execute_query('''
    SELECT problem_type, details, found_date
    FROM findings
    ORDER BY found_date DESC
    LIMIT 5
''')
print('\nRecent findings:')
for item in recent:
    print(f'  - {item[\"problem_type\"]}: {item[\"details\"][:60]}...')
"
```

### Step 10: View Detailed Results

Query the database directly:

```bash
psql wikiverify -c "
SELECT 
    f.problem_type,
    f.severity,
    f.details,
    c.wikipedia_article,
    c.source_url
FROM findings f
JOIN citations c ON f.citation_id = c.id
ORDER BY f.found_date DESC
LIMIT 10;
"
```

## Complete E2E Test Script

Create a comprehensive test script:

```bash
#!/bin/bash
# Complete E2E test

cd /Users/rk/Documents/wiki/wiki-verify
source venv/bin/activate

echo "=== WikiVerify E2E Test ==="
echo ""

# Step 1: Verify setup
echo "Step 1: Verifying setup..."
python scripts/verify_setup.py || exit 1

# Step 2: Import test article
echo ""
echo "Step 2: Importing test article..."
python scripts/test_import.py Aspirin || exit 1

# Step 3: Run broken link agent
echo ""
echo "Step 3: Running Broken Link Agent..."
python -c "
from agents.broken_link_agent import BrokenLinkAgent
agent = BrokenLinkAgent()
agent.run(days=365, limit=5)
" || exit 1

# Step 4: Run retraction agent
echo ""
echo "Step 4: Running Retraction Agent..."
python -c "
from agents.retraction_agent import RetractionAgent
agent = RetractionAgent()
agent.run(update_cache=False, use_apis=False)
" || exit 1

# Step 5: Check results
echo ""
echo "Step 5: Checking results..."
python -c "
from core.database import execute_query
findings = execute_query('SELECT COUNT(*) as count FROM findings')
print(f'Total findings: {findings[0][\"count\"] if findings else 0}')
"

echo ""
echo "=== E2E Test Complete ==="
```

## Testing with Specific Scenarios

### Test 1: Broken Link Detection

```bash
# Import article with known broken links
python scripts/test_import.py "Article with old links"

# Run broken link agent
python -m agents.broken_link_agent

# Check for findings
psql wikiverify -c "SELECT * FROM findings WHERE problem_type = 'broken_link';"
```

### Test 2: Retraction Detection

```bash
# Import article with DOI citations
python scripts/test_import.py "Medical article with DOI"

# Update retraction cache
python -c "
from integrations.retraction_watch import RetractionWatch
rw = RetractionWatch()
rw.update_cache()
"

# Run retraction agent
python -m agents.retraction_agent
```

### Test 3: Source Change Detection

```bash
# Import article
python scripts/test_import.py "Article with web citations"

# Wait a bit, then run source change agent
# (This will create snapshots and check for changes)
python -m agents.source_change_agent
```

## Expected Results

After running the E2E test, you should see:

1. **Database populated** with citations
2. **Some findings** (depending on actual link status)
3. **Logs** showing agent activity
4. **No errors** in the output

## Troubleshooting

### "No citations found"
- Run: `python scripts/test_import.py Aspirin`
- Check: `psql wikiverify -c "SELECT COUNT(*) FROM citations;"`

### "Agent has no attribute 'client'"
- Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`
- Restart Python process

### "Database connection failed"
- Check PostgreSQL is running: `brew services list | grep postgresql`
- Verify `.env` file has correct `DATABASE_URL`

### "No findings created"
- This is normal if no problems are detected
- Try importing articles with older citations
- Check logs for any errors

## Next Steps

After successful E2E testing:

1. **Import more articles**: Edit `scripts/initial_import.py`
2. **Set up scheduler**: `python scripts/scheduler.py`
3. **Monitor findings**: Check database regularly
4. **Implement output**: Add Wikipedia bot (see `IMPLEMENTATION_PLAN.md`)

## Performance Testing

For larger scale testing:

```bash
# Import 10 articles
for article in "Aspirin" "Diabetes" "COVID-19" "Machine learning" "Python"; do
    python scripts/test_import.py "$article"
done

# Run agents on larger dataset
python -c "
from agents.broken_link_agent import BrokenLinkAgent
agent = BrokenLinkAgent()
agent.run(days=30, limit=1000)  # Check 1000 citations
"
```
