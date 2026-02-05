# WikiVerify Architecture

## Overview

WikiVerify is a system of automated agents that monitor Wikipedia citations for problems. The system uses a combination of ML models for detection, external APIs for data collection, and LLMs for generating human readable notifications. It operates on a periodic schedule with three distinct cycles: monthly data updates, weekly citation imports, and daily verification runs.

## Architecture Principles

1. **Local First**: All daily verification uses local data only. External APIs are called only during scheduled data refresh cycles.
2. **Separation of Concerns**: Checkers perform detection logic. Agents orchestrate workflows and make decisions. Models provide specific capabilities.
3. **Graceful Degradation**: If one model or data source is unavailable, the system continues with reduced capability rather than crashing.
4. **Batch Processing**: Everything runs in periodic batches, not real time. This keeps infrastructure simple and costs low.
5. **DRY**: Shared utilities eliminate code duplication across agents and integrations.
6. **Type Safety**: Type hints throughout. Constants module for magic values.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         MONTHLY CYCLE                                │
│                                                                      │
│   CrossRef API ──┐                                                   │
│                  ├──► download_retraction_database.py                 │
│   PubMed API ────┘           │                                       │
│                              ▼                                       │
│                   retraction_database_combined.json                   │
│                              │                                       │
│                              ▼                                       │
│                   precompute_embeddings.py                            │
│                              │                                       │
│                              ▼                                       │
│                   retraction_embeddings.pkl                           │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                         WEEKLY CYCLE                                 │
│                                                                      │
│   Wikipedia API ──► initial_import.py ──► PostgreSQL Database        │
│                     (finds new/changed      (citations table)        │
│                      citations)                                      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                          DAILY CYCLE                                 │
│                                                                      │
│   PostgreSQL ──► Synthesizer Agent ──► Retraction Checker            │
│   (unchecked       (orchestrator)       (detection logic)            │
│    citations)          │                     │                       │
│                        │                     ├── Citation Extractor   │
│                        │                     ├── Paper Matcher        │
│                        │                     └── Severity Classifier  │
│                        │                                             │
│                        ▼                                             │
│                   LLM (notification text) ──► findings table         │
│                                                                      │
│   No external API calls. Everything uses local data and models.      │
│   Only exception: LLM call for generating notification text.         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
wiki-verify/
├── agents/
│   ├── base_agent.py              # Abstract base class for all agents
│   └── synthesizer_agent.py       # Orchestrates retraction checking and notifications
│
├── core/
│   ├── config.py                  # Configuration management
│   ├── constants.py               # Constants and enums (ProblemType, Severity)
│   ├── database.py                # Database operations with context manager
│   ├── logger.py                  # Structured logging system
│   ├── parser.py                  # Wikipedia citation parsing
│   └── utils.py                   # Shared HTTP client, rate limiter
│
├── integrations/
│   ├── crossref.py                # CrossRef API client
│   ├── pubmed.py                  # PubMed API client
│   ├── retraction_watch.py        # Retraction Watch integration
│   └── wikipedia_api.py           # Wikipedia API client
│
├── ml/
│   ├── citation_extractor.py      # Loads and runs NER model (Model A)
│   ├── paper_matcher.py           # Loads sentence transformer + embeddings (Model C)
│   └── severity_classifier.py     # Loads and runs severity model (Model B)
│
├── checkers/
│   └── retraction_checker.py      # Main retraction checking logic
│
├── llm/
│   └── llm_triage.py              # LLM integration for triage and notifications
│
├── models/
│   ├── citation_extractor/        # Trained SciBERT NER model (~400 MB)
│   │   ├── config.json
│   │   ├── model.safetensors
│   │   └── tokenizer files
│   ├── severity_classifier/       # Trained DistilBERT classifier (~250 MB)
│   │   ├── config.json
│   │   ├── model.safetensors
│   │   └── tokenizer files
│   └── retraction_embeddings.pkl  # Precomputed embeddings (~50-100 MB)
│
├── training/
│   ├── train_citation_extractor.ipynb   # Colab notebook for Model A
│   ├── train_severity_classifier.ipynb  # Colab notebook for Model B
│   └── data/
│       ├── retraction_database_combined.json  # 40,000 retracted papers
│       ├── ner_train.json                     # NER training examples
│       └── severity_train.json                # Severity training examples
│
├── output/
│   ├── formatters.py              # Output formatting for findings
│   └── wiki_bot.py                # Wikipedia Talk page bot (future)
│
├── scripts/
│   ├── initial_import.py                      # Import Wikipedia articles
│   ├── download_retraction_database.py        # Download retractions from APIs
│   ├── precompute_retraction_embeddings.py    # Generate embeddings file
│   ├── build_ner_dataset.py                   # Build NER training data
│   └── scheduler.py                           # Runs all cycles on schedule
│
├── tests/
│   ├── test_retraction_checker.py
│   ├── test_citation_extractor.py
│   ├── test_paper_matcher.py
│   └── test_severity_classifier.py
│
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## ML Models

