#!/usr/bin/env python
"""
Test script to verify security URL namespaces are working
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from security.models import Role, UserRole

User = get_user_model()

def test_security_urls():
    print("🔗 Testing Security URL Namespaces")
    print("=" * 50)
    
    # Test URL reversing
    print("\n1. Testing URL Reversing:")
    
    security_urls = [
        ('admin_dashboard:security:dashboard', 'Security Dashboard'),
        ('admin_dashboard:security:role_management', 'Role Management'),
        ('admin_dashboard:security:audit_logs', 'Audit Logs'),
        ('admin_dashboard:security:backup_management', 'Backup Management'),
        ('admin_dashboard:security:security_settings', 'Security Settings'),
    ]
    
    for url_name, description in security_urls:
        try:
            url = reverse(url_name)
            print(f"   ✅ {description}: {url}")
        except Exception as e:
            print(f"   ❌ {description}: {e}")
    
    # Test URL accessibility with authentication
    print("\n2. Testing URL Accessibility:")
    
    client = Client()
    
    # Create and login admin user
    try:
        admin_user, created = User.objects.get_or_create(
            username='testadmin',
            defaults={
                'email': 'testadmin@ecolearn.zm',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('testpass123')
            admin_user.save()
        
        # Assign admin role
        admin_role = Role.objects.filter(name='admin').first()
        if admin_role:
            UserRole.objects.get_or_create(
                user=admin_user,
                role=admin_role,
                defaults={'assigned_by': admin_user}
            )
        
        # Login
        login_success = client.login(username='testadmin', password='testpass123')
        
        if login_success:
            print("   ✅ Test user login successful")
            
            # Test each URL
            for url_name, description in security_urls:
                try:
                    url = reverse(url_name)
                    response = client.get(url)
                    
                    if response.status_code == 200:
                        print(f"   ✅ {description}: Accessible (200)")
                    elif response.status_code == 302:
                        print(f"   ⚠️  {description}: Redirect (302)")
                    else:
                        print(f"   ❌ {description}: Status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ {description}: Error - {e}")
        else:
            print("   ❌ Test user login failed")
            
    except Exception as e:
        print(f"   ❌ Authentication setup error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Security URL Test Complete!")

if __name__ == "__main__":
    test_security_urls()