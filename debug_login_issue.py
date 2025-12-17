#!/usr/bin/env python3
"""
Debug Login Issue - Comprehensive Authentication Testing
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import CustomUser
from django.test import Client
from django.contrib.auth.hashers import check_password

def debug_login_issue():
    """Debug login authentication issues"""
    print("🔍 Debugging Login Authentication Issue")
    print("=" * 60)
    
    # Step 1: Check existing users
    print("\n1. Checking existing users in database...")
    users = CustomUser.objects.all()
    
    if not users.exists():
        print("   ❌ No users found in database!")
        print("   💡 You need to create a user first")
        return False
    
    print(f"   ✅ Found {users.count()} users:")
    for user in users:
        print(f"   - Username: '{user.username}'")
        print(f"     Email: '{user.email}'")
        print(f"     Phone: '{user.phone_number}'")
        print(f"     Active: {user.is_active}")
        print(f"     Staff: {user.is_staff}")
        print(f"     Superuser: {user.is_superuser}")
        print(f"     Has password: {bool(user.password)}")
        print(f"     Password hash: {user.password[:50]}..." if user.password else "     No password set!")
        print()
    
    # Step 2: Test authentication with each user
    print("\n2. Testing authentication for each user...")
    
    for user in users:
        print(f"\n   Testing user: {user.username}")
        
        # Test with common passwords
        test_passwords = [
            'testpass123',
            'password123',
            'admin123',
            'user123',
            '12345678',
            user.username,  # Sometimes password is same as username
        ]
        
        for password in test_passwords:
            auth_user = authenticate(username=user.username, password=password)
            if auth_user:
                print(f"   ✅ SUCCESS: Password '{password}' works for {user.username}")
                break
        else:
            print(f"   ❌ None of the test passwords worked for {user.username}")
            
            # Check if password is properly hashed
            if user.password:
                print(f"   🔍 Password hash starts with: {user.password[:20]}...")
                if user.password.startswith('pbkdf2_sha256$'):
                    print("   ✅ Password is properly hashed")
                else:
                    print("   ❌ Password may not be properly hashed")
            else:
                print("   ❌ No password set for this user")
    
    # Step 3: Test login form submission
    print("\n3. Testing login form submission...")
    
    client = Client()
    
    # Get login page first
    response = client.get('/accounts/login/')
    print(f"   Login page status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Login page loads successfully")
        
        # Check for CSRF token
        content = response.content.decode('utf-8')
        if 'csrfmiddlewaretoken' in content:
            print("   ✅ CSRF token found in login form")
        else:
            print("   ❌ CSRF token missing from login form")
    
    # Step 4: Create a test user and try login
    print("\n4. Creating test user and testing login...")
    
    # Clean up any existing test user
    CustomUser.objects.filter(username='testlogin').delete()
    
    # Create test user
    test_user = CustomUser.objects.create_user(
        username='testlogin',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    
    print(f"   ✅ Created test user: {test_user.username}")
    print(f"   Password hash: {test_user.password[:50]}...")
    
    # Test authentication
    auth_result = authenticate(username='testlogin', password='testpass123')
    if auth_result:
        print("   ✅ Test user authentication successful")
        
        # Test login via form
        login_response = client.post('/accounts/login/', {
            'username': 'testlogin',
            'password': 'testpass123'
        })
        
        print(f"   Login form response: {login_response.status_code}")
        
        if login_response.status_code == 302:
            print("   ✅ Login form submission successful (redirect)")
        else:
            print("   ❌ Login form submission failed")
            
    else:
        print("   ❌ Test user authentication failed")
    
    # Step 5: Check login view configuration
    print("\n5. Checking login view configuration...")
    
    from django.conf import settings
    print(f"   LOGIN_URL: {settings.LOGIN_URL}")
    print(f"   LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
    print(f"   AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
    
    # Check authentication backends
    print(f"   AUTHENTICATION_BACKENDS:")
    for backend in settings.AUTHENTICATION_BACKENDS:
        print(f"     - {backend}")
    
    print("\n" + "=" * 60)
    print("🎉 Login Debug Complete!")
    
    return True

def create_working_user():
    """Create a user that definitely works for testing"""
    print("\n🔧 Creating a guaranteed working test user...")
    
    # Remove any existing test user
    CustomUser.objects.filter(username='workinguser').delete()
    
    # Create user with explicit settings
    user = CustomUser(
        username='workinguser',
        email='working@example.com',
        first_name='Working',
        last_name='User',
        is_active=True,
        is_staff=False,
        is_superuser=False
    )
    user.set_password('password123')  # This ensures proper hashing
    user.save()
    
    print(f"✅ Created working user:")
    print(f"   Username: workinguser")
    print(f"   Password: password123")
    print(f"   Active: {user.is_active}")
    print(f"   Password hash: {user.password[:50]}...")
    
    # Test the user immediately
    auth_test = authenticate(username='workinguser', password='password123')
    if auth_test:
        print("✅ Working user authentication test PASSED")
    else:
        print("❌ Working user authentication test FAILED")
    
    return user

if __name__ == '__main__':
    debug_login_issue()
    create_working_user()
    
    print("\n" + "=" * 60)
    print("💡 TROUBLESHOOTING TIPS:")
    print("1. Try logging in with: workinguser / password123")
    print("2. Check if your user account is active (is_active=True)")
    print("3. Make sure password was set with user.set_password()")
    print("4. Clear browser cache and cookies")
    print("5. Check for CSRF token issues in browser dev tools")