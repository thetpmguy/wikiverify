"""CrossRef API integration."""
from typing import Optional, Dict, Any
from core.config import Config
from core.utils import HTTPClient
from core.logger import get_logger

logger = get_logger(__name__)


class CrossRef:
    """Client for CrossRef API."""
    
    def __init__(self):
        """Initialize the CrossRef client."""
        self.base_url = "https://api.crossref.org"
        self.email = Config.PUBMED_EMAIL or "contact@example.com"
        # Be polite: 1 request/second
        self.client = HTTPClient(
            base_url=self.base_url,
            user_agent=f'WikiVerify/1.0 (mailto:{self.email})',
            rate_limit_delay=1.0,
            timeout=Config.CHECK_TIMEOUT
        )
        self.client.session.headers.update({'Accept': 'application/json'})
    
    def normalize_doi(self, doi: str) -> str:
        """
        Normalize a DOI string.
        
        Args:
            doi: DOI string (may include prefixes)
        
        Returns:
            Normalized DOI
        """
        if not doi:
            return ""
        
        # Remove common prefixes
        doi = doi.strip().lower()
        doi = doi.replace('doi:', '').replace('DOI:', '').replace('https://doi.org/', '').strip()
        
        return doi
    
    def get_work(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Get work metadata from CrossRef by DOI.
        
        Args:
            doi: DOI to look up
        
        Returns:
            Work metadata or None if not found
        """
        normalized_doi = self.normalize_doi(doi)
        if not normalized_doi:
            return None
        
        url = f"/works/{normalized_doi}"
        
        response = self.client.get(url)
        if not response:
            return None
        
        try:
            data = response.json()
            if data.get('status') == 'ok':
                return data.get('message', {})
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing CrossRef response for {doi}: {e}")
        
        return None
    
    def check_retraction(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Check if a DOI has been retracted according to CrossRef.
        
        CrossRef indicates retractions in the 'update-to' field with type 'retraction'.
        
        Args:
            doi: DOI to check
        
        Returns:
            Retraction record if found, None otherwise
        """
        work = self.get_work(doi)
        if not work:
            return None
        
        # Check for retraction in update-to field
        updates = work.get('update-to', [])
        for update in updates:
            if isinstance(update, dict):
                update_type = update.get('type', '').lower()
                if 'retraction' in update_type:
                    return {
                        'doi': self.normalize_doi(doi),
                        'title': work.get('title', [''])[0] if work.get('title') else None,
                        'retraction_date': None,  # CrossRef doesn't always provide this
                        'retraction_reason': f"Retraction notice in CrossRef (type: {update_type})",
                        'source': 'crossref'
                    }
        
        # Also check if the work itself is a retraction notice
        # (looking for retraction in title or type)
        work_type = work.get('type', '').lower()
        if 'retraction' in work_type:
            return {
                'doi': self.normalize_doi(doi),
                'title': work.get('title', [''])[0] if work.get('title') else None,
                'retraction_date': None,
                'retraction_reason': "Retraction notice identified in CrossRef",
                'source': 'crossref'
            }
        
        return None
