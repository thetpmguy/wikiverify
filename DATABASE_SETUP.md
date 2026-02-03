# Database Setup Instructions

PostgreSQL is installed but the server needs to be started. Run these commands in your terminal:

## Quick Setup

```bash
cd /Users/rk/Documents/wiki/wiki-verify

# Start PostgreSQL service
brew services start postgresql@15

# Wait a few seconds, then run the setup script
./start_and_setup.sh
```

## Manual Setup

If you prefer to do it manually:

```bash
# 1. Add PostgreSQL to PATH (for this session)
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# 2. Start PostgreSQL service
brew services start postgresql@15

# 3. Wait a few seconds, then verify it's running
pg_isready

# 4. Create database
createdb wikiverify

# 5. Set up schema
psql wikiverify < schema.sql

# 6. Verify tables were created
psql wikiverify -c "\dt"
```

## Update .env File

After the database is set up, update your `.env` file:

```bash
# For default PostgreSQL setup (no password)
DATABASE_URL=postgresql://$(whoami)@localhost:5432/wikiverify

# Or if you created a user with password
DATABASE_URL=postgresql://wikiverify:wikiverify@localhost:5432/wikiverify
```

## Verify Setup

```bash
python scripts/verify_setup.py
```

This will check:
- ✓ All imports work
- ✓ Configuration is set
- ✓ Database connection works
- ✓ Database schema exists

## Troubleshooting

### "PostgreSQL service not running"

```bash
brew services start postgresql@15
# Wait a few seconds
pg_isready
```

### "Permission denied" errors

Make sure PostgreSQL is running:
```bash
brew services list | grep postgresql
```

### "psql: command not found"

Add PostgreSQL to your PATH:
```bash
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

To make it permanent, add to `~/.zshrc`:
```bash
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```
