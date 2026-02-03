"""Snapshot system for capturing source content."""
from typing import Optional, Dict, Any
from integrations.internet_archive import InternetArchive
from core.database import get_connection, execute_update
from core.logger import get_logger

logger = get_logger(__name__)


class SnapshotManager:
    """Manages snapshots of source content."""
    
    def __init__(self):
        """Initialize the snapshot manager."""
        self.internet_archive = InternetArchive()
    
    def create_snapshot(self, citation_id: int, url: str) -> Optional[str]:
        """
        Create a snapshot of a source URL and save it to the database.
        
        Args:
            citation_id: ID of the citation
            url: URL to snapshot
        
        Returns:
            Snapshot URL if successful, None otherwise
        """
        # First check if snapshot already exists
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT snapshot_url FROM citations WHERE id = %s AND snapshot_url IS NOT NULL",
                (citation_id,)
            )
            existing = cursor.fetchone()
            if existing:
                return existing[0]
        
        # Try to get existing snapshot from Internet Archive
        archive_info = self.internet_archive.get_available_snapshot(url)
        
        if archive_info.get('available'):
            snapshot_url = archive_info['url']
            snapshot_date = archive_info.get('timestamp')
            
            # Save to database
            self._save_snapshot_to_db(citation_id, snapshot_url, snapshot_date)
            return snapshot_url
        
        # If no existing snapshot, request a new one
        # Note: Save Page Now API requires polling, so this is async
        archive_url = self.internet_archive.save_page_now(url)
        if archive_url:
            self._save_snapshot_to_db(citation_id, archive_url, None)
            return archive_url
        
        return None
    
    def _save_snapshot_to_db(self, citation_id: int, snapshot_url: str, snapshot_date: Optional[str] = None):
        """Save snapshot information to the database."""
        query = """
        UPDATE citations
        SET snapshot_url = %s, snapshot_date = %s
        WHERE id = %s
        """
        execute_update(query, (snapshot_url, snapshot_date, citation_id))
    
    def get_snapshot_content(self, snapshot_url: str) -> Optional[str]:
        """
        Get the content of a snapshot.
        
        Args:
            snapshot_url: URL of the snapshot
        
        Returns:
            HTML content or None if error
        """
        return self.internet_archive.get_snapshot_content(snapshot_url)
