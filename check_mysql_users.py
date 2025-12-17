#!/usr/bin/env python
"""
Check users in MySQL database
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from accounts.models import CustomUser

def check_users():
    print("=== MYSQL DATABASE USERS ===")
    
    total_users = CustomUser.objects.count()
    print(f"Total users: {total_users}")
    
    if total_users > 0:
        print("\nRecent users:")
        recent_users = CustomUser.objects.order_by('-date_joined')[:10]
        for user in recent_users:
            print(f"  - Username: {user.username}")
            print(f"    Email: {user.email or 'No email'}")
            print(f"    Active: {user.is_active}")
            print(f"    Last login: {user.last_login or 'Never'}")
            print(f"    Date joined: {user.date_joined}")
            print("    ---")
    
    # Test a specific user login
    print("\n=== TESTING LOGIN FUNCTIONALITY ===")
    from django.contrib.auth import authenticate
    
    # Get a recent user to test
    if total_users > 0:
        test_user = CustomUser.objects.order_by('-date_joined').first()
        print(f"Testing user: {test_user.username}")
        
        # Check if user has a usable password
        if test_user.has_usable_password():
            print("✅ User has a usable password")
        else:
            print("❌ User does not have a usable password")
        
        # Try to authenticate (this won't work without the actual password)
        print("Note: Cannot test actual authentication without knowing the password")

if __name__ == "__main__":
    check_users()