### Model A: Citation Entity Extractor

**Purpose:** Extract structured fields (title, authors, journal, year, DOI) from messy unstructured citation text.

**Base model:** SciBERT (BERT pretrained on scientific papers), fine tuned for Named Entity Recognition.

**Training required:** Yes. Trained on your own Wikipedia citations database. Clean template citations provide the labeled examples automatically. The raw text is the input, the structured fields are the labels.

**Training location:** Google Colab (free GPU). Takes 15 to 30 minutes.

**Training data:** 2,000 to 5,000 labeled citation examples, generated automatically from your PostgreSQL database by `scripts/build_ner_dataset.py`.

**Model size:** ~400 MB on disk. Stored in `models/citation_extractor/`.

**When it is used:** Only during the daily run, only for citations that have no DOI and no structured fields. If a citation already has a DOI, this model is skipped entirely.

```
Input:  "According to Wakefield et al. (1998) in The Lancet,
         MMR vaccine was linked to autism"

Output: {
    "author": "Wakefield",
    "year": "1998",
    "journal": "The Lancet",
    "title": "MMR vaccine linked to autism"
}
```

### Model B: Retraction Severity Classifier

**Purpose:** Read a retraction notice and classify how serious the retraction is.

**Base model:** DistilBERT, fine tuned for text classification with four severity levels.

**Training required:** Yes. Trained on Retraction Watch reason codes mapped to severity levels.

**Training location:** Google Colab (free GPU). Takes 5 to 15 minutes.

**Training data:** 1,000 to 3,000 retraction notices with severity labels, derived from Retraction Watch reason codes by a simple mapping script.

**Model size:** ~250 MB on disk. Stored in `models/severity_classifier/`.

**Severity categories:**

```
critical:   Fabrication, fraud, data manipulation
major:      Methodology errors, unreliable results, statistical errors
minor:      Authorship disputes, duplication, copyright issues
corrected:  Paper replaced with corrected version
```

**When it is used:** Only during the daily run, only for citations confirmed to be retracted. If a citation is not retracted, this model is never called.

### Model C: Sentence Transformer (Paper Matcher)

**Purpose:** Convert text into 384 dimensional embeddings (arrays of numbers) that represent meaning. Used to match citations against retracted papers when no DOI is available.

**Base model:** all-MiniLM-L6-v2 from HuggingFace. Pretrained on millions of text pairs.

**Training required:** No. Downloaded and used as is. No fine tuning needed.

**Model size:** ~80 MB on disk. Downloaded automatically from HuggingFace on first use.

**Precomputed data:** All 40,000 retracted papers are converted to embeddings once per month and saved to `models/retraction_embeddings.pkl` (~50 to 100 MB). This file is loaded into memory at startup and used for fast comparison.

**When it is used:** Only during the daily run, only for citations that have no DOI. The citation text is converted to 384 numbers and compared against all 40,000 precomputed embeddings using cosine similarity. A score above 0.85 indicates a match.

```
Citation: "MMR vaccine linked to autism Wakefield Lancet 1998"
    → [0.23, -0.15, 0.87, 0.44, -0.32, 0.91, ...]

Paper #7,842: "Ileal-lymphoid-nodular hyperplasia..."
    → [0.21, -0.18, 0.85, 0.42, -0.29, 0.89, ...]

Cosine similarity: 0.91 → MATCH (above 0.85 threshold)
```

