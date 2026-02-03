"""Content extraction from web pages."""
from bs4 import BeautifulSoup
import re
from typing import Optional
from core.logger import get_logger

logger = get_logger(__name__)


class ContentExtractor:
    """Extracts main content from web pages, removing boilerplate."""
    
    def __init__(self):
        """Initialize the content extractor."""
        # Common tags to remove
        self.boilerplate_tags = [
            'nav', 'header', 'footer', 'aside', 'sidebar',
            'script', 'style', 'noscript', 'iframe',
            'advertisement', 'ads', 'social', 'share'
        ]
        
        # Common class/id patterns for boilerplate
        self.boilerplate_patterns = [
            re.compile(r'nav', re.I),
            re.compile(r'header', re.I),
            re.compile(r'footer', re.I),
            re.compile(r'sidebar', re.I),
            re.compile(r'advertisement', re.I),
            re.compile(r'comment', re.I),
            re.compile(r'cookie', re.I),
        ]
    
    def extract_text(self, html: str) -> Optional[str]:
        """
        Extract main text content from HTML.
        
        Args:
            html: HTML content
        
        Returns:
            Extracted text or None if error
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'noscript']):
                element.decompose()
            
            # Remove boilerplate tags
            for tag_name in self.boilerplate_tags:
                for element in soup.find_all(tag_name):
                    element.decompose()
            
            # Remove elements with boilerplate classes/ids
            for element in soup.find_all(class_=self._is_boilerplate_class):
                element.decompose()
            
            for element in soup.find_all(id=self._is_boilerplate_id):
                element.decompose()
            
            # Try to find main content area
            # Common selectors for main content
            main_selectors = [
                'main',
                'article',
                '[role="main"]',
                '.content',
                '.main-content',
                '#content',
                '#main-content',
                '.post-content',
                '.entry-content'
            ]
            
            main_content = None
            for selector in main_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.find('body')
            
            if not main_content:
                return None
            
            # Extract text
            text = main_content.get_text(separator=' ', strip=True)
            
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            return text
        except Exception as e:
            logger.error(f"Error extracting content: {e}")
            return None
    
    def _is_boilerplate_class(self, class_name):
        """Check if a class name indicates boilerplate."""
        if not class_name:
            return False
        class_str = ' '.join(class_name) if isinstance(class_name, list) else str(class_name)
        return any(pattern.search(class_str) for pattern in self.boilerplate_patterns)
    
    def _is_boilerplate_id(self, id_name):
        """Check if an ID indicates boilerplate."""
        if not id_name:
            return False
        return any(pattern.search(str(id_name)) for pattern in self.boilerplate_patterns)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using difflib.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity ratio (0.0 to 1.0)
        """
        from difflib import SequenceMatcher
        
        if not text1 or not text2:
            return 0.0
        
        matcher = SequenceMatcher(None, text1, text2)
        return matcher.ratio()
