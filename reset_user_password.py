#!/usr/bin/env python3
"""
Reset User Password - Fix Login Issues
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from accounts.models import CustomUser
from django.contrib.auth import authenticate

def reset_user_password():
    """Reset password for a specific user"""
    print("🔧 User Password Reset Tool")
    print("=" * 40)
    
    # Show all users
    print("\nAvailable users:")
    users = CustomUser.objects.all().order_by('username')
    
    for i, user in enumerate(users, 1):
        status = "✅ Active" if user.is_active else "❌ Inactive"
        role = "👑 Admin" if user.is_superuser else "👤 User"
        print(f"{i:2d}. {user.username:<15} | {user.email:<25} | {status} | {role}")
    
    print("\n" + "=" * 40)
    
    # Get user choice
    try:
        choice = input("Enter the number of the user to reset password for: ").strip()
        user_index = int(choice) - 1
        
        if 0 <= user_index < len(users):
            selected_user = users[user_index]
            print(f"\n✅ Selected user: {selected_user.username}")
            
            # Get new password
            new_password = input("Enter new password (or press Enter for 'password123'): ").strip()
            if not new_password:
                new_password = 'password123'
            
            # Reset password
            selected_user.set_password(new_password)
            selected_user.is_active = True  # Ensure user is active
            selected_user.save()
            
            print(f"\n🎉 Password reset successful!")
            print(f"Username: {selected_user.username}")
            print(f"New Password: {new_password}")
            print(f"User is active: {selected_user.is_active}")
            
            # Test the new password
            auth_test = authenticate(username=selected_user.username, password=new_password)
            if auth_test:
                print("✅ Password test successful - you can now log in!")
            else:
                print("❌ Password test failed - something went wrong")
            
        else:
            print("❌ Invalid selection")
            
    except (ValueError, IndexError):
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")

def create_easy_login_users():
    """Create some easy-to-remember login users"""
    print("\n🔧 Creating Easy Login Users...")
    
    easy_users = [
        {
            'username': 'admin',
            'email': 'admin@ecolearn.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_superuser': True,
            'is_staff': True
        },
        {
            'username': 'user',
            'email': 'user@ecolearn.com', 
            'password': 'user123',
            'first_name': 'Regular',
            'last_name': 'User',
            'is_superuser': False,
            'is_staff': False
        },
        {
            'username': 'test',
            'email': 'test@ecolearn.com',
            'password': 'test123',
            'first_name': 'Test',
            'last_name': 'User',
            'is_superuser': False,
            'is_staff': False
        }
    ]
    
    for user_data in easy_users:
        username = user_data['username']
        
        # Remove existing user if exists
        CustomUser.objects.filter(username=username).delete()
        
        # Create new user
        user = CustomUser.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        
        if user_data['is_superuser']:
            user.is_superuser = True
            user.is_staff = True
            user.save()
        
        print(f"✅ Created: {username} / {user_data['password']}")
        
        # Test login
        auth_test = authenticate(username=username, password=user_data['password'])
        if auth_test:
            print(f"   ✅ Login test passed")
        else:
            print(f"   ❌ Login test failed")
    
    print("\n🎉 Easy login users created!")
    print("You can now log in with:")
    print("- admin / admin123 (Admin access)")
    print("- user / user123 (Regular user)")
    print("- test / test123 (Test user)")

if __name__ == '__main__':
    print("Choose an option:")
    print("1. Reset existing user password")
    print("2. Create easy login users")
    print("3. Both")
    
    choice = input("\nEnter choice (1, 2, or 3): ").strip()
    
    if choice in ['1', '3']:
        reset_user_password()
    
    if choice in ['2', '3']:
        create_easy_login_users()
    
    print("\n" + "=" * 40)
    print("🎉 Done! Try logging in now.")