#!/usr/bin/env python3
"""
Fix Username to Full Name - Update usernames to use exact full names
This script changes usernames from "edward.jere" to "Edward Jere" (what user actually entered)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from accounts.models import CustomUser

def fix_usernames_to_fullname():
    """Fix usernames to use full names exactly as entered"""
    print("🔍 Updating usernames to use full names...")
    
    # Find users who have first_name and last_name but username doesn't match
    users_to_fix = []
    
    for user in CustomUser.objects.all():
        if user.first_name and user.last_name:
            expected_username = f"{user.first_name} {user.last_name}"
            if user.username != expected_username:
                users_to_fix.append((user, expected_username))
    
    if not users_to_fix:
        print("✅ All usernames already match full names")
        return
    
    print(f"📋 Found {len(users_to_fix)} users to update:")
    
    fixed_count = 0
    
    for user, expected_username in users_to_fix:
        # Check if the expected username is already taken by another user
        if CustomUser.objects.filter(username=expected_username).exclude(id=user.id).exists():
            print(f"   ⚠️  Skipped: '{expected_username}' already taken by another user")
            continue
        
        # Update the user
        old_username = user.username
        user.username = expected_username
        user.save()
        
        print(f"   ✅ Updated: '{old_username}' → '{expected_username}'")
        fixed_count += 1
    
    print(f"\n🎉 Updated {fixed_count} usernames!")
    
    # Show all current users
    print("\n📋 Current users in system:")
    for user in CustomUser.objects.all().order_by('date_joined'):
        full_name = user.get_full_name()
        if full_name:
            print(f"   👤 '{user.username}' - {full_name} ({user.email})")
        else:
            print(f"   👤 '{user.username}' - No full name ({user.email})")

def test_edward_login():
    """Test that Edward Jere can login with his full name"""
    print("\n🧪 Testing Edward Jere login with full name...")
    
    try:
        # Find Edward's user
        edward = CustomUser.objects.get(first_name='Edward', last_name='Jere')
        print(f"✅ Found user: '{edward.username}'")
        
        # Set a test password
        edward.set_password('testpass123')
        edward.save()
        print("   ✅ Set test password: testpass123")
        
        # Test authentication with full name
        from django.contrib.auth import authenticate
        user = authenticate(username=edward.username, password='testpass123')
        
        if user is not None:
            print(f"   ✅ Authentication successful with: '{edward.username}'")
            print(f"   👋 Welcome back, {user.get_full_name()}!")
        else:
            print(f"   ❌ Authentication failed with: '{edward.username}'")
            
    except CustomUser.DoesNotExist:
        print("❌ Edward Jere user not found")

if __name__ == '__main__':
    print("🚀 Starting Username to Full Name Fix...")
    print("=" * 50)
    
    try:
        # Fix usernames to use full names
        fix_usernames_to_fullname()
        
        # Test Edward's login
        test_edward_login()
        
        print("\n" + "=" * 50)
        print("✅ Username fix completed successfully!")
        print("\n💡 Users can now login with their full names:")
        print("   - Edward Jere logs in with: 'Edward Jere'")
        print("   - No more dots or special formatting")
        print("   - Exactly what they entered during registration")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()