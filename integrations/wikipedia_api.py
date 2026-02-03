"""Wikipedia API integration for fetching articles and citations."""
from typing import List, Dict, Any, Optional
from core.config import Config
from core.utils import HTTPClient
from core.logger import get_logger

logger = get_logger(__name__)


class WikipediaAPI:
    """Client for Wikipedia MediaWiki API."""
    
    def __init__(self):
        """Initialize the Wikipedia API client."""
        self.base_url = Config.WIKIPEDIA_API_URL
        self.user_agent = Config.WIKIPEDIA_USER_AGENT
        self.client = HTTPClient(
            base_url=None,  # URLs are full paths
            user_agent=self.user_agent,
            rate_limit_delay=Config.RATE_LIMIT_DELAY,
            timeout=Config.CHECK_TIMEOUT
        )
    
    def get_article_content(self, article_title: str, language: str = 'en') -> Optional[Dict[str, Any]]:
        """
        Fetch article content from Wikipedia.
        
        Args:
            article_title: Title of the Wikipedia article
            language: Language code (default: 'en')
        
        Returns:
            Dictionary with article content and metadata, or None if not found
        """
        url = f"https://{language}.wikipedia.org/w/api.php"
        
        # First, get the raw wikitext (better for parsing citations)
        params = {
            'action': 'query',
            'titles': article_title,
            'prop': 'revisions',
            'rvprop': 'content',
            'rvslots': 'main',
            'format': 'json',
            'redirects': 1
        }
        
        response = self.client.get(url, params=params)
        if not response:
            return None
        
        try:
            data = response.json()
            
            if 'error' in data:
                logger.warning(f"API error for article {article_title}: {data.get('error')}")
                return None
            
            pages = data.get('query', {}).get('pages', {})
            if not pages:
                return None
            
            page = list(pages.values())[0]
            if 'missing' in page:
                logger.debug(f"Article {article_title} not found")
                return None
            
            # Get wikitext
            revisions = page.get('revisions', [])
            if not revisions:
                return None
            
            wikitext = revisions[0].get('slots', {}).get('main', {}).get('*', '')
            title = page.get('title', article_title)
            
            # Also get parsed content for externallinks
            params_parse = {
                'action': 'parse',
                'page': article_title,
                'prop': 'externallinks|references',
                'format': 'json',
                'redirects': 1
            }
            
            response_parse = self.client.get(url, params=params_parse)
            if not response_parse:
                # Return what we have even if second request fails
                return {
                    'title': title,
                    'text': wikitext,
                    'externallinks': [],
                    'references': []
                }
            
            data_parse = response_parse.json()
            
            return {
                'title': title,
                'text': wikitext,  # Raw wikitext is better for parsing
                'externallinks': data_parse.get('parse', {}).get('externallinks', []),
                'references': data_parse.get('parse', {}).get('references', [])
            }
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing response for {article_title}: {e}")
            return None
    
    def get_article_references(self, article_title: str, language: str = 'en') -> List[Dict[str, Any]]:
        """
        Get references section from a Wikipedia article.
        
        Args:
            article_title: Title of the Wikipedia article
            language: Language code (default: 'en')
        
        Returns:
            List of reference dictionaries
        """
        url = f"https://{language}.wikipedia.org/w/api.php"
        params = {
            'action': 'parse',
            'page': article_title,
            'prop': 'references',
            'format': 'json',
            'redirects': 1
        }
        
        response = self.client.get(url, params=params)
        if not response:
            return []
        
        try:
            data = response.json()
            
            if 'error' in data:
                logger.warning(f"API error fetching references for {article_title}")
                return []
            
            return data.get('parse', {}).get('references', [])
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing references for {article_title}: {e}")
            return []
    
    def search_articles(self, query: str, limit: int = 10, language: str = 'en') -> List[str]:
        """
        Search for Wikipedia articles.
        
        Args:
            query: Search query
            limit: Maximum number of results
            language: Language code (default: 'en')
        
        Returns:
            List of article titles
        """
        url = f"https://{language}.wikipedia.org/w/api.php"
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srlimit': limit,
            'format': 'json'
        }
        
        response = self.client.get(url, params=params)
        if not response:
            return []
        
        try:
            data = response.json()
            return [item['title'] for item in data.get('query', {}).get('search', [])]
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing search results for '{query}': {e}")
            return []
