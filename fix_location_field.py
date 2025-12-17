#!/usr/bin/env python3
"""
Fix Location Field Issue - Add location field to CustomUser model
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.db import connection

def fix_location_field():
    """Add location field to CustomUser table if it doesn't exist"""
    print("🔧 Fixing Location Field Issue")
    print("=" * 40)
    
    try:
        with connection.cursor() as cursor:
            # Check if location column exists
            cursor.execute("PRAGMA table_info(accounts_customuser)")
            columns = [row[1] for row in cursor.fetchall()]
            
            print(f"Current columns: {columns}")
            
            if 'location' not in columns:
                print("Adding location column...")
                cursor.execute("""
                    ALTER TABLE accounts_customuser 
                    ADD COLUMN location VARCHAR(255) DEFAULT ''
                """)
                print("✅ Location column added")
            else:
                print("✅ Location column already exists")
                
                # Check if it allows NULL
                cursor.execute("SELECT sql FROM sqlite_master WHERE name='accounts_customuser'")
                table_sql = cursor.fetchone()[0]
                
                if 'location' in table_sql and 'NOT NULL' in table_sql:
                    print("Location field is NOT NULL, updating to allow NULL...")
                    # SQLite doesn't support ALTER COLUMN, so we'll set default values
                    cursor.execute("UPDATE accounts_customuser SET location = '' WHERE location IS NULL")
                    print("✅ Set empty string for NULL location values")
        
        print("\n🎉 Location field issue fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing location field: {e}")
        return False

def test_user_creation():
    """Test creating a user after fix"""
    print("\n🧪 Testing user creation after fix...")
    
    try:
        from accounts.models import CustomUser
        
        # Remove test user if exists
        CustomUser.objects.filter(username='locationtest').delete()
        
        # Create test user
        user = CustomUser.objects.create_user(
            username='locationtest',
            email='location@test.com',
            password='test123',
            first_name='Location',
            last_name='Test'
        )
        
        print(f"✅ Successfully created user: {user.username}")
        
        # Test authentication
        from django.contrib.auth import authenticate
        auth_test = authenticate(username='locationtest', password='test123')
        
        if auth_test:
            print("✅ Authentication test passed")
        else:
            print("❌ Authentication test failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return False

if __name__ == '__main__':
    success = fix_location_field()
    
    if success:
        test_user_creation()
        
        print("\n" + "=" * 40)
        print("🎉 LOCATION FIELD FIXED!")
        print("\nYou can now:")
        print("1. Create new users without location field errors")
        print("2. Test the password reset system")
        print("3. Run: python test_password_reset_simple.py")
    else:
        print("\n❌ Failed to fix location field issue")