#!/usr/bin/env python3
"""
Test script to verify the login functionality is working after migrations
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def test_database_schema():
    """Test if the database schema is correct"""
    print("🔍 Testing database schema...")
    
    # Check if gender column exists
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(accounts_customuser);")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"✅ CustomUser table columns: {column_names}")
        
        if 'gender' in column_names:
            print("✅ Gender column exists!")
        else:
            print("❌ Gender column missing!")
            
        return 'gender' in column_names

def test_user_creation():
    """Test creating a user"""
    print("\n👤 Testing user creation...")
    
    try:
        # Try to create a test user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ User created successfully: {user.username}")
        
        # Test user fields
        print(f"   - Email: {user.email}")
        print(f"   - Gender: {getattr(user, 'gender', 'Not set')}")
        print(f"   - Phone: {getattr(user, 'phone_number', 'Not set')}")
        
        # Clean up
        user.delete()
        print("✅ Test user cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Django EcoLearn Login System\n")
    
    schema_ok = test_database_schema()
    user_ok = test_user_creation()
    
    print(f"\n📊 Test Results:")
    print(f"   Database Schema: {'✅ PASS' if schema_ok else '❌ FAIL'}")
    print(f"   User Creation: {'✅ PASS' if user_ok else '❌ FAIL'}")
    
    if schema_ok and user_ok:
        print("\n🎉 All tests passed! Login system should work correctly.")
        print("   You can now:")
        print("   1. Visit http://127.0.0.1:8000/accounts/register/ to create an account")
        print("   2. Visit http://127.0.0.1:8000/accounts/login/ to login")
        print("   3. Visit http://127.0.0.1:8000/admin/ for admin interface")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")

if __name__ == '__main__':
    main()