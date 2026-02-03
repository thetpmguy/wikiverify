"""Database connection and utilities."""
import psycopg2
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


@contextmanager
def get_connection():
    """
    Get a database connection context manager.
    
    Yields:
        Database connection
    
    Raises:
        psycopg2.Error: If connection fails
    """
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def execute_query(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """
    Execute a SELECT query and return results as list of dicts.
    
    Args:
        query: SQL query string
        params: Query parameters
    
    Returns:
        List of dictionaries representing rows
    
    Raises:
        psycopg2.Error: If query execution fails
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            results = cursor.fetchall()
            return [dict(zip(columns, row)) for row in results]
    except psycopg2.Error as e:
        logger.error(f"Query execution error: {e}, Query: {query[:100]}")
        raise


def execute_update(query: str, params: Optional[tuple] = None) -> int:
    """
    Execute an INSERT/UPDATE/DELETE query and return affected rows.
    
    Args:
        query: SQL query string
        params: Query parameters
    
    Returns:
        Number of affected rows
    
    Raises:
        psycopg2.Error: If query execution fails
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    except psycopg2.Error as e:
        logger.error(f"Update execution error: {e}, Query: {query[:100]}")
        raise


def save_citation(citation: Dict[str, Any]) -> int:
    """Save a citation to the database and return its ID."""
    query = """
    INSERT INTO citations (
        wikipedia_article, wikipedia_language, citation_number,
        source_url, source_doi, source_title, source_authors,
        source_journal, source_year, snapshot_url, snapshot_date,
        status, last_checked
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    ) RETURNING id
    """
    params = (
        citation.get('wikipedia_article'),
        citation.get('wikipedia_language', 'en'),
        citation.get('citation_number'),
        citation.get('source_url'),
        citation.get('source_doi'),
        citation.get('source_title'),
        citation.get('source_authors'),
        citation.get('source_journal'),
        citation.get('source_year'),
        citation.get('snapshot_url'),
        citation.get('snapshot_date'),
        citation.get('status', 'unchecked'),
        citation.get('last_checked')
    )
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0]


def save_finding(citation_id: int, wikipedia_article: str, problem_type: str,
                 details: str, severity: str = 'medium') -> int:
    """Save a finding to the database and return its ID."""
    query = """
    INSERT INTO findings (
        citation_id, wikipedia_article, problem_type, severity, details
    ) VALUES (%s, %s, %s, %s, %s) RETURNING id
    """
    params = (citation_id, wikipedia_article, problem_type, severity, details)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()[0]


def get_citations_needing_check(days: int = 7, limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Get citations that need to be checked (not checked in last N days).
    
    Args:
        days: Number of days since last check
        limit: Maximum number of citations to return
    
    Returns:
        List of citation dictionaries
    """
    query = """
    SELECT * FROM citations
    WHERE (last_checked IS NULL OR last_checked < NOW() - INTERVAL '%s days')
    AND source_url IS NOT NULL
    ORDER BY last_checked NULLS FIRST
    LIMIT %s
    """
    return execute_query(query, (days, limit))


def get_citations_with_dois() -> List[Dict[str, Any]]:
    """Get all citations that have DOIs."""
    query = """
    SELECT * FROM citations
    WHERE source_doi IS NOT NULL
    """
    return execute_query(query)


def update_citation_last_checked(citation_id: int):
    """Update the last_checked timestamp for a citation."""
    query = """
    UPDATE citations
    SET last_checked = NOW()
    WHERE id = %s
    """
    execute_update(query, (citation_id,))
