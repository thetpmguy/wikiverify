"""Test script to import a single article and verify it works."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.wikipedia_api import WikipediaAPI
from core.parser import CitationParser
from core.database import save_citation, execute_query


def test_import_article(article_title: str = "Aspirin"):
    """Test importing a single article."""
    print(f"Testing import for article: {article_title}")
    print("=" * 50)
    
    # Step 1: Fetch article
    print("\n1. Fetching article from Wikipedia...")
    api = WikipediaAPI()
    article_data = api.get_article_content(article_title)
    
    if not article_data:
        print(f"✗ Could not fetch article: {article_title}")
        return False
    
    print(f"✓ Article fetched: {article_data['title']}")
    
    # Step 2: Parse citations
    print("\n2. Parsing citations...")
    parser = CitationParser()
    citations = parser.parse_article(
        article_data['title'],
        article_data['text'],
        'en'
    )
    
    print(f"✓ Found {len(citations)} citations")
    
    if not citations:
        print("⚠ No citations found. This might be normal for some articles.")
        return True
    
    # Step 3: Save to database
    print("\n3. Saving citations to database...")
    saved_count = 0
    for citation in citations[:5]:  # Save first 5 for testing
        try:
            citation_id = save_citation(citation)
            saved_count += 1
            print(f"  ✓ Saved citation #{citation.get('citation_number')} (ID: {citation_id})")
            if citation.get('source_url'):
                print(f"    URL: {citation['source_url'][:60]}...")
            if citation.get('source_doi'):
                print(f"    DOI: {citation['source_doi']}")
        except Exception as e:
            print(f"  ✗ Error saving citation: {e}")
    
    print(f"\n✓ Saved {saved_count} citations")
    
    # Step 4: Verify in database
    print("\n4. Verifying in database...")
    try:
        result = execute_query(
            "SELECT COUNT(*) as count FROM citations WHERE wikipedia_article = %s",
            (article_data['title'],)
        )
        count = result[0]['count'] if result else 0
        print(f"✓ Found {count} citations in database for this article")
    except Exception as e:
        print(f"✗ Error querying database: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ Test import successful!")
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test WikiVerify import')
    parser.add_argument(
        'article',
        nargs='?',
        default='Aspirin',
        help='Wikipedia article title to import (default: Aspirin)'
    )
    
    args = parser.parse_args()
    
    success = test_import_article(args.article)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
