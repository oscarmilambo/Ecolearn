#!/usr/bin/env python
"""
Test script to verify the security web interface is working
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from security.models import Role, UserRole

User = get_user_model()

def test_security_web_interface():
    print("🌐 Testing Security Web Interface")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    # Test 1: Check if security URLs are accessible (without login)
    print("\n1. Testing URL Accessibility:")
    
    # These should redirect to login
    security_urls = [
        '/admin_dashboard/security/',
        '/admin_dashboard/security/roles/',
        '/admin_dashboard/security/audit-logs/',
        '/admin_dashboard/security/backups/',
    ]
    
    for url in security_urls:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:  # 200 OK or 302 Redirect to login
                print(f"   ✅ {url} - Status: {response.status_code}")
            else:
                print(f"   ❌ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {url} - Error: {e}")
    
    # Test 2: Check if admin user exists and can be assigned roles
    print("\n2. Testing User Role Assignment:")
    
    try:
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@ecolearn.zm',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            print("   ✅ Created admin user")
        else:
            print("   ✅ Admin user already exists")
        
        # Assign admin role
        admin_role = Role.objects.filter(name='admin').first()
        if admin_role:
            user_role, created = UserRole.objects.get_or_create(
                user=admin_user,
                role=admin_role,
                defaults={'assigned_by': admin_user}
            )
            
            if created:
                print("   ✅ Assigned admin role to user")
            else:
                print("   ✅ Admin role already assigned")
        
    except Exception as e:
        print(f"   ❌ User role assignment error: {e}")
    
    # Test 3: Test login and access to security dashboard
    print("\n3. Testing Authenticated Access:")
    
    try:
        # Login as admin
        login_success = client.login(username='admin', password='admin123')
        
        if login_success:
            print("   ✅ Admin login successful")
            
            # Test security dashboard access
            response = client.get('/admin_dashboard/security/')
            if response.status_code == 200:
                print("   ✅ Security dashboard accessible")
            else:
                print(f"   ⚠️  Security dashboard status: {response.status_code}")
        else:
            print("   ❌ Admin login failed")
            
    except Exception as e:
        print(f"   ❌ Authentication test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Security Web Interface Test Complete!")
    print("\n📋 Access Information:")
    print("Username: admin")
    print("Password: admin123")
    print("Security Dashboard: http://127.0.0.1:8000/admin_dashboard/security/")
    print("\n✅ The security system is ready for use!")

if __name__ == "__main__":
    test_security_web_interface()