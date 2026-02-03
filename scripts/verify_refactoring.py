#!/usr/bin/env python3
"""Verify that the refactoring was applied correctly."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verify_broken_link_agent():
    """Verify BrokenLinkAgent has the correct attributes."""
    print("Verifying BrokenLinkAgent...")
    
    try:
        from agents.broken_link_agent import BrokenLinkAgent
        
        # Check imports
        import inspect
        source = inspect.getsource(BrokenLinkAgent.__init__)
        
        # Check for old code
        if 'self.session' in source:
            print("❌ ERROR: Still has old 'self.session' code")
            return False
        
        if 'self.last_request_time' in source:
            print("❌ ERROR: Still has old 'self.last_request_time' code")
            return False
        
        if '_rate_limit' in source:
            print("❌ ERROR: Still has old '_rate_limit' method")
            return False
        
        # Check for new code
        if 'HTTPClient' not in source:
            print("❌ ERROR: Missing 'HTTPClient' in __init__")
            return False
        
        if 'self.client' not in source:
            print("❌ ERROR: Missing 'self.client' in __init__")
            return False
        
        # Try to instantiate
        agent = BrokenLinkAgent()
        
        # Check attributes
        if not hasattr(agent, 'client'):
            print("❌ ERROR: Agent instance doesn't have 'client' attribute")
            return False
        
        if not hasattr(agent, 'llm_triage'):
            print("❌ ERROR: Agent instance doesn't have 'llm_triage' attribute")
            return False
        
        print("✅ PASS: BrokenLinkAgent is correctly refactored")
        print(f"   - Has 'client' attribute: {hasattr(agent, 'client')}")
        print(f"   - Client type: {type(agent.client).__name__}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_imports():
    """Verify all required imports are available."""
    print("\nVerifying imports...")
    
    try:
        from core.utils import HTTPClient, RateLimiter
        from core.constants import ProblemType, Severity
        from core.logger import get_logger
        
        print("✅ PASS: All core modules import correctly")
        return True
    except ImportError as e:
        print(f"❌ ERROR: Import failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("WikiVerify Refactoring Verification")
    print("=" * 60)
    
    results = []
    
    results.append(verify_imports())
    results.append(verify_broken_link_agent())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL CHECKS PASSED")
        print("\nIf you're still seeing errors, try:")
        print("1. Clear Python cache: find . -type d -name __pycache__ -exec rm -r {} +")
        print("2. Restart your Python process/script")
        print("3. Make sure you're using the updated code")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
