#!/usr/bin/env python
"""
Test login functionality to debug authentication issues
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import CustomUser
from django.contrib.auth.hashers import check_password

def test_login():
    print("=== LOGIN FUNCTIONALITY TEST ===")
    
    # Create a test user with known credentials
    test_username = "logintest"
    test_password = "testpass123"
    
    # Check if user already exists
    try:
        user = CustomUser.objects.get(username=test_username)
        print(f"User {test_username} already exists")
    except CustomUser.DoesNotExist:
        # Create new test user
        user = CustomUser.objects.create_user(
            username=test_username,
            password=test_password,
            email="logintest@example.com"
        )
        print(f"Created test user: {test_username}")
    
    print(f"User active: {user.is_active}")
    print(f"User has usable password: {user.has_usable_password()}")
    
    # Test authentication
    print("\n=== AUTHENTICATION TEST ===")
    
    # Test with correct credentials
    auth_user = authenticate(username=test_username, password=test_password)
    if auth_user:
        print("✅ Authentication successful with correct credentials")
    else:
        print("❌ Authentication failed with correct credentials")
        
        # Debug: Check password manually
        if check_password(test_password, user.password):
            print("✅ Password hash verification successful")
        else:
            print("❌ Password hash verification failed")
    
    # Test with wrong password
    auth_user_wrong = authenticate(username=test_username, password="wrongpassword")
    if auth_user_wrong:
        print("❌ Authentication succeeded with wrong password (this is bad!)")
    else:
        print("✅ Authentication correctly failed with wrong password")
    
    # Test with non-existent user
    auth_user_nonexistent = authenticate(username="nonexistentuser", password="anypassword")
    if auth_user_nonexistent:
        print("❌ Authentication succeeded with non-existent user (this is bad!)")
    else:
        print("✅ Authentication correctly failed with non-existent user")
    
    print(f"\nTest user credentials for manual testing:")
    print(f"Username: {test_username}")
    print(f"Password: {test_password}")

if __name__ == "__main__":
    test_login()