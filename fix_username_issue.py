#!/usr/bin/env python3
"""
Fix Username Issue - Update truncated usernames to use full names
This script fixes the issue where usernames like "user_edwa" should be "edward.jere"
"""

import os
import sys
import django
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from accounts.models import CustomUser

def fix_usernames():
    """Fix usernames to use full names instead of truncated versions"""
    print("🔍 Checking for users with auto-generated usernames...")
    
    # Find users with auto-generated usernames (user_xxxx pattern)
    users_to_fix = CustomUser.objects.filter(username__startswith='user_')
    
    if not users_to_fix.exists():
        print("✅ No users found with auto-generated usernames")
        return
    
    print(f"📋 Found {users_to_fix.count()} users with auto-generated usernames:")
    
    fixed_count = 0
    
    for user in users_to_fix:
        if user.first_name and user.last_name:
            # Generate new username from full name
            first_name = user.first_name.strip()
            last_name = user.last_name.strip()
            
            # Create username from full name (e.g., "Edward Jere" -> "edward.jere")
            base_username = f"{first_name.lower()}.{last_name.lower()}".replace(' ', '.')
            
            # Remove any special characters except dots and underscores
            base_username = re.sub(r'[^a-z0-9._]', '', base_username)
            
            # Ensure unique username
            counter = 1
            new_username = base_username
            while CustomUser.objects.filter(username=new_username).exists():
                new_username = f"{base_username}{counter}"
                counter += 1
            
            # Update the user
            old_username = user.username
            user.username = new_username
            user.save()
            
            print(f"   ✅ Fixed: '{old_username}' → '{new_username}' ({user.get_full_name()})")
            fixed_count += 1
        else:
            print(f"   ⚠️  Skipped: {user.username} (missing first/last name)")
    
    print(f"\n🎉 Fixed {fixed_count} usernames!")
    
    # Show all current users
    print("\n📋 Current users in system:")
    for user in CustomUser.objects.all().order_by('date_joined'):
        print(f"   👤 {user.username} - {user.get_full_name()} ({user.email})")

def create_test_user():
    """Create a test user to verify the fix works"""
    print("\n🧪 Creating test user 'Edward Jere'...")
    
    # Check if user already exists
    if CustomUser.objects.filter(first_name='Edward', last_name='Jere').exists():
        print("   ⚠️  User 'Edward Jere' already exists")
        return
    
    # Create user with the new logic
    first_name = 'Edward'
    last_name = 'Jere'
    
    # Generate username from full name
    base_username = f"{first_name.lower()}.{last_name.lower()}".replace(' ', '.')
    base_username = re.sub(r'[^a-z0-9._]', '', base_username)
    
    # Ensure unique username
    counter = 1
    username = base_username
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create the user
    user = CustomUser.objects.create_user(
        username=username,
        email='edward.jere@example.com',
        password='testpass123',
        first_name=first_name,
        last_name=last_name,
        is_active=True
    )
    
    print(f"   ✅ Created test user: '{username}' - {user.get_full_name()}")
    print(f"   📧 Email: {user.email}")
    print(f"   🔑 Password: testpass123")

if __name__ == '__main__':
    print("🚀 Starting Username Fix Script...")
    print("=" * 50)
    
    try:
        # Fix existing users
        fix_usernames()
        
        # Create test user
        create_test_user()
        
        print("\n" + "=" * 50)
        print("✅ Username fix completed successfully!")
        print("\n💡 Users can now login with their proper usernames:")
        print("   - 'Edward Jere' will have username 'edward.jere'")
        print("   - Login will work with the full name-based username")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()