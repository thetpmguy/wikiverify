"""Internet Archive / Wayback Machine integration."""
from typing import Optional, Dict, Any
from core.config import Config
from core.utils import HTTPClient
from core.logger import get_logger

logger = get_logger(__name__)


class InternetArchive:
    """Client for Internet Archive Wayback Machine API."""
    
    def __init__(self):
        """Initialize the Internet Archive client."""
        self.base_url = "https://archive.org/wayback"
        self.client = HTTPClient(
            base_url=self.base_url,
            rate_limit_delay=Config.RATE_LIMIT_DELAY,
            timeout=Config.CHECK_TIMEOUT
        )
    
    def get_available_snapshot(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Check if a URL has an archived snapshot in Wayback Machine.
        
        Args:
            url: URL to check
        
        Returns:
            Dictionary with snapshot info or None if not found
        """
        api_url = "/available"
        params = {'url': url}
        
        response = self.client.get(api_url, params=params)
        if not response:
            return {'available': False}
        
        try:
            data = response.json()
            
            if data.get('archived_snapshots', {}).get('closest'):
                snapshot = data['archived_snapshots']['closest']
                return {
                    'available': True,
                    'url': snapshot.get('url'),
                    'timestamp': snapshot.get('timestamp'),
                    'status': snapshot.get('status')
                }
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing Internet Archive response for {url}: {e}")
        
        return {'available': False}
    
    def save_page_now(self, url: str) -> Optional[str]:
        """
        Request Internet Archive to save a page now.
        
        Args:
            url: URL to archive
        
        Returns:
            Archive URL if successful, None otherwise
        """
        api_url = "https://web.archive.org/save"
        params = {'url': url}
        
        if Config.INTERNET_ARCHIVE_EMAIL:
            params['email'] = Config.INTERNET_ARCHIVE_EMAIL
        
        response = self.client.post(api_url, data=params, timeout=30)
        
        if response and response.status_code == 200:
            # The API returns JSON with job_id, we'd need to poll for completion
            # For now, return a placeholder
            return f"https://web.archive.org/web/*/{url}"
        
        return None
    
    def get_snapshot_content(self, archive_url: str) -> Optional[str]:
        """
        Get the content of an archived snapshot.
        
        Args:
            archive_url: Wayback Machine archive URL
        
        Returns:
            HTML content or None if error
        """
        response = self.client.get(archive_url)
        if response:
            return response.text
        return None
