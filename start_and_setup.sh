#!/bin/bash
# Start PostgreSQL and set up WikiVerify database

set -e

echo "WikiVerify Database Setup"
echo "=========================="
echo ""

# Add PostgreSQL to PATH
if [ -d "/opt/homebrew/opt/postgresql@15/bin" ]; then
    export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
elif [ -d "/usr/local/opt/postgresql@15/bin" ]; then
    export PATH="/usr/local/opt/postgresql@15/bin:$PATH"
fi

# Check if PostgreSQL service is running
if ! pg_isready &> /dev/null; then
    echo "Starting PostgreSQL service..."
    brew services start postgresql@15 || brew services start postgresql
    echo "Waiting for PostgreSQL to start..."
    sleep 3
    
    # Check again
    if ! pg_isready &> /dev/null; then
        echo "⚠ PostgreSQL may not be running. Please start it manually:"
        echo "  brew services start postgresql@15"
        exit 1
    fi
fi

echo "✓ PostgreSQL is running"
echo ""

# Create database
echo "Creating database 'wikiverify'..."
createdb wikiverify 2>&1 || {
    if psql -lqt | cut -d \| -f 1 | grep -qw wikiverify; then
        echo "✓ Database 'wikiverify' already exists"
    else
        echo "✗ Failed to create database"
        exit 1
    fi
}

# Set up schema
echo ""
echo "Setting up database schema..."
psql wikiverify < schema.sql

echo ""
echo "Verifying schema..."
TABLE_COUNT=$(psql wikiverify -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)
echo "✓ Found $TABLE_COUNT tables in database"

echo ""
echo "=========================="
echo "✓ Database setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update .env file with: DATABASE_URL=postgresql://$(whoami)@localhost:5432/wikiverify"
echo "  2. Run: python scripts/verify_setup.py"
echo "  3. Test: python scripts/test_import.py Aspirin"
