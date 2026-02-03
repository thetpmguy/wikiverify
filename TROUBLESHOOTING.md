# Troubleshooting Guide

## Common Issues and Solutions

### HTTP Timeout Errors

**Symptom:**
```
HTTP HEAD error for https://example.com: Read timed out. (read timeout=10)
```

**Explanation:**
This is **normal behavior**, not an error. Some websites are slow to respond or may be temporarily unavailable. The system logs these as debug messages (not errors) because they're expected when checking thousands of URLs.

**Solution:**
- These are handled gracefully - the system marks the URL as inaccessible
- If you see too many timeouts, you can increase the timeout in `.env`:
  ```bash
  CHECK_TIMEOUT=20  # Increase from default 15 to 20 seconds
  ```
- Timeouts are logged at DEBUG level, so they won't appear unless you set logging to DEBUG

### Too Many Timeout Messages

If you're seeing too many timeout messages in logs:

1. **Increase timeout** (if you have slow network):
   ```bash
   # In .env file
   CHECK_TIMEOUT=20
   ```

2. **Reduce log verbosity** (timeouts are logged at DEBUG level):
   ```python
   # In your script
   import logging
   logging.getLogger().setLevel(logging.INFO)  # Only show INFO and above
   ```

3. **This is expected**: When checking many URLs, some will timeout. The system handles this correctly.

### Database Connection Errors

**Symptom:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
1. Check PostgreSQL is running:
   ```bash
   brew services list | grep postgresql
   ```

2. Start PostgreSQL if not running:
   ```bash
   brew services start postgresql@15
   ```

3. Verify database exists:
   ```bash
   psql -l | grep wikiverify
   ```

4. Check `.env` file has correct `DATABASE_URL`

### "Agent has no attribute 'client'"

**Symptom:**
```
AttributeError: 'BrokenLinkAgent' object has no attribute 'client'
```

**Solution:**
1. Clear Python cache:
   ```bash
   find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
   find . -name "*.pyc" -delete 2>/dev/null || true
   ```

2. Restart your Python process/script

3. Make sure you're using the latest code (after refactoring)

### No Citations Found

**Symptom:**
```
Found 0 citations
```

**Solution:**
1. Import articles first:
   ```bash
   python scripts/test_import.py Aspirin
   ```

2. Check database:
   ```bash
   psql wikiverify -c "SELECT COUNT(*) FROM citations;"
   ```

3. Some articles may not have citations (this is normal)

### No Findings Created

**Symptom:**
```
Completed: Checked 10 citations, found 0 broken links
```

**Explanation:**
This is **good news** - it means no problems were detected! The system only creates findings when it finds actual issues.

**To test findings:**
- Import articles with older citations
- Check URLs that are known to be broken
- The system will create findings when problems are detected

### Import Errors

**Symptom:**
```
Error fetching article: ...
```

**Solution:**
1. Check internet connection
2. Verify article title is correct (case-sensitive)
3. Check Wikipedia API rate limiting (1 request/second)
4. Some articles may not exist or be deleted

### LLM Triage Errors

**Symptom:**
```
Warning: openai package not installed. LLM triage disabled.
```

**Solution:**
1. This is optional - agents work without LLM triage
2. To enable, install OpenAI package:
   ```bash
   pip install openai
   ```
3. Add API key to `.env`:
   ```bash
   OPENAI_API_KEY=your_key_here
   ```

### Rate Limiting Issues

**Symptom:**
Slow performance or API errors

**Solution:**
1. The system automatically rate limits (1 request/second by default)
2. You can adjust in `.env`:
   ```bash
   RATE_LIMIT_DELAY=2  # Increase delay between requests
   ```
3. Be respectful of external APIs - don't reduce too much

### Logging Too Verbose

**Symptom:**
Too many log messages

**Solution:**
1. Set log level to INFO:
   ```python
   import logging
   logging.getLogger().setLevel(logging.INFO)
   ```

2. Or in your script:
   ```python
   from core.logger import setup_logger
   logger = setup_logger(__name__, level=logging.INFO)
   ```

### Performance Issues

**Symptom:**
Agents running very slowly

**Solution:**
1. Reduce the number of citations checked:
   ```python
   agent.run(limit=100)  # Instead of 1000
   ```

2. Increase rate limit delay (if hitting API limits):
   ```bash
   RATE_LIMIT_DELAY=2
   ```

3. Check network connection speed

### PostgreSQL Not Found

**Symptom:**
```
psql: command not found
```

**Solution:**
1. Add PostgreSQL to PATH:
   ```bash
   export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
   ```

2. Or use full path:
   ```bash
   /opt/homebrew/opt/postgresql@15/bin/psql ...
   ```

## Getting Help

If you encounter issues not covered here:

1. Check the logs: `wiki-verify.log`
2. Run verification: `python scripts/verify_setup.py`
3. Check database: `psql wikiverify -c "SELECT COUNT(*) FROM citations;"`
4. Review error messages - they usually indicate what's wrong

## Debug Mode

To see more detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show all debug messages including timeouts and connection attempts.
