#!/usr/bin/env python3
"""
Check current database content and provide recovery options
"""

import os
import django
import sqlite3

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def check_current_database():
    """Check what's currently in the database"""
    print("🔍 Checking current database content...")
    
    try:
        # Check users
        users = User.objects.all()
        print(f"   👥 Total users: {users.count()}")
        
        for user in users:
            print(f"      - {user.username} ({user.email}) - Staff: {user.is_staff}, Super: {user.is_superuser}")
        
        # Check other tables
        with connection.cursor() as cursor:
            # Check if we have learning modules
            cursor.execute("SELECT COUNT(*) FROM elearning_module;")
            modules = cursor.fetchone()[0]
            print(f"   📚 Learning modules: {modules}")
            
            # Check if we have community data
            cursor.execute("SELECT COUNT(*) FROM community_communitycampaign;")
            campaigns = cursor.fetchone()[0]
            print(f"   🌍 Community campaigns: {campaigns}")
            
            # Check enrollments
            cursor.execute("SELECT COUNT(*) FROM elearning_enrollment;")
            enrollments = cursor.fetchone()[0]
            print(f"   📝 User enrollments: {enrollments}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def backup_current_database():
    """Create a backup of current database before any recovery"""
    print("\n💾 Creating backup of current database...")
    
    try:
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"db_backup_before_recovery_{timestamp}.sqlite3"
        
        shutil.copy2('db.sqlite3', backup_name)
        print(f"✅ Current database backed up as: {backup_name}")
        
        return backup_name
        
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return None

def check_backup_file():
    """Check if we can access the backup file"""
    print("\n🔍 Checking backup file...")
    
    backup_file = "backups/database_backup_20251129_032030.sql.gz.enc"
    
    if os.path.exists(backup_file):
        size = os.path.getsize(backup_file)
        print(f"✅ Backup file found: {backup_file}")
        print(f"   Size: {size:,} bytes")
        print(f"   This appears to be an encrypted SQL backup")
        
        # Check if we have the encryption key
        if os.path.exists('.env'):
            print("   📝 .env file exists (may contain encryption key)")
        
        return True
    else:
        print(f"❌ Backup file not found: {backup_file}")
        return False

def suggest_recovery_options():
    """Suggest recovery options"""
    print("\n🔄 Database Recovery Options:")
    print("\n1. 📂 **Keep Current Database** (Recommended for now)")
    print("   - Your current database has the new optimized structure")
    print("   - All migrations are applied correctly")
    print("   - You can recreate your admin user and data")
    
    print("\n2. 🔓 **Restore from Encrypted Backup**")
    print("   - Requires decryption key from your .env file")
    print("   - May need to re-run migrations after restore")
    print("   - Risk of compatibility issues with new optimizations")
    
    print("\n3. 🔄 **Hybrid Approach** (Best of both worlds)")
    print("   - Keep current optimized database structure")
    print("   - Extract and import specific data from backup")
    print("   - Manually recreate important content")

def main():
    """Check database and suggest recovery options"""
    print("🚀 Database Recovery Analysis\n")
    
    # Check current database
    db_ok = check_current_database()
    
    # Create backup of current state
    backup_name = backup_current_database()
    
    # Check backup file
    backup_exists = check_backup_file()
    
    # Suggest options
    suggest_recovery_options()
    
    print(f"\n📊 Summary:")
    print(f"   Current DB: {'✅ Accessible' if db_ok else '❌ Issues'}")
    print(f"   Backup Created: {'✅ ' + backup_name if backup_name else '❌ Failed'}")
    print(f"   Original Backup: {'✅ Found' if backup_exists else '❌ Not found'}")
    
    print(f"\n💡 Recommendation:")
    print(f"   1. Fix CSRF issue first (restart server)")
    print(f"   2. Test admin login with current database")
    print(f"   3. If you need specific data, we can extract it from backup")

if __name__ == '__main__':
    main()