"""
Project Niyati - Setup Verification Script
Verifies all environment configuration and database connections
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_variables():
    """Verify all required environment variables are set"""
    print("=" * 60)
    print("CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    required_vars = [
        'DATABASE_URL',
        'NEO4J_URI',
        'NEO4J_USER',
        'NEO4J_PASSWORD',
        'LLM_PROVIDER',
        'LLM_API_KEY',
        'JWT_SECRET',
        'CIRCUIT_BREAKER_THRESHOLD',
        'BATCH_SIZE'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            print(f"❌ {var}: NOT SET or using placeholder")
            missing_vars.append(var)
        else:
            # Mask sensitive values
            if 'KEY' in var or 'PASSWORD' in var or 'SECRET' in var:
                display_value = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
    
    print()
    if missing_vars:
        print(f"⚠️  Warning: {len(missing_vars)} environment variable(s) need configuration")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def check_dependencies():
    """Check if required Python packages are installed"""
    print("=" * 60)
    print("CHECKING PYTHON DEPENDENCIES")
    print("=" * 60)
    
    required_packages = [
        'langgraph',
        'neo4j',
        'interpret',
        'fastapi',
        'pydantic',
        'langchain_groq',
        'circuitbreaker',
        'sse_starlette',
        'uvicorn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: installed")
        except ImportError:
            print(f"❌ {package}: NOT installed")
            missing_packages.append(package)
    
    print()
    if missing_packages:
        print(f"⚠️  Missing {len(missing_packages)} package(s). Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def check_data_files():
    """Verify existing data files are accessible"""
    print("=" * 60)
    print("CHECKING DATA FILES")
    print("=" * 60)
    
    data_dir = Path(__file__).parent / 'data'
    required_files = [
        'e_invoices.csv',
        'eway_bills.csv',
        'entity_master.csv',
        'filing_history.csv',
        'purchase_register.csv',
        'returns_summary.csv',
        'feature_vectors.csv'
    ]
    
    missing_files = []
    for filename in required_files:
        filepath = data_dir / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"✅ {filename}: {size_kb:.1f} KB")
        else:
            print(f"❌ {filename}: NOT FOUND")
            missing_files.append(filename)
    
    print()
    if missing_files:
        print(f"⚠️  Missing {len(missing_files)} data file(s)")
        return False
    else:
        print("✅ All data files are accessible")
        return True

def check_model_files():
    """Verify trained EBM model is accessible"""
    print("=" * 60)
    print("CHECKING MODEL FILES")
    print("=" * 60)
    
    model_dir = Path(__file__).parent / 'model'
    required_files = [
        'daksha_ebm.pkl',
        'feature_engineering.py',
        'ebm_training.py'
    ]
    
    missing_files = []
    for filename in required_files:
        filepath = model_dir / filename
        if filepath.exists():
            if filename.endswith('.pkl'):
                size_kb = filepath.stat().st_size / 1024
                print(f"✅ {filename}: {size_kb:.1f} KB")
            else:
                print(f"✅ {filename}: exists")
        else:
            print(f"❌ {filename}: NOT FOUND")
            missing_files.append(filename)
    
    print()
    if missing_files:
        print(f"⚠️  Missing {len(missing_files)} model file(s)")
        return False
    else:
        print("✅ All model files are accessible")
        return True

def test_postgresql_connection():
    """Test PostgreSQL database connection"""
    print("=" * 60)
    print("TESTING POSTGRESQL CONNECTION")
    print("=" * 60)
    
    try:
        from sqlalchemy import create_engine, text
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url or database_url.startswith('sqlite'):
            print("⚠️  DATABASE_URL not configured for PostgreSQL")
            print("   Using SQLite fallback for development")
            return True
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ PostgreSQL connection successful")
            print(f"   Version: {version.split(',')[0]}")
            return True
            
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {str(e)}")
        print("   Make sure PostgreSQL is running (docker-compose up -d postgres)")
        return False

def test_neo4j_connection():
    """Test Neo4j database connection"""
    print("=" * 60)
    print("TESTING NEO4J CONNECTION")
    print("=" * 60)
    
    try:
        from neo4j import GraphDatabase
        
        uri = os.getenv('NEO4J_URI')
        user = os.getenv('NEO4J_USER')
        password = os.getenv('NEO4J_PASSWORD')
        
        if not all([uri, user, password]):
            print("❌ Neo4j credentials not configured")
            return False
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version")
            record = result.single()
            print(f"✅ Neo4j connection successful")
            print(f"   Version: {record['version']}")
            driver.close()
            return True
            
    except Exception as e:
        print(f"❌ Neo4j connection failed: {str(e)}")
        print("   Make sure Neo4j is running (docker-compose up -d neo4j)")
        return False

def main():
    """Run all verification checks"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "PROJECT NIYATI - SETUP VERIFICATION" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    results = {
        'Environment Variables': check_env_variables(),
        'Python Dependencies': check_dependencies(),
        'Data Files': check_data_files(),
        'Model Files': check_model_files(),
        'PostgreSQL Connection': test_postgresql_connection(),
        'Neo4j Connection': test_neo4j_connection()
    }
    
    print()
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check}")
    
    print()
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    if passed_count == total_count:
        print(f"🎉 All checks passed ({passed_count}/{total_count})")
        print()
        print("Next steps:")
        print("  1. Start services: docker-compose up -d")
        print("  2. Install dependencies: pip install -r requirements.txt")
        print("  3. Run backend: uvicorn app:app --reload")
        print("  4. Run frontend: cd frontend && npm run dev")
        return 0
    else:
        print(f"⚠️  {total_count - passed_count} check(s) failed ({passed_count}/{total_count} passed)")
        print()
        print("Please fix the issues above before proceeding.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
