# Installing PostgreSQL for WikiVerify

## Quick Installation (macOS)

Run the installation script:

```bash
cd wiki-verify
./install_postgresql.sh
```

## Manual Installation

### Option 1: Using Homebrew (Recommended)

```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Add to PATH (add to ~/.zshrc for permanent)
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
```

### Option 2: Using Postgres.app

1. Download from https://postgresapp.com/
2. Install and launch the app
3. Click "Initialize" to create a new server
4. PostgreSQL will be available at `localhost:5432`

### Option 3: Using Docker

```bash
cd wiki-verify
docker-compose up -d
```

This will start PostgreSQL in a Docker container.

## Verify Installation

```bash
# Check if PostgreSQL is installed
psql --version

# Check if service is running
pg_isready

# Or for Homebrew
brew services list | grep postgresql
```

## After Installation

1. **Create the database:**
   ```bash
   createdb wikiverify
   ```

2. **Set up the schema:**
   ```bash
   cd wiki-verify
   psql wikiverify < schema.sql
   ```

3. **Or use the setup script:**
   ```bash
   ./setup_database.sh
   ```

## Troubleshooting

### "psql: command not found"

Add PostgreSQL to your PATH:

```bash
# For Homebrew on Apple Silicon
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"

# For Homebrew on Intel
export PATH="/usr/local/opt/postgresql@15/bin:$PATH"

# Add to ~/.zshrc for permanent
echo 'export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### "Connection refused"

Start the PostgreSQL service:

```bash
# Homebrew
brew services start postgresql@15

# Or manually
pg_ctl -D /opt/homebrew/var/postgresql@15 start
```

### "Database does not exist"

Create it:

```bash
createdb wikiverify
```

### Permission Issues

If you get permission errors, you may need to create a PostgreSQL user:

```bash
# Connect as superuser
psql postgres

# Create user and database
CREATE USER wikiverify WITH PASSWORD 'wikiverify';
CREATE DATABASE wikiverify OWNER wikiverify;
\q
```

Then update your `.env` file:
```
DATABASE_URL=postgresql://wikiverify:wikiverify@localhost:5432/wikiverify
```

## Next Steps

Once PostgreSQL is installed and running:

1. Run: `python scripts/verify_setup.py` to verify everything works
2. Test import: `python scripts/test_import.py Aspirin`
3. Start using WikiVerify!
