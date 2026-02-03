#!/bin/bash
# Script to push WikiVerify to GitHub

set -e

cd "$(dirname "$0")/.."

echo "WikiVerify - Push to GitHub"
echo "============================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
    echo "✅ Git initialized"
fi

# Check if .env exists and warn
if [ -f .env ]; then
    if ! git check-ignore .env > /dev/null 2>&1; then
        echo "⚠️  WARNING: .env file is not in .gitignore!"
        echo "   This file may contain sensitive data."
        read -p "   Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Get GitHub info
echo ""
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter repository name (default: wiki-verify): " REPO_NAME
REPO_NAME=${REPO_NAME:-wiki-verify}

# Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    CURRENT_REMOTE=$(git remote get-url origin)
    echo ""
    echo "Current remote: $CURRENT_REMOTE"
    read -p "Update remote? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
        git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        echo "✅ Remote updated"
    fi
else
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "✅ Remote added"
fi

# Add all files
echo ""
echo "Adding files to git..."
git add .

# Show status
echo ""
echo "Files to be committed:"
git status --short | head -20
if [ $(git status --short | wc -l) -gt 20 ]; then
    echo "... and more"
fi

# Commit
echo ""
read -p "Commit message (press Enter for default): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Initial commit: WikiVerify - Automated Wikipedia citation verification system

Features:
- Broken Link Agent: Detects inaccessible citation URLs
- Retraction Agent: Identifies retracted scientific papers  
- Source Change Agent: Monitors source content changes
- LLM Triage: Filters false positives using GPT-4o-mini
- Comprehensive testing and documentation"}

git commit -m "$COMMIT_MSG"
echo "✅ Committed"

# Push
echo ""
echo "Pushing to GitHub..."
echo "Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

if git push -u origin main; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "Next steps:"
    echo "  1. Visit your repository on GitHub"
    echo "  2. Add a description and topics"
    echo "  3. Consider adding a LICENSE file"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "  1. Repository doesn't exist on GitHub - create it first"
    echo "  2. Authentication failed - check your credentials"
    echo "  3. Network issues - check your connection"
    echo ""
    echo "To create the repository, go to:"
    echo "  https://github.com/new"
    echo ""
    echo "Repository name: $REPO_NAME"
    echo "DO NOT initialize with README, .gitignore, or license"
    exit 1
fi
