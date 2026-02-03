#!/bin/bash
# Quick E2E test runner script

set -e

cd "$(dirname "$0")/.."

echo "WikiVerify E2E Test Runner"
echo "============================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠ Virtual environment not activated."
    echo "  Activating virtual environment..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "❌ Virtual environment not found. Run: python -m venv venv"
        exit 1
    fi
fi

# Run the E2E test
echo "Running E2E test suite..."
echo ""
python scripts/e2e_test.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ E2E test completed successfully!"
else
    echo ""
    echo "❌ E2E test failed. Check the output above for details."
fi

exit $exit_code
