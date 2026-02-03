#!/bin/bash
# PostgreSQL Installation Script for macOS

set -e

echo "PostgreSQL Installation for WikiVerify"
echo "======================================="
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "✗ Homebrew not found. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "✓ Homebrew found"
echo ""

# Check if PostgreSQL is already installed
if brew list postgresql@15 &> /dev/null || brew list postgresql &> /dev/null; then
    echo "✓ PostgreSQL appears to be installed via Homebrew"
    POSTGRES_INSTALLED=true
else
    echo "Installing PostgreSQL..."
    brew install postgresql@15
    POSTGRES_INSTALLED=false
fi

echo ""
echo "Setting up PostgreSQL service..."

# Start PostgreSQL service
if [ "$POSTGRES_INSTALLED" = false ]; then
    echo "Starting PostgreSQL service..."
    brew services start postgresql@15
    sleep 3  # Give it time to start
fi

# Check if service is running
if brew services list | grep -q "postgresql.*started"; then
    echo "✓ PostgreSQL service is running"
else
    echo "Starting PostgreSQL service..."
    brew services start postgresql@15 || brew services start postgresql
    sleep 3
fi

# Add PostgreSQL to PATH (for this session)
export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"
export PATH="/usr/local/opt/postgresql@15/bin:$PATH"

# Check if psql is available
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL client (psql) is available"
    psql --version
else
    echo "⚠ psql not found in PATH. You may need to add it:"
    echo "  export PATH=\"/opt/homebrew/opt/postgresql@15/bin:\$PATH\""
    echo "  Or add to ~/.zshrc or ~/.bash_profile"
fi

echo ""
echo "======================================="
echo "PostgreSQL Installation Complete!"
echo ""
echo "Next steps:"
echo "  1. Create database: createdb wikiverify"
echo "  2. Set up schema: psql wikiverify < schema.sql"
echo "  3. Or run: ./setup_database.sh"
echo ""