---

## Component Relationships

### Checker vs Agent

A **checker** is a function. It takes input, produces output, makes no decisions about what to do with the output. It has no autonomy.

An **agent** is an orchestrator. It decides what to check, when to check it, what to do with findings, and how to communicate results. It has decision making logic.

```
Retraction Checker (function):
    Input: one citation
    Output: {is_retracted: true/false, details: {...}}
    Does not decide what happens next.

Synthesizer Agent (agent):
    Decides which citations to check (queries database)
    Calls the retraction checker for each one
    Decides whether to generate a notification
    Calls the LLM to write the notification
    Saves findings to the database
    Decides when to run again
```

### Model Loading

All three ML models are loaded once at startup and stay in memory for the entire daily run. They are not reloaded for each citation.

```
Startup (30-60 seconds):
    Load Model A into RAM (~400 MB)
    Load Model C into RAM (~80 MB)
    Load precomputed embeddings into RAM (~80 MB)
    Load Model B into RAM (~250 MB)
    Total RAM: ~850 MB

Per citation (milliseconds):
    Models are already in memory
    Just run the input through them
    No disk access, no downloads, no waiting
```

---

## Data Flow: Daily Run

### Flow 1: Citation HAS a DOI

This is the fast path. No ML models are used.

```
Citation with DOI "10.1234/lancet.2019.456"
    │
    ▼
Search local retraction database file
(loop through 40,000 entries, compare DOI strings)
    │
    ├── DOI found → Paper is retracted
    │       │
    │       ▼
    │   Severity Classifier (Model B)
    │   reads the retraction notice text
    │   outputs: critical / major / minor / corrected
    │       │
    │       ▼
    │   Return structured result to synthesizer
    │
    └── DOI not found → Paper is not retracted
            │
            ▼
        Return {is_retracted: false}
```

**Time per citation:** Under 1 second. Just a string comparison against a local file.

### Flow 2: Citation has NO DOI

This is the complex path. All three ML models may be used.

```
Messy citation text with no DOI
    │
    ▼
Citation Entity Extractor (Model A)
reads the messy text, extracts:
    author, year, journal, title
    │
    ▼
Build search query from extracted fields:
"MMR vaccine linked to autism Wakefield The Lancet 1998"
    │
    ▼
Sentence Transformer (Model C)
converts search query to 384 numbers:
[0.23, -0.15, 0.87, 0.44, -0.32, ...]
    │
    ▼
Compare against 40,000 precomputed embeddings
(cosine similarity, pure math, takes 0.01 seconds)
    │
    ▼
Find highest scoring match
    │
    ├── Score > 0.85 → Match found, paper is retracted
    │       │
    │       ▼
    │   Severity Classifier (Model B)
    │   classifies the retraction severity
    │       │
    │       ▼
    │   Return structured result to synthesizer
    │
    └── Score < 0.85 → No match, not retracted
            │
            ▼
        Return {is_retracted: false}
```

**Time per citation:** About 0.3 seconds for the ML processing.

### After checking: Notification Generation

When the synthesizer receives a positive result (paper is retracted), it generates a notification.

```
Structured result from retraction checker
    │
    ▼
Synthesizer builds an LLM prompt containing:
    article name, paper details, retraction reason,
    severity, confidence score, match method
    │
    ▼
LLM generates human readable notification text
(this is the only external API call in the daily run)
    │
    ▼
Synthesizer saves everything to the findings table:
    citation_id, problem_type, severity,
    confidence, details, notification text,
    status = "pending"
```

**Cost per notification:** ~$0.002 (two tenths of a cent).

---

## Scheduling

### Three Independent Cycles

