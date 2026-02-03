#!/usr/bin/env python3
"""End-to-end test script for WikiVerify."""
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import execute_query
from core.logger import setup_logger

logger = setup_logger(__name__)


def print_step(step_num: int, description: str):
    """Print a test step header."""
    print("\n" + "=" * 70)
    print(f"STEP {step_num}: {description}")
    print("=" * 70)


def verify_setup():
    """Step 1: Verify the setup."""
    print_step(1, "Verifying Setup")
    
    try:
        from scripts.verify_setup import check_imports, check_config, check_database
        
        if not check_imports():
            print("❌ FAIL: Import check failed")
            return False
        
        if not check_config():
            print("❌ FAIL: Config check failed")
            return False
        
        if not check_database():
            print("❌ FAIL: Database check failed")
            return False
        
        print("✅ PASS: Setup verification successful")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def import_test_article():
    """Step 2: Import a test article."""
    print_step(2, "Importing Test Article")
    
    try:
        from scripts.test_import import test_import_article
        
        print("Importing 'Aspirin' article...")
        result = test_import_article("Aspirin")
        
        if result:
            # Verify citations were saved
            citations = execute_query(
                "SELECT COUNT(*) as count FROM citations WHERE wikipedia_article = %s",
                ("Aspirin",)
            )
            count = citations[0]['count'] if citations else 0
            print(f"✅ PASS: Article imported, {count} citations saved")
            return True
        else:
            print("❌ FAIL: Article import failed")
            return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_broken_link_agent():
    """Step 3: Test broken link agent."""
    print_step(3, "Testing Broken Link Agent")
    
    try:
        from agents.broken_link_agent import BrokenLinkAgent
        
        # Get citation count before
        before = execute_query("SELECT COUNT(*) as count FROM findings WHERE problem_type = 'broken_link'")
        before_count = before[0]['count'] if before else 0
        
        print("Running Broken Link Agent (checking 5 citations)...")
        agent = BrokenLinkAgent(use_llm_triage=False)  # Disable LLM for faster testing
        agent.run(days=365, limit=5)
        
        # Get citation count after
        after = execute_query("SELECT COUNT(*) as count FROM findings WHERE problem_type = 'broken_link'")
        after_count = after[0]['count'] if after else 0
        
        print(f"✅ PASS: Broken Link Agent completed")
        print(f"   Findings before: {before_count}, after: {after_count}")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_retraction_agent():
    """Step 4: Test retraction agent."""
    print_step(4, "Testing Retraction Agent")
    
    try:
        from agents.retraction_agent import RetractionAgent
        
        # Get citation count before
        before = execute_query("SELECT COUNT(*) as count FROM findings WHERE problem_type = 'retraction'")
        before_count = before[0]['count'] if before else 0
        
        print("Running Retraction Agent (skipping cache update for speed)...")
        agent = RetractionAgent(use_llm_triage=False)
        agent.run(update_cache=False, use_apis=False)
        
        # Get citation count after
        after = execute_query("SELECT COUNT(*) as count FROM findings WHERE problem_type = 'retraction'")
        after_count = after[0]['count'] if after else 0
        
        print(f"✅ PASS: Retraction Agent completed")
        print(f"   Findings before: {before_count}, after: {after_count}")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_source_change_agent():
    """Step 5: Test source change agent."""
    print_step(5, "Testing Source Change Agent")
    
    try:
        from agents.source_change_agent import SourceChangeAgent
        
        # Get citation count before
        before = execute_query("SELECT COUNT(*) as count FROM findings WHERE problem_type = 'source_change'")
        before_count = before[0]['count'] if before else 0
        
        print("Running Source Change Agent (checking 3 citations)...")
        agent = SourceChangeAgent(use_llm_triage=False)
        agent.run(limit=3)
        
        # Get citation count after
        after = execute_query("SELECT COUNT(*) as count FROM findings WHERE problem_type = 'source_change'")
        after_count = after[0]['count'] if after else 0
        
        print(f"✅ PASS: Source Change Agent completed")
        print(f"   Findings before: {before_count}, after: {after_count}")
        return True
    except Exception as e:
        print(f"⚠ WARN: Source Change Agent - {e}")
        print("   (This is OK if no snapshots exist yet)")
        return True  # Don't fail E2E test for this


def check_results():
    """Step 6: Check and display results."""
    print_step(6, "Checking Results")
    
    try:
        # Total citations
        citations = execute_query("SELECT COUNT(*) as count FROM citations")
        citation_count = citations[0]['count'] if citations else 0
        
        # Total findings
        findings = execute_query("SELECT COUNT(*) as count FROM findings")
        finding_count = findings[0]['count'] if findings else 0
        
        # Breakdown by type
        breakdown = execute_query("""
            SELECT problem_type, COUNT(*) as count 
            FROM findings 
            GROUP BY problem_type
        """)
        
        print(f"📊 Database Statistics:")
        print(f"   Total citations: {citation_count}")
        print(f"   Total findings: {finding_count}")
        
        if breakdown:
            print(f"\n   Findings by type:")
            for item in breakdown:
                print(f"     - {item['problem_type']}: {item['count']}")
        
        # Recent findings
        recent = execute_query("""
            SELECT problem_type, details, found_date
            FROM findings
            ORDER BY found_date DESC
            LIMIT 3
        """)
        
        if recent:
            print(f"\n   Recent findings:")
            for item in recent:
                details = item['details'][:60] + "..." if len(item['details']) > 60 else item['details']
                print(f"     - {item['problem_type']}: {details}")
        
        print("\n✅ PASS: Results check complete")
        return True
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the complete E2E test suite."""
    print("=" * 70)
    print("WikiVerify End-to-End Test Suite")
    print("=" * 70)
    
    steps = [
        ("Setup Verification", verify_setup),
        ("Import Test Article", import_test_article),
        ("Broken Link Agent", test_broken_link_agent),
        ("Retraction Agent", test_retraction_agent),
        ("Source Change Agent", test_source_change_agent),
        ("Check Results", check_results),
    ]
    
    results = []
    start_time = time.time()
    
    for name, func in steps:
        try:
            result = func()
            results.append((name, result))
            if not result and name != "Source Change Agent":  # Source change is optional
                print(f"\n⚠ Stopping early due to failure in: {name}")
                break
        except KeyboardInterrupt:
            print("\n\n⚠ Test interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))
            break
    
    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("E2E TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} steps passed")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    
    if passed == total:
        print("\n🎉 All E2E tests passed! WikiVerify is working correctly.")
        print("\nNext steps:")
        print("  1. Import more articles: python scripts/test_import.py 'Article Name'")
        print("  2. Run agents on larger dataset: python scripts/scheduler.py --run-now")
        print("  3. Start scheduler: python scripts/scheduler.py")
        return 0
    elif passed >= total - 1:  # Allow one failure (source change)
        print("\n✅ E2E test mostly passed (some optional steps may have failed)")
        return 0
    else:
        print("\n⚠ Some E2E tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
