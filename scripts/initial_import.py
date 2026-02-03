"""Script to import initial Wikipedia articles and citations."""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.wikipedia_api import WikipediaAPI
from core.parser import CitationParser
from core.database import save_citation


def import_article(article_title: str, language: str = 'en', verbose: bool = True):
    """
    Import a single Wikipedia article and its citations.
    
    Args:
        article_title: Title of the Wikipedia article
        language: Language code (default: 'en')
        verbose: Print progress messages
    
    Returns:
        Number of citations imported
    """
    if verbose:
        print(f"Importing: {article_title}")
    
    # Fetch article
    api = WikipediaAPI()
    article_data = api.get_article_content(article_title, language)
    
    if not article_data:
        if verbose:
            print(f"  Error: Could not fetch article")
        return 0
    
    # Parse citations
    parser = CitationParser()
    citations = parser.parse_article(
        article_data['title'],
        article_data['text'],
        language
    )
    
    if verbose:
        print(f"  Found {len(citations)} citations")
    
    # Save citations to database
    saved_count = 0
    for citation in citations:
        try:
            save_citation(citation)
            saved_count += 1
        except Exception as e:
            if verbose:
                print(f"  Error saving citation {citation.get('citation_number')}: {e}")
    
    if verbose:
        print(f"  Saved {saved_count} citations")
    
    return saved_count


def import_articles(article_titles: list, language: str = 'en', delay: float = 1.0):
    """
    Import multiple Wikipedia articles.
    
    Args:
        article_titles: List of article titles to import
        language: Language code (default: 'en')
        delay: Delay between articles in seconds (default: 1.0)
    
    Returns:
        Dictionary with import statistics
    """
    stats = {
        'total_articles': len(article_titles),
        'successful': 0,
        'failed': 0,
        'total_citations': 0
    }
    
    for i, title in enumerate(article_titles, 1):
        print(f"\n[{i}/{len(article_titles)}] Processing: {title}")
        
        try:
            count = import_article(title, language, verbose=True)
            stats['total_citations'] += count
            stats['successful'] += 1
        except Exception as e:
            print(f"  Error: {e}")
            stats['failed'] += 1
        
        # Rate limiting
        if i < len(article_titles):
            time.sleep(delay)
    
    return stats


def main():
    """Main entry point for the import script."""
    # Example: Import some medical articles
    # In production, this would read from a file or database
    medical_articles = [
        "Aspirin",
        "Diabetes",
        "Hypertension",
        "COVID-19"
    ]
    
    print("WikiVerify Initial Import")
    print("=" * 50)
    
    stats = import_articles(medical_articles, delay=1.0)
    
    print("\n" + "=" * 50)
    print("Import Complete")
    print(f"Articles processed: {stats['total_articles']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Total citations imported: {stats['total_citations']}")


if __name__ == "__main__":
    main()
