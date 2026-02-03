# Push to GitHub Guide

Follow these steps to push WikiVerify to GitHub.

## Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right → "New repository"
3. Repository name: `wiki-verify` (or your preferred name)
4. Description: "Automated Wikipedia citation verification system"
5. Choose **Public** or **Private**
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

## Step 2: Initialize Git (if not already done)

```bash
cd /Users/rk/Documents/wiki/wiki-verify

# Check if git is initialized
if [ ! -d .git ]; then
    git init
    git branch -M main
fi
```

## Step 3: Add and Commit Files

```bash
cd /Users/rk/Documents/wiki/wiki-verify

# Add all files
git add .

# Check what will be committed
git status

# Commit
git commit -m "Initial commit: WikiVerify - Automated Wikipedia citation verification system

Features:
- Broken Link Agent: Detects inaccessible citation URLs
- Retraction Agent: Identifies retracted scientific papers
- Source Change Agent: Monitors source content changes
- LLM Triage: Filters false positives using GPT-4o-mini
- Comprehensive testing and documentation"
```

## Step 4: Add GitHub Remote

Replace `YOUR_USERNAME` with your GitHub username:

```bash
git remote add origin https://github.com/YOUR_USERNAME/wiki-verify.git
```

Or if you prefer SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/wiki-verify.git
```

## Step 5: Push to GitHub

```bash
# Push to main branch
git push -u origin main
```

If you get an error about authentication, you may need to:
- Use a Personal Access Token (for HTTPS)
- Set up SSH keys (for SSH)

## Complete Script

Here's a complete script you can run:

```bash
#!/bin/bash
# Push WikiVerify to GitHub

cd /Users/rk/Documents/wiki/wiki-verify

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter repository name (default: wiki-verify): " REPO_NAME
REPO_NAME=${REPO_NAME:-wiki-verify}

# Initialize git if needed
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "Adding files..."
git add .

# Check status
echo ""
echo "Files to be committed:"
git status --short

# Commit
read -p "Commit message (press Enter for default): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Initial commit: WikiVerify - Automated Wikipedia citation verification system"}
git commit -m "$COMMIT_MSG"

# Add remote
echo ""
echo "Adding GitHub remote..."
git remote remove origin 2>/dev/null
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

# Push
echo ""
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Done! Your repository is at: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
```

## Alternative: Manual Steps

If you prefer to do it manually:

### 1. Check current status
```bash
cd /Users/rk/Documents/wiki/wiki-verify
git status
```

### 2. Add files
```bash
git add .
```

### 3. Commit
```bash
git commit -m "Initial commit: WikiVerify"
```

### 4. Add remote (replace YOUR_USERNAME)
```bash
git remote add origin https://github.com/YOUR_USERNAME/wiki-verify.git
```

### 5. Push
```bash
git push -u origin main
```

## Troubleshooting

### "Repository not found"
- Make sure you created the repository on GitHub first
- Check the repository name matches
- Verify your GitHub username is correct

### "Authentication failed"
- For HTTPS: Use a Personal Access Token instead of password
  - Go to GitHub Settings → Developer settings → Personal access tokens
  - Generate a token with `repo` permissions
  - Use token as password when prompted
- For SSH: Set up SSH keys
  ```bash
  ssh-keygen -t ed25519 -C "your_email@example.com"
  # Then add to GitHub Settings → SSH and GPG keys
  ```

### "Remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/wiki-verify.git
```

### "Failed to push some refs"
```bash
# If GitHub repo has files (README, etc.), pull first:
git pull origin main --allow-unrelated-histories
# Then push:
git push -u origin main
```

## What Gets Pushed

The `.gitignore` file ensures these are **NOT** pushed:
- `venv/` - Virtual environment
- `.env` - Environment variables (sensitive data)
- `__pycache__/` - Python cache files
- `*.log` - Log files
- `*.pyc` - Compiled Python files

## After Pushing

1. **Add a README badge** (optional):
   ```markdown
   ![License](https://img.shields.io/badge/license-MIT-blue.svg)
   ```

2. **Add topics/tags** on GitHub:
   - `wikipedia`
   - `citation-verification`
   - `python`
   - `automation`
   - `ai`

3. **Add a license** (if you want):
   - Create `LICENSE` file
   - MIT, Apache 2.0, or GPL are common choices

4. **Enable GitHub Actions** (optional):
   - For CI/CD
   - Automated testing

## Security Notes

⚠️ **Important**: Make sure `.env` is in `.gitignore` (it should be)

Before pushing, verify:
```bash
git check-ignore .env
# Should output: .env
```

If it doesn't, your `.env` file might be committed. Remove it:
```bash
git rm --cached .env
git commit -m "Remove .env from tracking"
```

## Next Steps

After pushing:
1. Share the repository link
2. Add collaborators (if needed)
3. Set up GitHub Actions for CI/CD
4. Add issues and project boards
5. Create releases for versions
