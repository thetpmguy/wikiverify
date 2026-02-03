"""Source Change Agent - Detects when source content has changed."""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from core.database import execute_query, update_citation_last_checked
from core.config import Config
from core.utils import HTTPClient
from core.constants import ProblemType, Severity, DEFAULT_SIMILARITY_THRESHOLD
from core.snapshot import SnapshotManager
from core.content_extractor import ContentExtractor
from llm.triage import LLMTriage


class SourceChangeAgent(BaseAgent):
    """Agent that detects when source content has changed significantly."""
    
    def __init__(self, use_llm_triage: bool = True):
        """
        Initialize the Source Change Agent.
        
        Args:
            use_llm_triage: Whether to use LLM triage to filter false positives
        """
        super().__init__("source_change_agent")
        self.snapshot_manager = SnapshotManager()
        self.content_extractor = ContentExtractor()
        self.client = HTTPClient(
            base_url=None,  # URLs are full paths
            user_agent=Config.WIKIPEDIA_USER_AGENT,
            rate_limit_delay=Config.RATE_LIMIT_DELAY,
            timeout=Config.CHECK_TIMEOUT
        )
        self.similarity_threshold = DEFAULT_SIMILARITY_THRESHOLD
        self.llm_triage = LLMTriage(enabled=use_llm_triage) if use_llm_triage else None
    
    def fetch_current_content(self, url: str) -> Optional[str]:
        """
        Fetch current content from a URL.
        
        Args:
            url: URL to fetch
        
        Returns:
            HTML content or None if error
        """
        response = self.client.get(url)
        if response:
            return response.text
        return None
    
    def check_citation(self, citation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check a single citation for content changes.
        
        Args:
            citation: Citation dictionary from database
        
        Returns:
            Finding dictionary if change detected, None otherwise
        """
        url = citation.get('source_url')
        snapshot_url = citation.get('snapshot_url')
        
        if not url:
            return None
        
        if not snapshot_url:
            # Create snapshot if doesn't exist
            self.log(f"Creating snapshot for citation {citation['id']}", "info")
            snapshot_url = self.snapshot_manager.create_snapshot(citation['id'], url)
            if not snapshot_url:
                self.log(f"Could not create snapshot for {url}", "warning")
                return None
        
        self.log(f"Checking citation {citation['id']}: {url}", "debug")
        
        # Fetch current content
        current_html = self.fetch_current_content(url)
        if not current_html:
            return None
        
        # Fetch snapshot content
        snapshot_html = self.snapshot_manager.get_snapshot_content(snapshot_url)
        if not snapshot_html:
            self.log(f"Could not fetch snapshot content: {snapshot_url}", "warning")
            return None
        
        # Extract text from both
        current_text = self.content_extractor.extract_text(current_html)
        snapshot_text = self.content_extractor.extract_text(snapshot_html)
        
        if not current_text or not snapshot_text:
            return None
        
        # Calculate similarity
        similarity = self.content_extractor.calculate_similarity(current_text, snapshot_text)
        
        self.log(f"Similarity: {similarity:.2%}", "debug")
        
        if similarity < self.similarity_threshold:
            change_percent = (1 - similarity) * 100
            details = (
                f"Source content has changed significantly. "
                f"Similarity: {similarity:.1%} (threshold: {self.similarity_threshold:.1%}). "
                f"Content changed by approximately {change_percent:.1f}%. "
                f"Original snapshot: {snapshot_url}"
            )
            
            finding = {
                'citation_id': citation['id'],
                'wikipedia_article': citation['wikipedia_article'],
                'problem_type': ProblemType.SOURCE_CHANGE,
                'details': details,
                'severity': Severity.MEDIUM if similarity > 0.50 else Severity.HIGH
            }
            
            # Use LLM triage to determine if this is a significant change
            if self.llm_triage:
                citation_context = {
                    'source_url': url,
                    'source_title': citation.get('source_title'),
                    'wikipedia_article': citation.get('wikipedia_article'),
                    'citation_number': citation.get('citation_number'),
                    'similarity': similarity,
                    'change_percent': change_percent
                }
                
                is_real_problem = self.llm_triage.is_real_problem(
                    problem_type=ProblemType.SOURCE_CHANGE,
                    details=details,
                    citation_context=citation_context
                )
                
                if not is_real_problem:
                    self.log(f"LLM triage: False positive filtered for citation {citation['id']} (similarity: {similarity:.1%})", "debug")
                    return None
                
                # Generate enhanced explanation
                enhanced_details = self.llm_triage.explain_finding(
                    problem_type=ProblemType.SOURCE_CHANGE,
                    details=details,
                    citation_context=citation_context
                )
                finding['details'] = enhanced_details
            
            return finding
        
        return None
    
    def run(self, limit: int = 100):
        """
        Run the source change agent.
        
        Args:
            limit: Maximum number of citations to check
        """
        self.log("Starting Source Change Agent", "info")
        
        # Query citations with snapshots
        query = """
        SELECT * FROM citations
        WHERE snapshot_url IS NOT NULL
        AND source_url IS NOT NULL
        ORDER BY last_checked NULLS FIRST, created_at DESC
        LIMIT %s
        """
        citations = execute_query(query, (limit,))
        
        self.log(f"Found {len(citations)} citations with snapshots to check", "info")
        
        findings_count = 0
        checked_count = 0
        
        for citation in citations:
            try:
                finding = self.check_citation(citation)
                
                if finding:
                    self.save_finding(
                        citation_id=finding['citation_id'],
                        wikipedia_article=finding['wikipedia_article'],
                        problem_type=finding['problem_type'],
                        details=finding['details'],
                        severity=finding['severity']
                    )
                    findings_count += 1
                    self.log(f"Found content change: {citation.get('source_url')}", "info")
                
                # Update last_checked timestamp
                update_citation_last_checked(citation['id'])
                checked_count += 1
            except Exception as e:
                self.log(f"Error checking citation {citation.get('id')}: {e}", "error")
                continue
        
        self.log(f"Completed: Checked {checked_count} citations, found {findings_count} content changes", "info")


if __name__ == "__main__":
    agent = SourceChangeAgent()
    agent.run()
