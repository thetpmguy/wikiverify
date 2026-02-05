"""Script to verify WikiVerify setup."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_imports():
    """Check if all required modules can be imported."""
    print("Checking imports...")
    try:
        from core.config import Config
        from core.database import get_connection
        from integrations.wikipedia_api import WikipediaAPI
        # Note: Only Synthesizer Agent is used for retraction checking
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Make sure you've installed dependencies: pip install -r requirements.txt")
        return False

def check_database():
    """Check database connection."""
    print("\nChecking database connection...")
    try:
        from core.config import Config
        from core.database import get_connection
        
        if not Config.DATABASE_URL:
            print("✗ DATABASE_URL not set in .env file")
            return False
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("  Make sure:")
        print("  1. PostgreSQL is running")
        print("  2. DATABASE_URL is correct in .env file")
        print("  3. Database exists: createdb wikiverify")
        print("  4. Schema is set up: psql wikiverify < schema.sql")
        return False

def check_database_schema():
    """Check if database schema exists."""
    print("\nChecking database schema...")
    try:
        from core.database import execute_query
        
        # Check for required tables
        tables = ['citations', 'findings', 'retractions_cache']
        for table in tables:
            result = execute_query(
                f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
            )
            if not result or not result[0].get('exists'):
                print(f"✗ Table '{table}' not found")
                print("  Run: psql wikiverify < schema.sql")
                return False
        
        print("✓ All required tables exist")
        return True
    except Exception as e:
        print(f"✗ Schema check failed: {e}")
        return False

def check_config():
    """Check configuration."""
    print("\nChecking configuration...")
    try:
        from core.config import Config
        
        issues = []
        if not Config.DATABASE_URL:
            issues.append("DATABASE_URL not set")
        if Config.DATABASE_URL == "postgresql://user:password@localhost:5432/wikiverify":
            issues.append("DATABASE_URL still has default value - update .env file")
        
        if issues:
            print("⚠ Configuration issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✓ Configuration looks good")
        
        return True
    except Exception as e:
        print(f"✗ Config check failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("WikiVerify Setup Verification")
    print("=" * 50)
    print()
    
    checks = [
        ("Imports", check_imports),
        ("Configuration", check_config),
        ("Database Connection", check_database),
        ("Database Schema", check_database_schema),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name} check crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("Verification Summary")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All checks passed! WikiVerify is ready to use.")
        print("\nNext steps:")
        print("  1. Import articles: python scripts/initial_import.py")
        print("  2. Run synthesizer agent: python -m agents.synthesizer_agent")
        print("  3. Start scheduler: python scripts/scheduler.py --run-now")
    else:
        print("⚠ Some checks failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