```
MONTHLY (1st of each month):
    1. download_retraction_database.py
       Calls CrossRef API and PubMed API
       Downloads full list of retracted papers
       Saves to training/data/retraction_database_combined.json

    2. precompute_retraction_embeddings.py
       Loads the updated retraction database
       Runs each paper through sentence transformer
       Saves all embeddings to models/retraction_embeddings.pkl

    Duration: 30 to 45 minutes
    External calls: CrossRef API, PubMed API
    Purpose: Keep retraction data current


WEEKLY (every Monday):
    1. initial_import.py
       Calls Wikipedia API for each watched article
       Compares against existing citations in database
       Saves any new or changed citations
       New citations get last_checked = NULL

    Duration: 10 to 30 minutes depending on article count
    External calls: Wikipedia API
    Purpose: Catch new citations added by editors


DAILY (every day at 6 AM):
    1. synthesizer_agent.py
       Loads ML models into memory (30 to 60 seconds)
       Queries database for citations where:
           last_checked is NULL (new, never checked)
           OR last_checked older than 30 days (stale, needs recheck)
       Checks each citation against local retraction data
       Generates notifications for retracted citations
       Updates last_checked timestamps
       Saves findings

    Duration: depends on citation count
       Typical day (10 to 50 new citations): 1 to 2 minutes
       Monthly recheck (all 5,000 citations): 5 to 10 minutes
    External calls: LLM only, and only for confirmed retractions
    Purpose: Detect retracted citations and generate alerts
```

### Why This Schedule Works

On most days, the synthesizer has very little work. Maybe 10 to 20 new citations from the weekly import. Some days it has nothing at all. This is by design. The system is not meant to run constantly. It checks what needs checking and stops.

Once a month, after the retraction database is refreshed, all citations become eligible for rechecking (their last_checked dates are now 30+ days old). The synthesizer rechecks everything over the next few days. This catches papers that were retracted since the last check.

The three cycles are completely independent. If the monthly download fails, the daily run still works using the previous month's data. If the weekly import fails, the daily run still checks existing citations. No single failure brings down the entire system.

---

## Database Schema

### Core Tables

```
articles
    id              SERIAL PRIMARY KEY
    title           TEXT NOT NULL
    wiki_page_id    INTEGER
    last_imported    TIMESTAMP
    url             TEXT

citations
    id              SERIAL PRIMARY KEY
    article_id      INTEGER REFERENCES articles(id)
    raw_text        TEXT NOT NULL
    citation_type   TEXT (journal, web, book, news)
    title           TEXT
    authors         TEXT[]
    doi             TEXT
    url             TEXT
    journal         TEXT
    year            INTEGER
    last_checked    TIMESTAMP (NULL = never checked)
    created_at      TIMESTAMP DEFAULT NOW()

findings
    id              SERIAL PRIMARY KEY
    citation_id     INTEGER REFERENCES citations(id)
    problem_type    TEXT NOT NULL (retracted_citation)
    severity        TEXT NOT NULL (critical, major, minor, corrected)
    confidence      FLOAT
    match_method    TEXT (doi_exact, fuzzy_title)
    details         JSONB
    notification    TEXT (LLM generated message for editors)
    status          TEXT DEFAULT 'pending' (pending, posted, dismissed)
    found_date      TIMESTAMP DEFAULT NOW()
```

### Key Queries

```sql
-- Daily run: find citations needing checking
SELECT * FROM citations
WHERE last_checked IS NULL
   OR last_checked < NOW() - INTERVAL '30 days'
ORDER BY last_checked NULLS FIRST
LIMIT 500;

-- After checking: update timestamp
UPDATE citations SET last_checked = NOW() WHERE id = ?;

-- Weekly import: check if citation already exists
SELECT id FROM citations
WHERE article_id = ? AND raw_text = ?;

-- Pending notifications
SELECT f.*, c.article_id, a.title as article_title
FROM findings f
JOIN citations c ON f.citation_id = c.id
JOIN articles a ON c.article_id = a.id
WHERE f.status = 'pending'
ORDER BY f.severity, f.found_date;
```

---

## Core Components

### Shared HTTP Client (`core/utils.py`)

All external API calls go through the shared HTTP client. This provides consistent rate limiting, error handling, timeout management, and session reuse.

```python
from core.utils import HTTPClient

client = HTTPClient(
    base_url="https://api.crossref.org",
    user_agent="WikiVerify/1.0 (mailto:you@email.com)",
    rate_limit_delay=1.0
)

response = client.get("/works", params={"filter": "type:retraction"})
```

Used by: all integration modules (crossref.py, pubmed.py, wikipedia_api.py). Never used during the daily checking run because the daily run makes no external API calls (except the LLM).

### Logging System (`core/logger.py`)

