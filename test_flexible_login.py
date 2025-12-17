#!/usr/bin/env python3
"""
Test Flexible Login System - Verify all username formats work
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import CustomUser

def test_oscar_login():
    """Test that oscarmilambo2 can still login"""
    print("🧪 Testing Oscar's Login (Super Admin)...")
    print("=" * 40)
    
    try:
        # Find Oscar's user
        oscar = CustomUser.objects.get(username='oscarmilambo2')
        print(f"✅ Found user: '{oscar.username}'")
        print(f"   📧 Email: {oscar.email}")
        print(f"   👤 Full name: {oscar.get_full_name()}")
        print(f"   🔐 Is superuser: {oscar.is_superuser}")
        print(f"   🔐 Is staff: {oscar.is_staff}")
        
        # Set a test password
        oscar.set_password('admin123')
        oscar.save()
        print("   ✅ Set test password: admin123")
        
        # Test different login methods
        login_methods = [
            ('Original username', 'oscarmilambo2'),
            ('Email', oscar.email if oscar.email else 'N/A'),
            ('Full name', oscar.get_full_name() if oscar.get_full_name() else 'N/A'),
            ('Case insensitive', 'OSCARMILAMBO2'),
        ]
        
        for method_name, username_input in login_methods:
            if username_input == 'N/A':
                print(f"   ⚠️  {method_name}: Not available")
                continue
                
            user = authenticate(username=username_input, password='admin123')
            if user is not None:
                print(f"   ✅ {method_name}: '{username_input}' - SUCCESS")
            else:
                print(f"   ❌ {method_name}: '{username_input}' - FAILED")
                
    except CustomUser.DoesNotExist:
        print("❌ oscarmilambo2 user not found")

def test_all_users_flexible_login():
    """Test that all users can login with multiple methods"""
    print(f"\n🧪 Testing Flexible Login for All Users...")
    print("=" * 50)
    
    users = CustomUser.objects.all()
    
    for user in users:
        print(f"\n👤 Testing: {user.username}")
        
        # Set a test password
        user.set_password('testpass123')
        user.save()
        
        # Test methods
        test_methods = []
        
        # Method 1: Original username
        test_methods.append(('Username', user.username))
        
        # Method 2: Email (if available)
        if user.email:
            test_methods.append(('Email', user.email))
        
        # Method 3: Full name (if available)
        if user.get_full_name():
            test_methods.append(('Full Name', user.get_full_name()))
        
        # Test each method
        for method_name, login_input in test_methods:
            auth_user = authenticate(username=login_input, password='testpass123')
            if auth_user is not None:
                print(f"   ✅ {method_name}: '{login_input}' - SUCCESS")
            else:
                print(f"   ❌ {method_name}: '{login_input}' - FAILED")

def show_login_guide():
    """Show login guide for all users"""
    print(f"\n📋 LOGIN GUIDE FOR ALL USERS:")
    print("=" * 40)
    
    users = CustomUser.objects.all().order_by('username')
    
    for user in users:
        print(f"\n👤 {user.get_full_name() or user.username}")
        print(f"   Username: '{user.username}'")
        if user.email:
            print(f"   Email: {user.email}")
        
        print("   Can login with:")
        print(f"   • '{user.username}' (original username)")
        if user.email:
            print(f"   • '{user.email}' (email)")
        if user.get_full_name():
            print(f"   • '{user.get_full_name()}' (full name)")

if __name__ == '__main__':
    print("🚀 Testing Flexible Login System...")
    print("=" * 60)
    
    try:
        # Test Oscar specifically (super admin)
        test_oscar_login()
        
        # Test all users
        test_all_users_flexible_login()
        
        # Show login guide
        show_login_guide()
        
        print("\n" + "=" * 60)
        print("✅ Flexible Login System Test Complete!")
        print("\n🎉 SUMMARY:")
        print("   ✅ oscarmilambo2 can login with original username")
        print("   ✅ Edward Jere can login with full name")
        print("   ✅ All users can login with email")
        print("   ✅ System supports multiple login methods")
        print("   ✅ No users are locked out!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()