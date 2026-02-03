"""Base agent class for all WikiVerify agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from core.database import save_finding
from core.logger import get_logger
from core.constants import Severity, ProblemType


class BaseAgent(ABC):
    """Base class for all verification agents."""
    
    def __init__(self, name: str):
        """
        Initialize the agent.
        
        Args:
            name: Agent name
        """
        self.name = name
        self.logger = get_logger(f"agents.{name}")
    
    @abstractmethod
    def run(self, **kwargs):
        """
        Run the agent's main verification logic.
        
        Args:
            **kwargs: Agent-specific parameters
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement run()")
    
    def save_finding(self, citation_id: int, wikipedia_article: str,
                    problem_type: str, details: str, 
                    severity: str = Severity.MEDIUM) -> int:
        """
        Save a finding to the database.
        
        Args:
            citation_id: ID of the citation with the problem
            wikipedia_article: Name of the Wikipedia article
            problem_type: Type of problem (e.g., 'broken_link', 'retraction')
            details: Detailed description of the problem
            severity: Severity level ('low', 'medium', 'high')
        
        Returns:
            ID of the created finding
        """
        return save_finding(
            citation_id=citation_id,
            wikipedia_article=wikipedia_article,
            problem_type=problem_type,
            details=details,
            severity=severity
        )
    
    def log(self, message: str, level: str = "info"):
        """
        Log a message.
        
        Args:
            message: Message to log
            level: Log level ('debug', 'info', 'warning', 'error')
        """
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
