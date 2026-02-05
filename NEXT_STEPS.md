# Next Steps - Complete WikiVerify Setup

## ✅ What's Done

- ✅ PostgreSQL installed
- ✅ Database created and schema set up
- ✅ Project code implemented

## 🔧 What's Left

### Step 1: Install Python Dependencies

Run the complete setup script:

```bash
cd /Users/rk/Documents/wiki/wiki-verify
./complete_setup.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Create and configure `.env` file
- Verify the setup

### Step 2: Update .env File

After running the setup script, edit `.env` and update:

```bash
# Your email for Wikipedia API
WIKIPEDIA_USER_AGENT=WikiVerify/1.0 (your-email@example.com)

# Your email for PubMed API (recommended)
PUBMED_EMAIL=your-email@example.com

# Optional: OpenAI API key for LLM triage and enhanced explanations
OPENAI_API_KEY=your_key_here
```

### Step 3: Verify Everything Works

```bash
# Activate virtual environment
source venv/bin/activate

# Run verification
python scripts/verify_setup.py
```

### Step 4: Test the System

```bash
# Test importing an article
python scripts/test_import.py Aspirin

# Test running an agent
python -m agents.broken_link_agent

# Or test all agents
python scripts/scheduler.py --run-now
```

## 🎯 Quick Start Commands

```bash
cd /Users/rk/Documents/wiki/wiki-verify

# Complete setup
./complete_setup.sh

# Activate environment
source venv/bin/activate

# Verify
python scripts/verify_setup.py

# Test
python scripts/test_import.py Aspirin
```

## 📚 Documentation

- `README.md` - Project overview
- `QUICKSTART.md` - Quick start guide
- `SETUP_INSTRUCTIONS.md` - Detailed setup
- `DATABASE_SETUP.md` - Database setup guide

## 🐛 Troubleshooting

**"No module named 'dotenv'"**
- Run: `./complete_setup.sh` to install dependencies

**"Database connection failed"**
- Check PostgreSQL is running: `brew services list | grep postgresql`
- Verify database exists: `psql -l | grep wikiverify`
- Check `.env` file has correct DATABASE_URL

**"psql: command not found"**
- Add to PATH: `export PATH="/opt/homebrew/opt/postgresql@15/bin:$PATH"`
