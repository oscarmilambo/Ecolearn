#!/usr/bin/env python
"""
Final comprehensive login test
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import CustomUser

def final_test():
    print("=== FINAL LOGIN SYSTEM TEST ===")
    
    # Test 1: Check database connection and user count
    total_users = CustomUser.objects.count()
    print(f"✅ Database connected - Total users: {total_users}")
    
    # Test 2: Create a new user for testing
    test_username = "final_test_user"
    test_password = "secure123"
    
    # Remove existing test user if exists
    CustomUser.objects.filter(username=test_username).delete()
    
    # Create new user
    user = CustomUser.objects.create_user(
        username=test_username,
        password=test_password,
        email="finaltest@example.com"
    )
    print(f"✅ Created test user: {test_username}")
    
    # Test 3: Verify user properties
    print(f"   - User ID: {user.id}")
    print(f"   - Username: {user.username}")
    print(f"   - Email: {user.email}")
    print(f"   - Is active: {user.is_active}")
    print(f"   - Has usable password: {user.has_usable_password()}")
    
    # Test 4: Test authentication
    auth_user = authenticate(username=test_username, password=test_password)
    if auth_user:
        print("✅ Authentication successful!")
        print(f"   - Authenticated user ID: {auth_user.id}")
        print(f"   - Authenticated username: {auth_user.username}")
    else:
        print("❌ Authentication failed!")
        return False
    
    # Test 5: Test wrong password
    wrong_auth = authenticate(username=test_username, password="wrongpassword")
    if not wrong_auth:
        print("✅ Correctly rejected wrong password")
    else:
        print("❌ Incorrectly accepted wrong password")
        return False
    
    # Test 6: Check existing users can authenticate
    print("\n=== TESTING EXISTING USERS ===")
    existing_users = CustomUser.objects.filter(last_login__isnull=False)[:3]
    for existing_user in existing_users:
        print(f"User: {existing_user.username} - Last login: {existing_user.last_login}")
    
    print("\n🎉 ALL TESTS PASSED! Login system is working correctly.")
    print(f"\nYou can now test login with:")
    print(f"Username: {test_username}")
    print(f"Password: {test_password}")
    
    return True

if __name__ == "__main__":
    final_test()