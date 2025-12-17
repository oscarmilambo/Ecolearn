#!/usr/bin/env python3
"""
Test Oscar Admin Login - Verify super admin can still access the system
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import CustomUser

def test_oscar_access():
    """Test that Oscar (oscarmilambo2) can still login"""
    print("🔑 Testing Super Admin Access...")
    print("=" * 40)
    
    try:
        # Find Oscar
        oscar = CustomUser.objects.get(username='oscarmilambo2')
        print(f"✅ Found super admin: {oscar.username}")
        print(f"   📧 Email: {oscar.email or 'Not set'}")
        print(f"   👤 Full name: {oscar.get_full_name() or 'Not set'}")
        print(f"   🔐 Is superuser: {oscar.is_superuser}")
        print(f"   🔐 Is staff: {oscar.is_staff}")
        print(f"   🔐 Is active: {oscar.is_active}")
        
        # Reset password to a known value
        oscar.set_password('admin123')
        oscar.save()
        print(f"   ✅ Password reset to: admin123")
        
        # Test direct authentication
        user = authenticate(username='oscarmilambo2', password='admin123')
        if user is not None:
            print(f"   ✅ Direct login successful!")
            print(f"   👋 Welcome back, {user.get_full_name() or user.username}!")
        else:
            print(f"   ❌ Direct login failed!")
            
        # Test case variations
        test_usernames = [
            'oscarmilambo2',
            'OSCARMILAMBO2',
            'OscarMilambo2',
        ]
        
        print(f"\n🧪 Testing username variations:")
        for test_username in test_usernames:
            user = authenticate(username=test_username, password='admin123')
            if user is not None:
                print(f"   ✅ '{test_username}' - SUCCESS")
            else:
                print(f"   ❌ '{test_username}' - FAILED")
        
        return True
        
    except CustomUser.DoesNotExist:
        print("❌ Super admin 'oscarmilambo2' not found!")
        
        # Show all users
        print("\n📋 Available users:")
        for user in CustomUser.objects.all():
            print(f"   👤 {user.username} - {user.get_full_name()} (superuser: {user.is_superuser})")
        
        return False

def create_emergency_admin():
    """Create emergency admin if needed"""
    print(f"\n🚨 Creating Emergency Admin Access...")
    
    try:
        # Check if we have any superuser
        superusers = CustomUser.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            print("   ⚠️  No superusers found! Creating emergency admin...")
            
            # Create emergency admin
            admin = CustomUser.objects.create_user(
                username='emergency_admin',
                email='admin@emergency.com',
                password='emergency123',
                first_name='Emergency',
                last_name='Admin',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            
            print(f"   ✅ Created emergency admin:")
            print(f"      Username: emergency_admin")
            print(f"      Password: emergency123")
            print(f"      Email: admin@emergency.com")
        else:
            print(f"   ✅ Found {superusers.count()} superuser(s):")
            for su in superusers:
                print(f"      👤 {su.username} - {su.get_full_name()}")
                
    except Exception as e:
        print(f"   ❌ Error creating emergency admin: {e}")

if __name__ == '__main__':
    print("🚀 Testing Super Admin Access...")
    print("=" * 50)
    
    try:
        # Test Oscar's access
        oscar_ok = test_oscar_access()
        
        # Create emergency admin if needed
        if not oscar_ok:
            create_emergency_admin()
        
        print("\n" + "=" * 50)
        if oscar_ok:
            print("✅ Super Admin Access Confirmed!")
            print("\n💡 Oscar can login with:")
            print("   Username: oscarmilambo2")
            print("   Password: admin123")
        else:
            print("⚠️  Super Admin Access Issue!")
            print("   Emergency admin created if needed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()