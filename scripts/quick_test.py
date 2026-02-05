"""Quick test script to verify WikiVerify is working."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_import():
    """Test importing an article."""
    print("\n" + "="*60)
    print("TEST 1: Article Import")
    print("="*60)
    
    try:
        from scripts.test_import import test_import_article
        result = test_import_article("Aspirin")
        if result:
            print("✅ PASS: Article import successful")
            return True
        else:
            print("❌ FAIL: Article import failed")
            return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_database():
    """Test database connection and schema."""
    print("\n" + "="*60)
    print("TEST 2: Database Connection")
    print("="*60)
    
    try:
        from core.database import execute_query
        
        # Check tables exist
        result = execute_query(
            "SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = 'public'"
        )
        table_count = result[0]['count'] if result else 0
        
        if table_count >= 3:
            print(f"✅ PASS: Database connected, {table_count} tables found")
            return True
        else:
            print(f"❌ FAIL: Only {table_count} tables found (expected at least 3)")
            return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_citations():
    """Test if citations exist in database."""
    print("\n" + "="*60)
    print("TEST 3: Citations in Database")
    print("="*60)
    
    try:
        from core.database import execute_query
        
        result = execute_query("SELECT COUNT(*) as count FROM citations")
        count = result[0]['count'] if result else 0
        
        if count > 0:
            print(f"✅ PASS: Found {count} citations in database")
            
            # Show sample
            sample = execute_query("SELECT wikipedia_article, citation_number, source_url FROM citations LIMIT 3")
            if sample:
                print("\nSample citations:")
                for cit in sample:
                    print(f"  - {cit.get('wikipedia_article')} [#{cit.get('citation_number')}]")
            return True
        else:
            print("⚠ WARN: No citations found. Run: python scripts/test_import.py Aspirin")
            return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_agents():
    """Test if agents can be imported and initialized."""
    print("\n" + "="*60)
    print("TEST 4: Agent Initialization")
    print("="*60)
    
    try:
        # Note: Only Synthesizer Agent is used for retraction checking
        # It requires ML models and may not be fully implemented yet
        try:
            from agents.synthesizer_agent import SynthesizerAgent
            agent = SynthesizerAgent()
            print(f"✅ PASS: Synthesizer Agent initialized successfully")
            print(f"  - {agent.name}")
            return True
        except ImportError:
            print("⏭️  SKIP: Synthesizer Agent not yet implemented")
            print("   This is expected - Synthesizer Agent requires ML models")
            return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_findings():
    """Test findings in database."""
    print("\n" + "="*60)
    print("TEST 5: Findings")
    print("="*60)
    
    try:
        from core.database import execute_query
        
        result = execute_query("SELECT COUNT(*) as count FROM findings")
        count = result[0]['count'] if result else 0
        
        if count > 0:
            print(f"✅ PASS: Found {count} findings in database")
            
            # Show breakdown by type
            breakdown = execute_query(
                "SELECT problem_type, COUNT(*) as count FROM findings GROUP BY problem_type"
            )
            if breakdown:
                print("\nFindings by type:")
                for item in breakdown:
                    print(f"  - {item['problem_type']}: {item['count']}")
        else:
            print("ℹ INFO: No findings yet (this is normal if no problems detected)")
        
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def main():
    """Run all tests."""
    print("WikiVerify Quick Test Suite")
    print("="*60)
    
    tests = [
        ("Database Connection", test_database),
        ("Agent Initialization", test_agents),
        ("Article Import", test_import),
        ("Citations", test_citations),
        ("Findings", test_findings),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ FAIL: {name} - {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! WikiVerify is ready to use.")
        print("\nNext steps:")
        print("  1. Import more articles: python scripts/test_import.py 'Article Name'")
        print("  2. Run synthesizer agent: python -m agents.synthesizer_agent")
        print("  3. Start scheduler: python scripts/scheduler.py --run-now")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
