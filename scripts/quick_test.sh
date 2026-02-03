#!/bin/bash
# Quick test script for WikiVerify

set -e

echo "WikiVerify Quick Test"
echo "===================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠ Virtual environment not activated."
    echo "  Run: source venv/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Verify setup
echo "Step 1: Verifying setup..."
python scripts/verify_setup.py
if [ $? -ne 0 ]; then
    echo ""
    echo "✗ Setup verification failed. Please fix issues above."
    exit 1
fi

echo ""
echo "Step 2: Testing article import..."
python scripts/test_import.py Aspirin

echo ""
echo "Step 3: Testing broken link agent (checking 5 citations)..."
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').absolute()))
from agents.broken_link_agent import BrokenLinkAgent
agent = BrokenLinkAgent()
agent.run(days=365, limit=5)
"

echo ""
echo "===================="
echo "✓ Quick test complete!"
echo ""
echo "Next steps:"
echo "  - Import more articles: python scripts/initial_import.py"
echo "  - Run all agents: python scripts/scheduler.py --run-now"
echo "  - Start scheduler: python scripts/scheduler.py"
