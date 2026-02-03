"""PubMed E-utilities API integration."""
from typing import List, Dict, Any, Optional
from xml.etree import ElementTree as ET
from core.config import Config
from core.utils import HTTPClient
from core.logger import get_logger

logger = get_logger(__name__)


class PubMed:
    """Client for PubMed E-utilities API."""
    
    def __init__(self):
        """Initialize the PubMed client."""
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = Config.PUBMED_EMAIL or "contact@example.com"
        # PubMed requires max 3 requests/second (0.34s delay)
        self.client = HTTPClient(
            base_url=self.base_url,
            user_agent=f'WikiVerify/1.0 ({self.email})',
            rate_limit_delay=0.34,
            timeout=Config.CHECK_TIMEOUT
        )
    
    def search_retractions(self, doi: Optional[str] = None, 
                          pmid: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for retraction notices.
        
        Args:
            doi: DOI to search for
            pmid: PubMed ID to search for
        
        Returns:
            List of retraction records
        """
        # Build search query
        query_parts = ['retracted publication[pt]']
        
        if doi:
            # Normalize DOI
            doi_normalized = doi.lower().replace('doi:', '').strip()
            query_parts.append(f'"{doi_normalized}"[DOI]')
        elif pmid:
            query_parts.append(f'{pmid}[PMID]')
        else:
            return []
        
        query = ' AND '.join(query_parts)
        
        # Search
        search_url = "/esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmode': 'json',
            'email': self.email
        }
        
        response = self.client.get(search_url, params=params)
        if not response:
            return []
        
        try:
            data = response.json()
            pmids = data.get('esearchresult', {}).get('idlist', [])
            if not pmids:
                return []
            
            # Fetch details for each PMID
            return self.fetch_details(pmids)
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing PubMed search response: {e}")
            return []
    
    def fetch_details(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for PubMed IDs.
        
        Args:
            pmids: List of PubMed IDs
        
        Returns:
            List of paper details
        """
        if not pmids:
            return []
        
        fetch_url = "/efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': ','.join(pmids),
            'retmode': 'xml',
            'email': self.email
        }
        
        response = self.client.get(fetch_url, params=params)
        if not response:
            return []
        
        try:
            # Parse XML
            root = ET.fromstring(response.content)
            articles = []
            
            for article in root.findall('.//PubmedArticle'):
                article_data = self._parse_article_xml(article)
                if article_data:
                    articles.append(article_data)
            
            return articles
        except ET.ParseError as e:
            logger.error(f"Error parsing PubMed XML: {e}")
            return []
    
    def _parse_article_xml(self, article_elem) -> Optional[Dict[str, Any]]:
        """Parse a PubMed article XML element."""
        try:
            # Extract DOI
            doi = None
            for article_id in article_elem.findall('.//ArticleId'):
                if article_id.get('IdType') == 'doi':
                    doi = article_id.text
                    break
            
            # Extract title
            title_elem = article_elem.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else None
            
            # Extract publication date
            pub_date_elem = article_elem.find('.//PubDate')
            year = None
            if pub_date_elem is not None:
                year_elem = pub_date_elem.find('Year')
                if year_elem is not None:
                    year = year_elem.text
            
            # Extract retraction information
            pub_type_list = article_elem.find('.//PublicationTypeList')
            is_retraction = False
            if pub_type_list is not None:
                for pub_type in pub_type_list.findall('PublicationType'):
                    if pub_type.text and 'retraction' in pub_type.text.lower():
                        is_retraction = True
                        break
            
            if not is_retraction:
                return None
            
            return {
                'doi': doi.lower() if doi else None,
                'pmid': article_elem.find('.//PMID').text if article_elem.find('.//PMID') is not None else None,
                'title': title,
                'year': int(year) if year else None,
                'source': 'pubmed'
            }
        except Exception as e:
            logger.error(f"Error parsing article XML: {e}")
            return None
    
    def check_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Check if a DOI has been retracted according to PubMed.
        
        Args:
            doi: DOI to check
        
        Returns:
            Retraction record if found, None otherwise
        """
        retractions = self.search_retractions(doi=doi)
        return retractions[0] if retractions else None
