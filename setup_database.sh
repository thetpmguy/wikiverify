#!/bin/bash
# Database setup script for WikiVerify

set -e

echo "WikiVerify Database Setup"
echo "=========================="
echo ""

# Add PostgreSQL to PATH if not already there
if ! command -v psql &> /dev/null; then
    # Try to find PostgreSQL installation
    if [ -d "/opt/homebrew/opt/postgresql@15/bin" ]; then
        export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
        echo "✓ Added PostgreSQL@15 to PATH"
    elif [ -d "/usr/local/opt/postgresql@15/bin" ]; then
        export PATH="/usr/local/opt/postgresql@15/bin:$PATH"
        echo "✓ Added PostgreSQL@15 to PATH"
    elif [ -d "/opt/homebrew/opt/postgresql/bin" ]; then
        export PATH="/opt/homebrew/opt/postgresql/bin:$PATH"
        echo "✓ Added PostgreSQL to PATH"
    elif [ -d "/usr/local/opt/postgresql/bin" ]; then
        export PATH="/usr/local/opt/postgresql/bin:$PATH"
        echo "✓ Added PostgreSQL to PATH"
    fi
fi

# Check if PostgreSQL is available
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL client found: $(which psql)"
    psql --version
else
    echo "✗ PostgreSQL client not found. Please install PostgreSQL."
    echo "  Or add PostgreSQL bin directory to your PATH"
    exit 1
fi

# Check if database exists
DB_NAME="wikiverify"
DB_USER="${DB_USER:-wikiverify}"
DB_PASSWORD="${DB_PASSWORD:-wikiverify}"
DB_HOST="${DB_HOST:-localhost}"

echo ""
echo "Setting up database: $DB_NAME"
echo "User: $DB_USER"
echo "Host: $DB_HOST"
echo ""

# Try to connect and create database if it doesn't exist
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1; then
    echo "✓ Database '$DB_NAME' already exists"
else
    echo "Creating database '$DB_NAME'..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME" || {
        echo "Error: Could not create database. Trying without password..."
        psql -h $DB_HOST -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME" || {
            echo "Error: Please create the database manually:"
            echo "  createdb $DB_NAME"
            exit 1
        }
    }
    echo "✓ Database created"
fi

# Run schema
echo ""
echo "Setting up schema..."
if [ -f "schema.sql" ]; then
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f schema.sql || {
        echo "Trying without password..."
        psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f schema.sql || {
            echo "Error: Could not run schema. Please run manually:"
            echo "  psql $DB_NAME < schema.sql"
            exit 1
        }
    }
    echo "✓ Schema created"
else
    echo "✗ schema.sql not found!"
    exit 1
fi

echo ""
echo "=========================="
echo "✓ Database setup complete!"
echo ""
echo "Update your .env file with:"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:5432/$DB_NAME"
