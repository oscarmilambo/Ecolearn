#!/usr/bin/env python
"""
Reset admin credentials for Render deployment
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

def reset_admin_credentials():
    """Reset admin credentials"""
    print("🔧 Resetting admin credentials...")
    
    User = get_user_model()
    
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Check if CustomUser table exists
    try:
        user_count = User.objects.count()
        print(f"✅ CustomUser table accessible - {user_count} users found")
    except Exception as e:
        print(f"❌ CustomUser table issue: {e}")
        return False
    
    # Delete existing admin users
    try:
        admin_users = User.objects.filter(is_superuser=True)
        admin_count = admin_users.count()
        if admin_count > 0:
            admin_users.delete()
            print(f"🗑️  Deleted {admin_count} existing admin users")
    except Exception as e:
        print(f"⚠️  Could not delete existing admin users: {e}")
    
    # Create new admin user
    try:
        admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@ecolearn.com'  # Add email if required
        )
        print("✅ New admin user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@ecolearn.com")
        
        # Verify the user was created
        if admin_user.check_password('admin123'):
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Admin user creation failed: {e}")
        return False
    
    # Test authentication
    try:
        from django.contrib.auth import authenticate
        user = authenticate(username='admin', password='admin123')
        if user:
            print("✅ Authentication test successful")
            print(f"   User ID: {user.id}")
            print(f"   Is superuser: {user.is_superuser}")
            print(f"   Is staff: {user.is_staff}")
        else:
            print("❌ Authentication test failed")
            return False
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False
    
    print("🎉 Admin credentials reset completed successfully!")
    return True

if __name__ == '__main__':
    success = reset_admin_credentials()
    sys.exit(0 if success else 1)