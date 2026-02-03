"""Constants used throughout WikiVerify."""
from enum import Enum


class ProblemType(str, Enum):
    """Types of citation problems."""
    BROKEN_LINK = "broken_link"
    RETRACTION = "retraction"
    SOURCE_CHANGE = "source_change"
    EVIDENCE_WEAK = "evidence_weak"


class Severity(str, Enum):
    """Severity levels for findings."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CitationStatus(str, Enum):
    """Status of citations."""
    UNCHECKED = "unchecked"
    CHECKING = "checking"
    OK = "ok"
    PROBLEM = "problem"
    ERROR = "error"


class ReportingStatus(str, Enum):
    """Status of findings reporting."""
    PENDING = "pending"
    REPORTED = "reported"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


# Default values
DEFAULT_SIMILARITY_THRESHOLD = 0.80
DEFAULT_CHECK_INTERVAL_DAYS = 7
DEFAULT_RATE_LIMIT_DELAY = 1.0
DEFAULT_CHECK_TIMEOUT = 10

# Citation template names
CITATION_TEMPLATES = [
    'cite journal', 'cite web', 'cite news', 'cite book',
    'cite paper', 'cite conference', 'cite arxiv', 'cite pmid',
    'cite doi', 'cite pmc'
]

# HTTP status codes
HTTP_ERROR_CODES = [404, 410, 500, 503]
HTTP_SUCCESS_CODES = [200, 201, 202]

# Retraction sources
RETRACTION_SOURCE_RETRACTION_WATCH = "retraction_watch"
RETRACTION_SOURCE_PUBMED = "pubmed"
RETRACTION_SOURCE_CROSSREF = "crossref"