Structured logging with levels. File and console output.

```python
from core.logger import get_logger
logger = get_logger(__name__)

logger.info("Checking citation %d", citation_id)
logger.warning("Low confidence match: %.2f", score)
logger.error("Model failed to load: %s", error)
```

### Constants (`core/constants.py`)

All magic values are centralized. Enums provide type safety and IDE autocomplete.

```python
from core.constants import ProblemType, Severity, MatchMethod

problem = ProblemType.RETRACTED_CITATION
severity = Severity.CRITICAL
method = MatchMethod.FUZZY_TITLE
SIMILARITY_THRESHOLD = 0.85
RECHECK_INTERVAL_DAYS = 30
```

### Database Layer (`core/database.py`)

Context manager for connections. Automatic transaction handling.

```python
from core.database import get_connection

with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citations WHERE last_checked IS NULL")
    citations = cursor.fetchall()
    # Auto commits on success, rolls back on error
```

---

## Integration Pattern

All integrations follow the same structure. They use the shared HTTP client. They are only called during the monthly or weekly cycles, never during the daily run.

```python
class CrossRefIntegration:
    def __init__(self):
        self.client = HTTPClient(
            base_url="https://api.crossref.org",
            user_agent="WikiVerify/1.0",
            rate_limit_delay=1.0
        )

    def get_retracted_papers(self):
        """Called monthly. Downloads all retracted papers."""
        papers = []
        cursor = "*"
        while cursor:
            response = self.client.get("/works", params={
                "filter": "update-type:retraction",
                "cursor": cursor,
                "rows": 100
            })
            if not response:
                break
            papers.extend(response["message"]["items"])
            cursor = response["message"].get("next-cursor")
        return papers
```

---

## ML Module Pattern

Each ML module in the `ml/` directory follows the same pattern. Load once, use many times. Fail gracefully.

```python
class CitationExtractor:
    def __init__(self, model_path="models/citation_extractor"):
        self.model = None
        self.tokenizer = None
        self._load_model(model_path)

    def _load_model(self, path):
        """Load model from disk into memory. Called once at startup."""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(path)
            self.model = AutoModelForTokenClassification.from_pretrained(path)
            logger.info("Citation extractor loaded from %s", path)
        except Exception as e:
            logger.error("Failed to load citation extractor: %s", e)
            self.model = None

    def extract(self, raw_text):
        """Extract entities from citation text. Called per citation."""
        if self.model is None:
            return None  # Fail gracefully
        tokens = self.tokenizer(raw_text, return_tensors="pt")
        outputs = self.model(**tokens)
        # Process outputs into structured fields
        return {"title": ..., "author": ..., "year": ..., "journal": ...}
```

---

## Agent Pattern

The synthesizer agent follows the base agent pattern but adds ML model orchestration.

```python
class SynthesizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("synthesizer")
        self.checker = RetractionChecker()
        self.llm = LLMTriage()

    def run(self):
        self.log("Starting daily retraction check")

        citations = self._get_unchecked_citations()
        self.log(f"Found {len(citations)} citations to check")

        for citation in citations:
            try:
                result = self.checker.check(citation)

                if result["is_retracted"]:
                    notification = self.llm.generate_notification(result)
                    self._save_finding(citation, result, notification)

                self._update_last_checked(citation["id"])

            except Exception as e:
                self.log(f"Error checking citation {citation['id']}: {e}")
                continue  # Don't crash on single citation error

        self.log("Daily run complete")
```

---

## Error Handling

Every component follows the same error handling philosophy: log the error, fail gracefully, continue processing.

A single broken citation should never crash the entire daily run. A failed model load should not prevent the agent from starting (it can still check citations with DOIs using exact lookup). A failed LLM call should not prevent findings from being saved (save without notification text, generate it later).

```
Model A fails to load:
    Log warning. Skip fuzzy matching.
    Citations with DOIs still get checked via exact lookup.
    Citations without DOIs are skipped with a logged warning.

Model B fails to load:
    Log warning. Use "unknown" severity.
    Retracted citations still get detected.
    Severity classification is degraded but detection works.

Model C fails to load:
    Log warning. Skip fuzzy matching entirely.
    Same behavior as Model A failure.

LLM call fails:
    Log warning. Save finding without notification text.
    Mark as "pending_notification" instead of "pending".
    Retry notification generation on next run.

Database connection fails:
    Log error. Abort the daily run.
    This is the one failure that stops everything.
    The scheduler will retry on the next scheduled run.
```

