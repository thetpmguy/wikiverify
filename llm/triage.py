"""LLM Triage Layer - Filters false positives using cheap LLM."""
from typing import Dict, Any, Optional
from core.config import Config
from core.logger import get_logger

logger = get_logger(__name__)


class LLMTriage:
    """Uses cheap LLM to quickly assess if a finding is worth reporting."""
    
    def __init__(self, enabled: bool = True):
        """
        Initialize LLM Triage.
        
        Args:
            enabled: Whether LLM triage is enabled (can be disabled if no API key)
        """
        self.enabled = enabled and bool(Config.OPENAI_API_KEY)
        self.client = None
        
        if self.enabled:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            except ImportError:
                logger.warning("openai package not installed. LLM triage disabled.")
                self.enabled = False
    
    def is_real_problem(self, problem_type: str, details: str, 
                       citation_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Use cheap LLM to determine if a finding is a real problem worth reporting.
        
        Args:
            problem_type: Type of problem (broken_link, retraction, source_change)
            details: Details about the problem
            citation_context: Optional citation information for context
        
        Returns:
            True if this is a real problem worth reporting, False if false positive
        """
        if not self.enabled or not self.client:
            # If LLM not available, default to reporting (conservative)
            return True
        
        try:
            # Build context for LLM
            context = f"Problem Type: {problem_type}\nDetails: {details}"
            
            if citation_context:
                if citation_context.get('source_title'):
                    context += f"\nSource: {citation_context['source_title']}"
                if citation_context.get('wikipedia_article'):
                    context += f"\nArticle: {citation_context['wikipedia_article']}"
            
            # Use GPT-4o-mini for cheap, fast triage
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a Wikipedia citation verification assistant. 
Your job is to quickly assess if a citation problem is real and worth reporting to editors.

Consider:
- Is this a permanent problem or temporary issue?
- Is this significant enough to warrant editor attention?
- Could this be a false positive (e.g., temporary server issue, minor formatting change)?

Respond with ONLY "yes" if this is a real problem worth reporting, or "no" if it's likely a false positive."""
                    },
                    {
                        "role": "user",
                        "content": f"""Assess this citation problem:

{context}

Is this a real problem worth reporting to Wikipedia editors? Respond with only "yes" or "no"."""
                    }
                ],
                max_tokens=10,
                temperature=0.1  # Low temperature for consistent yes/no answers
            )
            
            answer = response.choices[0].message.content.strip().lower()
            return answer.startswith('yes')
            
        except Exception as e:
            logger.warning(f"LLM triage failed: {e}. Defaulting to report finding.")
            # On error, default to reporting (conservative approach)
            return True
    
    def explain_finding(self, problem_type: str, details: str,
                       citation_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a human-readable explanation of a finding.
        
        Args:
            problem_type: Type of problem
            details: Details about the problem
            citation_context: Optional citation information
        
        Returns:
            Human-readable explanation
        """
        if not self.enabled or not self.client:
            return details  # Return original details if LLM not available
        
        try:
            context = f"Problem Type: {problem_type}\nDetails: {details}"
            
            if citation_context:
                if citation_context.get('source_title'):
                    context += f"\nSource: {citation_context['source_title']}"
                if citation_context.get('wikipedia_article'):
                    context += f"\nWikipedia Article: {citation_context['wikipedia_article']}"
                if citation_context.get('citation_number'):
                    context += f"\nCitation Number: {citation_context['citation_number']}"
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a Wikipedia citation verification assistant.
Generate a clear, concise explanation of a citation problem that Wikipedia editors can understand.
Focus on what the problem is and why it matters."""
                    },
                    {
                        "role": "user",
                        "content": f"""Explain this citation problem in 2-3 sentences:

{context}

Provide a clear explanation that helps Wikipedia editors understand the issue."""
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.warning(f"LLM explanation failed: {e}")
            return details  # Return original details on error
