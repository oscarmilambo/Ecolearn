#!/usr/bin/env python3
"""
Script to create an admin user for Django admin access
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_admin_user():
    """Create an admin user"""
    print("🔧 Creating Django Admin User...")
    
    # Admin user details
    username = 'admin'
    email = 'admin@ecolearn.com'
    password = 'admin123'  # Change this to a secure password
    
    try:
        # Check if admin user already exists
        if User.objects.filter(username=username).exists():
            print(f"⚠️  User '{username}' already exists!")
            user = User.objects.get(username=username)
            print(f"   Email: {user.email}")
            print(f"   Is Staff: {user.is_staff}")
            print(f"   Is Superuser: {user.is_superuser}")
            return user
        
        # Create the admin user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Admin',
            last_name='User'
        )
        
        # Make the user a staff member and superuser
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        
        return user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return None

def create_test_user():
    """Create a regular test user"""
    print("\n👤 Creating Test User...")
    
    username = 'testuser'
    email = 'test@ecolearn.com'
    password = 'test123'
    
    try:
        if User.objects.filter(username=username).exists():
            print(f"⚠️  User '{username}' already exists!")
            return User.objects.get(username=username)
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
        
        print(f"✅ Test user created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        
        return user
        
    except Exception as e:
        print(f"❌ Error creating test user: {e}")
        return None

def main():
    """Create admin and test users"""
    print("🚀 Setting up Django EcoLearn Users\n")
    
    admin_user = create_admin_user()
    test_user = create_test_user()
    
    print(f"\n📊 Summary:")
    print(f"   Admin User: {'✅ Created' if admin_user else '❌ Failed'}")
    print(f"   Test User: {'✅ Created' if test_user else '❌ Failed'}")
    
    if admin_user:
        print(f"\n🎉 You can now access Django Admin:")
        print(f"   URL: http://127.0.0.1:8000/admin/")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        
    if test_user:
        print(f"\n👤 You can also test regular login:")
        print(f"   URL: http://127.0.0.1:8000/accounts/login/")
        print(f"   Username: testuser")
        print(f"   Password: test123")

if __name__ == '__main__':
    main()