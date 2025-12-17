#!/usr/bin/env python3
"""
Simple Password Reset Test - Bypasses migration issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import CustomUser
from django.contrib.auth import authenticate

def test_password_reset_views():
    """Test password reset views without database operations"""
    print("🧪 Testing Password Reset Views")
    print("=" * 50)
    
    client = Client()
    
    # Test 1: Password reset request page
    print("\n1. Testing password reset request page...")
    try:
        response = client.get('/accounts/password-reset/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Password reset request page loads successfully")
            
            # Check for form elements
            content = response.content.decode('utf-8')
            if 'phone_number' in content:
                print("   ✅ Phone number field found in form")
            else:
                print("   ❌ Phone number field missing")
                
            if 'csrf' in content.lower():
                print("   ✅ CSRF protection present")
            else:
                print("   ❌ CSRF protection missing")
        else:
            print(f"   ❌ Failed to load page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error loading page: {e}")
    
    # Test 2: Password reset verify page (with session)
    print("\n2. Testing password reset verify page...")
    try:
        # Set session data to simulate coming from request page
        session = client.session
        session['reset_phone'] = '+260977123456'
        session.save()
        
        response = client.get('/accounts/password-reset/verify/')
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Password reset verify page loads successfully")
            
            content = response.content.decode('utf-8')
            if 'code' in content:
                print("   ✅ Code input field found")
            if 'new_password' in content:
                print("   ✅ New password field found")
            if 'confirm_password' in content:
                print("   ✅ Confirm password field found")
        else:
            print(f"   ❌ Failed to load verify page: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error loading verify page: {e}")

def test_existing_users():
    """Test with existing users in database"""
    print("\n3. Testing with existing users...")
    
    try:
        users = CustomUser.objects.all()
        print(f"   Found {users.count()} users in database")
        
        for user in users[:3]:  # Test first 3 users
            print(f"   - {user.username}: {user.email}, Active: {user.is_active}")
            
            # Test common passwords
            test_passwords = ['password123', 'admin123', 'user123', 'testpass123']
            
            for password in test_passwords:
                auth_result = authenticate(username=user.username, password=password)
                if auth_result:
                    print(f"     ✅ Working login: {user.username} / {password}")
                    break
            else:
                print(f"     ❌ No working password found for {user.username}")
                
    except Exception as e:
        print(f"   ❌ Error testing users: {e}")

def test_url_patterns():
    """Test URL patterns are working"""
    print("\n4. Testing URL patterns...")
    
    try:
        # Test URL reverse
        reset_url = reverse('accounts:password_reset_request')
        verify_url = reverse('accounts:password_reset_verify')
        
        print(f"   ✅ Reset request URL: {reset_url}")
        print(f"   ✅ Reset verify URL: {verify_url}")
        
    except Exception as e:
        print(f"   ❌ URL pattern error: {e}")

def create_working_user_simple():
    """Create a simple working user for testing"""
    print("\n5. Creating simple test user...")
    
    try:
        # Remove existing test user
        CustomUser.objects.filter(username='simpletest').delete()
        
        # Create user with minimal fields
        user = CustomUser(
            username='simpletest',
            email='simple@test.com',
            first_name='Simple',
            last_name='Test',
            is_active=True
        )
        user.set_password('simple123')
        user.save()
        
        print(f"   ✅ Created user: simpletest / simple123")
        
        # Test authentication
        auth_test = authenticate(username='simpletest', password='simple123')
        if auth_test:
            print("   ✅ Authentication test passed")
        else:
            print("   ❌ Authentication test failed")
            
        return user
        
    except Exception as e:
        print(f"   ❌ Error creating user: {e}")
        return None

if __name__ == '__main__':
    print("🔧 Simple Password Reset System Test")
    print("=" * 60)
    
    try:
        test_url_patterns()
        test_password_reset_views()
        test_existing_users()
        create_working_user_simple()
        
        print("\n" + "=" * 60)
        print("🎉 BASIC TESTS COMPLETED!")
        print("\nNext steps:")
        print("1. Try logging in with existing users")
        print("2. Use the password reset utility: python reset_user_password.py")
        print("3. Test password reset flow at /accounts/password-reset/")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()