---

## Deployment

### Development

```bash
# Start database
docker-compose up -d postgres

# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initial setup
python scripts/initial_import.py
python scripts/download_retraction_database.py
python scripts/precompute_retraction_embeddings.py

# Run manually
python -m agents.synthesizer_agent
```

### Production

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: wikiverify
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  wikiverify:
    build: .
    depends_on:
      - postgres
    volumes:
      - ./models:/app/models
      - ./training/data:/app/training/data
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/wikiverify
      LLM_API_KEY: ${LLM_API_KEY}
```

The application container runs the scheduler which manages all three cycles (monthly, weekly, daily). Models are stored in a mounted volume so they persist across container restarts and can be updated without rebuilding the image.

### Resource Requirements

```
RAM:    ~2 GB minimum
          850 MB for ML models
          500 MB for application and database connections
          Buffer for processing

CPU:    2 cores minimum
          ML inference is CPU bound but fast (milliseconds per citation)
          No GPU needed for inference

Disk:   ~2 GB for models and data
          400 MB citation extractor
          250 MB severity classifier
          80 MB sentence transformer
          100 MB precomputed embeddings
          500 MB retraction database
          Remaining for logs, database, etc.

Cost:   $30 to $80/month for a cloud server
        $0.002 per LLM notification call
        All APIs and models are free
```

---

## Training Pipeline

### Model A: Citation Entity Extractor

```
1. Run build_ner_dataset.py
   Reads citations from PostgreSQL
   Creates labeled NER examples from template citations
   Saves to training/data/ner_train.json

2. Open training/train_citation_extractor.ipynb in Google Colab
   Upload ner_train.json to Google Drive
   Set runtime to GPU
   Fine tune SciBERT on NER task
   10 epochs, batch size 16, learning rate 2e-5
   Training time: 15 to 30 minutes

3. Save trained model to Google Drive
   Download to models/citation_extractor/
```

### Model B: Severity Classifier

```
1. Map Retraction Watch reason codes to severity levels
   "Falsification/Fabrication of Data" → critical
   "Error in Data/Analysis" → major
   "Authorship Dispute" → minor
   "Replaced with Corrected Article" → corrected
   Save to training/data/severity_train.json

2. Open training/train_severity_classifier.ipynb in Google Colab
   Upload severity_train.json to Google Drive
   Set runtime to GPU
   Fine tune DistilBERT on classification task
   5 epochs, batch size 16, learning rate 2e-5
   Training time: 5 to 15 minutes

3. Save trained model to Google Drive
   Download to models/severity_classifier/
```

### Model C: Sentence Transformer

No training. Downloaded automatically from HuggingFace on first use.

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Model downloads to ~/.cache/torch/sentence_transformers/
# Size: ~80 MB
```

---

## Future Enhancements

> Note: The following are potential future enhancements, not part of the current architecture.

### Source Change Agent ML Integration (Future)

Three additional models planned for the source change detection pipeline:

**Semantic Change Detector:** Sentence transformer embeddings to compare old vs new source content by meaning rather than characters. Detects "drug is effective" changing to "drug is NOT effective" even though only one word changed.

**Claim Relevance Checker:** DeBERTa NLI model to determine whether a source content change actually affects the Wikipedia claim it supports. Filters out irrelevant changes (formatting, unrelated paragraphs).

**Change Type Classifier:** Fine tuned DistilBERT to categorize changes as cosmetic, addition, correction, contradiction, or removal. Helps prioritize which changes editors should review first.

### Notification Delivery

**Wikipedia Bot:** Automated posting to article Talk pages when retracted citations are found. Requires Wikipedia bot approval process.

**Browser Extension:** Editor facing tool that highlights problematic citations while browsing Wikipedia. Shows warnings inline with severity indicators.

### Feedback Loop

Editor responses to notifications (useful vs noise) feed back into model retraining. Over time, the models improve at distinguishing real problems from false positives.
