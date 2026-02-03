#!/bin/bash
# Add PostgreSQL to PATH for WikiVerify setup

# Detect PostgreSQL installation path
if [ -d "/opt/homebrew/opt/postgresql@15/bin" ]; then
    export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
    echo "✓ Added PostgreSQL@15 to PATH (Apple Silicon)"
elif [ -d "/usr/local/opt/postgresql@15/bin" ]; then
    export PATH="/usr/local/opt/postgresql@15/bin:$PATH"
    echo "✓ Added PostgreSQL@15 to PATH (Intel)"
elif [ -d "/opt/homebrew/opt/postgresql/bin" ]; then
    export PATH="/opt/homebrew/opt/postgresql/bin:$PATH"
    echo "✓ Added PostgreSQL to PATH (Apple Silicon)"
elif [ -d "/usr/local/opt/postgresql/bin" ]; then
    export PATH="/usr/local/opt/postgresql/bin:$PATH"
    echo "✓ Added PostgreSQL to PATH (Intel)"
else
    echo "⚠ PostgreSQL not found in standard locations"
    echo "Please add PostgreSQL bin directory to your PATH manually"
    exit 1
fi

# Verify psql is available
if command -v psql &> /dev/null; then
    echo "✓ psql is now available"
    psql --version
    echo ""
    echo "Now you can run:"
    echo "  createdb wikiverify"
    echo "  psql wikiverify < schema.sql"
else
    echo "✗ psql still not found. Please check your PostgreSQL installation."
    exit 1
fi
