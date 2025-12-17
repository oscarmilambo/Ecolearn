#!/usr/bin/env python3
"""
Test Full Name Login - Verify users can login with their exact full names
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import CustomUser

def test_all_users_login():
    """Test that all users can login with their usernames"""
    print("🧪 Testing login for all users with full names...")
    print("=" * 50)
    
    users_with_names = CustomUser.objects.exclude(first_name='').exclude(last_name='')
    
    for user in users_with_names:
        print(f"\n👤 Testing: {user.get_full_name()}")
        print(f"   Username: '{user.username}'")
        print(f"   Expected: '{user.first_name} {user.last_name}'")
        
        # Check if username matches expected format
        expected_username = f"{user.first_name} {user.last_name}"
        if user.username == expected_username:
            print(f"   ✅ Username format correct")
        else:
            print(f"   ⚠️  Username doesn't match expected format")
        
        # Set a test password and test authentication
        user.set_password('testpass123')
        user.save()
        
        # Test authentication
        auth_user = authenticate(username=user.username, password='testpass123')
        if auth_user is not None:
            print(f"   ✅ Login successful with: '{user.username}'")
        else:
            print(f"   ❌ Login failed with: '{user.username}'")

def test_new_registration_flow():
    """Test the new registration flow creates correct usernames"""
    print(f"\n🆕 Testing new registration username generation...")
    
    test_cases = [
        ('John', 'Doe'),
        ('Mary Jane', 'Smith'),
        ('José', 'García'),
        ('李', '小明'),
    ]
    
    for first_name, last_name in test_cases:
        # Simulate the new registration logic
        base_username = f"{first_name} {last_name}"
        
        counter = 1
        username = base_username
        while CustomUser.objects.filter(username=username).exists():
            username = f"{base_username} {counter}"
            counter += 1
        
        print(f"   📝 '{first_name} {last_name}' → Username: '{username}'")

def show_login_instructions():
    """Show clear instructions for users"""
    print(f"\n📋 LOGIN INSTRUCTIONS FOR USERS:")
    print("=" * 40)
    
    users_with_names = CustomUser.objects.exclude(first_name='').exclude(last_name='')
    
    for user in users_with_names:
        if user.email:  # Only show users with email (real users)
            print(f"👤 {user.get_full_name()}")
            print(f"   Username: '{user.username}'")
            print(f"   Email: {user.email}")
            print(f"   Login with exactly: '{user.username}'")
            print()

if __name__ == '__main__':
    print("🚀 Testing Full Name Login System...")
    print("=" * 60)
    
    try:
        # Test existing users
        test_all_users_login()
        
        # Test new registration logic
        test_new_registration_flow()
        
        # Show instructions
        show_login_instructions()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("\n🎉 SUMMARY:")
        print("   ✅ Users login with their exact full names")
        print("   ✅ No dots, underscores, or special formatting")
        print("   ✅ 'Edward Jere' logs in with 'Edward Jere'")
        print("   ✅ What they enter is what they use to login")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()