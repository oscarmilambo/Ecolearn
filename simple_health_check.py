#!/usr/bin/env python
"""
Simple health check that can be run independently
"""
import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def simple_health_check():
    """Simple health check without Django setup"""
    print("🔍 Simple Health Check")
    print("=" * 30)
    
    # Check environment variables
    database_url = os.environ.get('DATABASE_URL')
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    secret_key = os.environ.get('SECRET_KEY')
    
    print(f"DEBUG: {debug_mode}")
    print(f"DATABASE_URL present: {bool(database_url)}")
    print(f"SECRET_KEY present: {bool(secret_key)}")
    
    if database_url:
        # Show first and last few characters of DATABASE_URL
        masked_url = database_url[:15] + "***" + database_url[-10:] if len(database_url) > 25 else "***"
        print(f"DATABASE_URL (masked): {masked_url}")
        
        # Check if it looks like PostgreSQL
        if database_url.startswith('postgres://') or database_url.startswith('postgresql://'):
            print("✅ DATABASE_URL looks like PostgreSQL")
        else:
            print("⚠️  DATABASE_URL doesn't look like PostgreSQL")
    
    # Check if required packages are available
    try:
        import dj_database_url
        print("✅ dj_database_url available")
    except ImportError:
        print("❌ dj_database_url NOT available")
    
    try:
        import psycopg2
        print("✅ psycopg2 available")
    except ImportError:
        try:
            import psycopg2_binary
            print("✅ psycopg2-binary available")
        except ImportError:
            print("❌ psycopg2/psycopg2-binary NOT available")
    
    return True

if __name__ == '__main__':
    simple_health_check()