"""Broken Link Agent - Detects when source URLs no longer work."""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from core.database import get_citations_needing_check, update_citation_last_checked
from core.config import Config
from core.utils import HTTPClient
from core.constants import ProblemType, Severity, HTTP_ERROR_CODES
from llm.triage import LLMTriage


class BrokenLinkAgent(BaseAgent):
    """Agent that checks if citation URLs are still accessible."""
    
    def __init__(self, use_llm_triage: bool = True):
        """
        Initialize the Broken Link Agent.
        
        Args:
            use_llm_triage: Whether to use LLM triage to filter false positives
        """
        super().__init__("broken_link_agent")
        self.client = HTTPClient(
            base_url=None,  # URLs are full paths
            user_agent=Config.WIKIPEDIA_USER_AGENT,
            rate_limit_delay=Config.RATE_LIMIT_DELAY,
            timeout=Config.CHECK_TIMEOUT
        )
        self.llm_triage = LLMTriage(enabled=use_llm_triage) if use_llm_triage else None
    
    def check_url(self, url: str) -> Dict[str, Any]:
        """
        Check if a URL is accessible.
        
        Args:
            url: URL to check
        
        Returns:
            Dictionary with check results
        """
        result = {
            'accessible': False,
            'status_code': None,
            'error': None,
            'redirects_to_homepage': False
        }
        
        # Try HEAD request first (faster, less bandwidth)
        response = self.client.head(url, allow_redirects=True)
        
        if response:
            result['status_code'] = response.status_code
            
            # Check for error status codes
            if response.status_code in HTTP_ERROR_CODES:
                result['error'] = f"HTTP {response.status_code}"
                return result
            
            # Check if redirects to homepage (likely broken)
            final_url = response.url
            if self._is_homepage_redirect(url, final_url):
                result['redirects_to_homepage'] = True
                result['error'] = "Redirects to homepage"
                return result
            
            result['accessible'] = True
            return result
        
        # If HEAD fails, try GET
        response = self.client.get(url, allow_redirects=True)
        
        if response:
            result['status_code'] = response.status_code
            
            if response.status_code in HTTP_ERROR_CODES:
                result['error'] = f"HTTP {response.status_code}"
            elif self._is_homepage_redirect(url, response.url):
                result['redirects_to_homepage'] = True
                result['error'] = "Redirects to homepage"
            else:
                result['accessible'] = True
        else:
            result['error'] = "Connection failed"
        
        return result
    
    def _is_homepage_redirect(self, original_url: str, final_url: str) -> bool:
        """
        Check if a URL redirects to a homepage (likely broken link).
        
        Args:
            original_url: Original URL
            final_url: Final URL after redirects
        
        Returns:
            True if redirects to homepage
        """
        # Extract domain from URLs
        try:
            from urllib.parse import urlparse
            original_domain = urlparse(original_url).netloc
            final_domain = urlparse(final_url).netloc
            
            # If domains match and final URL is just the domain or root path
            if original_domain == final_domain:
                final_path = urlparse(final_url).path
                if final_path in ['', '/', '/index.html', '/index.php', '/home']:
                    return True
        except Exception:
            pass
        
        return False
    
    def check_citation(self, citation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check a single citation for broken links.
        
        Args:
            citation: Citation dictionary from database
        
        Returns:
            Finding dictionary if problem found, None otherwise
        """
        url = citation.get('source_url')
        if not url:
            return None
        
        self.log(f"Checking citation {citation['id']}: {url}", "debug")
        check_result = self.check_url(url)
        
        if not check_result['accessible']:
            # Problem found
            details = f"URL {url} is not accessible"
            if check_result['error']:
                details += f": {check_result['error']}"
            if check_result['status_code']:
                details += f" (HTTP {check_result['status_code']})"
            
            finding = {
                'citation_id': citation['id'],
                'wikipedia_article': citation['wikipedia_article'],
                'problem_type': ProblemType.BROKEN_LINK,
                'details': details,
                'severity': Severity.HIGH if check_result['status_code'] in [404, 410] else Severity.MEDIUM
            }
            
            # Use LLM triage to filter false positives
            if self.llm_triage:
                citation_context = {
                    'source_url': url,
                    'source_title': citation.get('source_title'),
                    'wikipedia_article': citation.get('wikipedia_article'),
                    'citation_number': citation.get('citation_number')
                }
                
                is_real_problem = self.llm_triage.is_real_problem(
                    problem_type=ProblemType.BROKEN_LINK,
                    details=details,
                    citation_context=citation_context
                )
                
                if not is_real_problem:
                    self.log(f"LLM triage: False positive filtered for citation {citation['id']}", "debug")
                    return None
                
                # Generate enhanced explanation
                enhanced_details = self.llm_triage.explain_finding(
                    problem_type=ProblemType.BROKEN_LINK,
                    details=details,
                    citation_context=citation_context
                )
                finding['details'] = enhanced_details
            
            return finding
        
        return None
    
    def run(self, days: int = 7, limit: int = 100):
        """
        Run the broken link agent.
        
        Args:
            days: Check citations not checked in last N days
            limit: Maximum number of citations to check
        """
        self.log("Starting Broken Link Agent", "info")
        
        citations = get_citations_needing_check(days, limit=limit)
        self.log(f"Found {len(citations)} citations to check", "info")
        
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
                    self.log(f"Found broken link: {citation.get('source_url')}", "info")
                
                # Update last_checked timestamp
                update_citation_last_checked(citation['id'])
                checked_count += 1
            except Exception as e:
                self.log(f"Error checking citation {citation.get('id')}: {e}", "error")
                continue
        
        self.log(f"Completed: Checked {checked_count} citations, found {findings_count} broken links", "info")


if __name__ == "__main__":
    agent = BrokenLinkAgent()
    agent.run()
