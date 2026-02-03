"""Debug script to test citation parsing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.wikipedia_api import WikipediaAPI
from core.parser import CitationParser


def test_citation_parsing(article_title: str = "Aspirin"):
    """Test citation parsing for an article."""
    print(f"Testing citation parsing for: {article_title}")
    print("=" * 60)
    
    # Fetch article
    api = WikipediaAPI()
    print("\n1. Fetching article...")
    article_data = api.get_article_content(article_title)
    
    if not article_data:
        print("✗ Could not fetch article")
        return
    
    print(f"✓ Article fetched: {article_data['title']}")
    print(f"  Text length: {len(article_data.get('text', ''))} characters")
    print(f"  External links: {len(article_data.get('externallinks', []))}")
    print(f"  References count from API: {len(article_data.get('references', []))}")
    
    # Try parsing
    print("\n2. Parsing citations from text...")
    parser = CitationParser()
    
    # Extract citations
    citations = parser.extract_citations_from_text(article_data['text'])
    print(f"  Found {len(citations)} citations using parser")
    
    # Try parsing the full article
    print("\n3. Parsing full article...")
    full_citations = parser.parse_article(
        article_data['title'],
        article_data['text'],
        'en'
    )
    print(f"  Found {len(full_citations)} citations from parse_article")
    
    # Show sample citations
    if citations:
        print("\n4. Sample citations:")
        for i, cit in enumerate(citations[:3], 1):
            print(f"\n  Citation {i}:")
            print(f"    Template: {cit.get('template_name')}")
            print(f"    URL: {cit.get('source_url', 'None')}")
            print(f"    DOI: {cit.get('source_doi', 'None')}")
            print(f"    Title: {cit.get('source_title', 'None')[:50]}")
    else:
        print("\n4. No citations found")
        print("\n   Debugging:")
        print(f"   - Text contains 'cite': {'cite' in article_data.get('text', '').lower()}")
        print(f"   - Text contains '{{': {'{{' in article_data.get('text', '')}")
        print(f"   - Text contains 'references': {'references' in article_data.get('text', '').lower()}")
        
        # Try a different approach - get references section
        print("\n5. Trying alternative: Fetching references section...")
        refs = api.get_article_references(article_title)
        print(f"   References from API: {len(refs)}")
        if refs:
            print(f"   First reference: {str(refs[0])[:100]}")


def test_multiple_articles():
    """Test multiple articles to find one with citations."""
    articles = [
        "Aspirin",
        "Diabetes",
        "COVID-19",
        "Quantum mechanics",
        "Albert Einstein"
    ]
    
    print("Testing multiple articles to find citations...")
    print("=" * 60)
    
    api = WikipediaAPI()
    parser = CitationParser()
    
    for article in articles:
        print(f"\nTesting: {article}")
        article_data = api.get_article_content(article)
        if article_data:
            citations = parser.extract_citations_from_text(article_data['text'])
            print(f"  Found {len(citations)} citations")
            if citations:
                print(f"  ✓ {article} has citations!")
                return article
        print(f"  No citations found")
    
    return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test citation parsing')
    parser.add_argument('article', nargs='?', default='Aspirin', help='Article to test')
    parser.add_argument('--find', action='store_true', help='Test multiple articles to find one with citations')
    
    args = parser.parse_args()
    
    if args.find:
        result = test_multiple_articles()
        if result:
            print(f"\n✓ Found article with citations: {result}")
    else:
        test_citation_parsing(args.article)
