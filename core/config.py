"""Configuration management for WikiVerify."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/wikiverify")
    
    # Wikipedia API
    WIKIPEDIA_USER_AGENT = os.getenv("WIKIPEDIA_USER_AGENT", "WikiVerify/1.0 (contact@example.com)")
    WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
    
    # Rate Limiting
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1"))  # seconds between requests
    CHECK_TIMEOUT = int(os.getenv("CHECK_TIMEOUT", "15"))  # seconds (increased from 10 to 15 for slow sites)
    
    # LLM Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # Internet Archive
    INTERNET_ARCHIVE_EMAIL = os.getenv("INTERNET_ARCHIVE_EMAIL", "")
    
    # PubMed
    PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "")
