"""Citation parser for extracting information from Wikipedia markup."""
import re
import mwparserfromhell
from typing import List, Dict, Any, Optional
from core.constants import CITATION_TEMPLATES


class CitationParser:
    """Parser for extracting citation information from Wikipedia articles."""
    
    def __init__(self):
        """Initialize the citation parser."""
        self.doi_pattern = re.compile(r'10\.\d{4,}/[^\s<>"{}|\\^`\[\]]+', re.IGNORECASE)
    
    def normalize_doi(self, doi: str) -> Optional[str]:
        """
        Normalize a DOI string.
        
        Args:
            doi: DOI string (may include prefixes like 'doi:', 'DOI:', etc.)
        
        Returns:
            Normalized DOI or None if invalid
        """
        if not doi:
            return None
        
        # Remove common prefixes
        doi = re.sub(r'^(doi|DOI|doi:|DOI:)\s*', '', doi.strip())
        
        # Extract DOI pattern
        match = self.doi_pattern.search(doi)
        if match:
            return match.group(0).lower()
        
        return None
    
    def parse_citation_template(self, template: mwparserfromhell.nodes.Template) -> Dict[str, Any]:
        """
        Parse a citation template ({{cite journal}}, {{cite web}}, etc.).
        
        Args:
            template: mwparserfromhell template node
        
        Returns:
            Dictionary with extracted citation information
        """
        citation = {
            'template_name': template.name.strip().lower(),
            'source_url': None,
            'source_doi': None,
            'source_title': None,
            'source_authors': None,
            'source_journal': None,
            'source_year': None
        }
        
        # Extract parameters
        for param in template.params:
            param_name = param.name.strip().lower()
            param_value = param.value.strip()
            
            # URL
            if param_name in ['url', 'website', 'access-url']:
                citation['source_url'] = param_value
            
            # DOI
            elif param_name in ['doi', 'doi-access']:
                citation['source_doi'] = self.normalize_doi(param_value)
            
            # Title
            elif param_name in ['title', 'article-title', 'chapter']:
                citation['source_title'] = param_value
            
            # Authors
            elif param_name in ['author', 'authors', 'author1', 'author2', 'last', 'first']:
                if citation['source_authors']:
                    citation['source_authors'] += f"; {param_value}"
                else:
                    citation['source_authors'] = param_value
            
            # Journal
            elif param_name in ['journal', 'periodical', 'work', 'website']:
                citation['source_journal'] = param_value
            
            # Year
            elif param_name in ['year', 'date', 'publication-date']:
                year_match = re.search(r'\b(19|20)\d{2}\b', param_value)
                if year_match:
                    citation['source_year'] = int(year_match.group(0))
        
        return citation
    
    def extract_citations_from_text(self, wikitext: str) -> List[Dict[str, Any]]:
        """
        Extract citations from Wikipedia markup text.
        
        Args:
            wikitext: Wikipedia markup text
        
        Returns:
            List of citation dictionaries
        """
        citations = []
        parsed = mwparserfromhell.parse(wikitext)
        
        citation_number = 1
        for template in parsed.filter_templates():
            template_name = template.name.strip().lower()
            
            if any(cite_type in template_name for cite_type in CITATION_TEMPLATES):
                citation = self.parse_citation_template(template)
                citation['citation_number'] = citation_number
                citations.append(citation)
                citation_number += 1
        
        return citations
    
    def extract_external_links(self, wikitext: str) -> List[str]:
        """
        Extract external links from Wikipedia markup.
        
        Args:
            wikitext: Wikipedia markup text
        
        Returns:
            List of external URLs
        """
        parsed = mwparserfromhell.parse(wikitext)
        external_links = []
        
        for link in parsed.filter_external_links():
            external_links.append(link.url.strip())
        
        return external_links
    
    def parse_article(self, article_title: str, wikitext: str,
                     language: str = 'en') -> List[Dict[str, Any]]:
        """
        Parse a Wikipedia article and extract all citations.
        
        Args:
            article_title: Title of the Wikipedia article
            wikitext: Wikipedia markup text
            language: Language code (default: 'en')
        
        Returns:
            List of citation dictionaries with article context
        """
        citations = self.extract_citations_from_text(wikitext)
        
        # Add article context to each citation
        for citation in citations:
            citation['wikipedia_article'] = article_title
            citation['wikipedia_language'] = language
        
        return citations
