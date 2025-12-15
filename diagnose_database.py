#!/usr/bin/env python
"""
Diagnose database configuration issues
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')

def diagnose_database():
    """Diagnose database configuration"""
    print("🔍 Database Configuration Diagnosis")
    print("=" * 50)
    
    # Check environment variables
    database_url = os.environ.get('DATABASE_URL')
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"DEBUG mode: {debug_mode}")
    print(f"DATABASE_URL present: {bool(database_url)}")
    if database_url:
        # Mask sensitive parts of the URL
        masked_url = database_url[:20] + "***" + database_url[-10:] if len(database_url) > 30 else "***"
        print(f"DATABASE_URL (masked): {masked_url}")
    
    # Check if dj_database_url is available
    try:
        import dj_database_url
        print("✅ dj_database_url is available")
    except ImportError:
        print("❌ dj_database_url is NOT available")
        return False
    
    # Try to set up Django and check database config
    try:
        django.setup()
        from django.conf import settings
        
        db_config = settings.DATABASES['default']
        print(f"Database engine: {db_config['ENGINE']}")
        print(f"Database name: {db_config.get('NAME', 'Not specified')}")
        print(f"Database host: {db_config.get('HOST', 'Not specified')}")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Database connection successful")
            
        # Check if it's really PostgreSQL
        if 'postgresql' in db_config['ENGINE']:
            print("✅ Using PostgreSQL (correct for production)")
        elif 'sqlite' in db_config['ENGINE']:
            print("⚠️  Using SQLite (should be PostgreSQL in production)")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == '__main__':
    success = diagnose_database()
    sys.exit(0 if success else 1)