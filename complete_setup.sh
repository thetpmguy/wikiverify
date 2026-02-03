#!/bin/bash
# Complete WikiVerify Setup Script
# Run this after PostgreSQL is installed and database is set up

set -e

echo "WikiVerify Complete Setup"
echo "========================"
echo ""

cd "$(dirname "$0")"

# Step 1: Create virtual environment
echo "Step 1: Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Step 2: Activate and install dependencies
echo ""
echo "Step 2: Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Step 3: Create .env file
echo ""
echo "Step 3: Setting up .env file..."
if [ ! -f ".env" ]; then
    cp env_template.txt .env
    
    # Update DATABASE_URL with current username
    USERNAME=$(whoami)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - use sed with backup
        sed -i '' "s|postgresql://wikiverify:wikiverify@localhost:5432/wikiverify|postgresql://$USERNAME@localhost:5432/wikiverify|g" .env
    else
        sed -i "s|postgresql://wikiverify:wikiverify@localhost:5432/wikiverify|postgresql://$USERNAME@localhost:5432/wikiverify|g" .env
    fi
    
    echo "✓ .env file created with database URL: postgresql://$USERNAME@localhost:5432/wikiverify"
    echo ""
    echo "⚠ Please update .env file with:"
    echo "  - Your email for WIKIPEDIA_USER_AGENT"
    echo "  - Your email for PUBMED_EMAIL (recommended)"
    echo "  - OPENAI_API_KEY (optional, for Evidence Agent)"
else
    echo "✓ .env file already exists"
fi

# Step 4: Verify setup
echo ""
echo "Step 4: Verifying setup..."
python scripts/verify_setup.py

echo ""
echo "========================"
echo "Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Test import: python scripts/test_import.py Aspirin"
echo "  3. Run an agent: python -m agents.broken_link_agent"
echo "  4. Or run all agents: python scripts/scheduler.py --run-now"
echo ""
