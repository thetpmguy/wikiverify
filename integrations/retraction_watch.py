"""Retraction Watch database integration."""
import csv
from typing import List, Dict, Any, Optional
from core.config import Config
from core.database import get_connection
from core.utils import HTTPClient
from core.logger import get_logger

logger = get_logger(__name__)


class RetractionWatch:
    """Client for Retraction Watch database."""
    
    def __init__(self):
        """Initialize the Retraction Watch client."""
        # Retraction Watch database URL (update with actual URL when available)
        self.database_url = "https://retractionwatch.com/wp-content/uploads/retraction-watch-database.csv"
        self.client = HTTPClient(
            base_url=None,  # Full URLs
            timeout=30  # Longer timeout for large file downloads
        )
    
    def download_database(self) -> Optional[List[Dict[str, Any]]]:
        """
        Download the Retraction Watch database.
        
        Returns:
            List of retraction records or None if error
        """
        response = self.client.get(self.database_url)
        if not response:
            return None
        
        try:
            # Parse CSV
            csv_content = response.text
            reader = csv.DictReader(csv_content.splitlines())
            retractions = []
            
            for row in reader:
                retraction = {
                    'doi': self._normalize_doi(row.get('DOI', '')),
                    'paper_title': row.get('Title', ''),
                    'retraction_date': row.get('RetractionDate', ''),
                    'retraction_reason': row.get('Reason', ''),
                    'source': 'retraction_watch'
                }
                if retraction['doi']:
                    retractions.append(retraction)
            
            return retractions
        except (csv.Error, ValueError) as e:
            logger.error(f"Error parsing Retraction Watch CSV: {e}")
            return None
    
    def _normalize_doi(self, doi: str) -> Optional[str]:
        """Normalize a DOI string."""
        if not doi:
            return None
        
        # Remove common prefixes
        doi = doi.strip().lower()
        doi = doi.replace('doi:', '').replace('DOI:', '').strip()
        
        # Extract DOI pattern (10.xxxx/...)
        import re
        match = re.search(r'10\.\d{4,}/[^\s<>"{}|\\^`\[\]]+', doi)
        if match:
            return match.group(0)
        
        return None
    
    def update_cache(self):
        """Download and update the retractions cache in the database."""
        retractions = self.download_database()
        if not retractions:
            print("No retractions downloaded")
            return 0
        
        with get_connection() as conn:
            cursor = conn.cursor()
            inserted = 0
            updated = 0
            
            for retraction in retractions:
                # Check if exists
                cursor.execute(
                    "SELECT id FROM retractions_cache WHERE doi = %s",
                    (retraction['doi'],)
                )
                exists = cursor.fetchone()
                
                if exists:
                    # Update
                    cursor.execute("""
                        UPDATE retractions_cache
                        SET paper_title = %s, retraction_date = %s,
                            retraction_reason = %s, source = %s,
                            fetched_at = NOW()
                        WHERE doi = %s
                    """, (
                        retraction['paper_title'],
                        retraction['retraction_date'],
                        retraction['retraction_reason'],
                        retraction['source'],
                        retraction['doi']
                    ))
                    updated += 1
                else:
                    # Insert
                    cursor.execute("""
                        INSERT INTO retractions_cache
                        (doi, paper_title, retraction_date, retraction_reason, source)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        retraction['doi'],
                        retraction['paper_title'],
                        retraction['retraction_date'],
                        retraction['retraction_reason'],
                        retraction['source']
                    ))
                    inserted += 1
            
            logger.info(f"Updated cache: {inserted} inserted, {updated} updated")
            return inserted + updated
    
    def check_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Check if a DOI is in the retractions cache.
        
        Args:
            doi: DOI to check
        
        Returns:
            Retraction record if found, None otherwise
        """
        normalized_doi = self._normalize_doi(doi)
        if not normalized_doi:
            return None
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM retractions_cache WHERE doi = %s",
                (normalized_doi,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'doi': row[1],
                    'paper_title': row[2],
                    'retraction_date': row[3],
                    'retraction_reason': row[4],
                    'source': row[5]
                }
        
        return None
