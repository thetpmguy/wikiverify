"""Retraction Agent - Detects when cited papers have been retracted."""
from typing import Optional, Dict, Any
from agents.base_agent import BaseAgent
from core.database import get_citations_with_dois
from core.constants import ProblemType, Severity
from integrations.retraction_watch import RetractionWatch
from integrations.pubmed import PubMed
from integrations.crossref import CrossRef
from llm.triage import LLMTriage


class RetractionAgent(BaseAgent):
    """Agent that checks citations against retraction databases."""
    
    def __init__(self, use_llm_triage: bool = True):
        """
        Initialize the Retraction Agent.
        
        Args:
            use_llm_triage: Whether to use LLM triage (usually not needed for retractions, but available)
        """
        super().__init__("retraction_agent")
        self.retraction_watch = RetractionWatch()
        self.pubmed = PubMed()
        self.crossref = CrossRef()
        self.llm_triage = LLMTriage(enabled=use_llm_triage) if use_llm_triage else None
    
    def update_retraction_cache(self):
        """Update the retraction cache from all sources."""
        self.log("Updating retraction cache...", "info")
        count = self.retraction_watch.update_cache()
        self.log(f"Updated {count} retraction records", "info")
    
    def check_citation(self, citation: Dict[str, Any], use_apis: bool = False) -> Optional[Dict[str, Any]]:
        """
        Check a single citation for retractions.
        
        Args:
            citation: Citation dictionary from database
            use_apis: Whether to also check PubMed and CrossRef APIs (slower)
        
        Returns:
            Finding dictionary if retraction found, None otherwise
        """
        doi = citation.get('source_doi')
        if not doi:
            return None
        
        self.log(f"Checking citation {citation['id']} with DOI: {doi}", "debug")
        
        # First check cached Retraction Watch database (fast)
        retraction = self.retraction_watch.check_doi(doi)
        source = 'retraction_watch'
        
        # If not found and APIs enabled, check PubMed and CrossRef
        if not retraction and use_apis:
            # Check PubMed
            pubmed_result = self.pubmed.check_doi(doi)
            if pubmed_result:
                retraction = {
                    'doi': doi,
                    'paper_title': pubmed_result.get('title'),
                    'retraction_date': None,
                    'retraction_reason': 'Retraction notice found in PubMed',
                    'source': 'pubmed'
                }
                source = 'pubmed'
            else:
                # Check CrossRef
                crossref_result = self.crossref.check_retraction(doi)
                if crossref_result:
                    retraction = crossref_result
                    source = 'crossref'
        
        if retraction:
            details = f"Paper with DOI {doi} was retracted"
            if retraction.get('retraction_date'):
                details += f" on {retraction['retraction_date']}"
            if retraction.get('retraction_reason'):
                details += f". Reason: {retraction['retraction_reason']}"
            if retraction.get('paper_title'):
                details += f" Paper: {retraction['paper_title']}"
            details += f" (Source: {source})"
            
            finding = {
                'citation_id': citation['id'],
                'wikipedia_article': citation['wikipedia_article'],
                'problem_type': ProblemType.RETRACTION,
                'details': details,
                'severity': Severity.HIGH
            }
            
            # Use LLM to generate better explanation (retractions are always real problems)
            if self.llm_triage:
                citation_context = {
                    'source_doi': doi,
                    'source_title': citation.get('source_title') or retraction.get('paper_title'),
                    'wikipedia_article': citation.get('wikipedia_article'),
                    'citation_number': citation.get('citation_number')
                }
                
                # Generate enhanced explanation
                enhanced_details = self.llm_triage.explain_finding(
                    problem_type=ProblemType.RETRACTION,
                    details=details,
                    citation_context=citation_context
                )
                finding['details'] = enhanced_details
            
            return finding
        
        return None
    
    def run(self, update_cache: bool = True, use_apis: bool = False):
        """
        Run the retraction agent.
        
        Args:
            update_cache: Whether to update the retraction cache first
            use_apis: Whether to also check PubMed and CrossRef APIs (slower but more comprehensive)
        """
        self.log("Starting Retraction Agent", "info")
        
        # Update cache if requested
        if update_cache:
            self.update_retraction_cache()
        
        # Get all citations with DOIs
        citations = get_citations_with_dois()
        self.log(f"Found {len(citations)} citations with DOIs to check", "info")
        
        findings_count = 0
        
        for citation in citations:
            try:
                finding = self.check_citation(citation, use_apis=use_apis)
                
                if finding:
                    self.save_finding(
                        citation_id=finding['citation_id'],
                        wikipedia_article=finding['wikipedia_article'],
                        problem_type=finding['problem_type'],
                        details=finding['details'],
                        severity=finding['severity']
                    )
                    findings_count += 1
                    self.log(f"Found retracted paper: {citation.get('source_doi')}", "info")
            except Exception as e:
                self.log(f"Error checking citation {citation.get('id')}: {e}", "error")
                continue
        
        self.log(f"Completed: Checked {len(citations)} citations, found {findings_count} retractions", "info")


if __name__ == "__main__":
    agent = RetractionAgent()
    agent.run()
