#!/usr/bin/env python
"""
Quick test to verify the USER_ROLES AttributeError fix
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
sys.path.append('.')
django.setup()

def test_user_roles_fix():
    """Test that CustomUser.ROLE_CHOICES works correctly"""
    from accounts.models import CustomUser
    
    print("Testing CustomUser.ROLE_CHOICES...")
    
    try:
        # This should work now
        role_choices = CustomUser.ROLE_CHOICES
        print(f"✅ CustomUser.ROLE_CHOICES works: {role_choices}")
        
        # This should fail (the old incorrect reference)
        try:
            user_roles = CustomUser.USER_ROLES
            print(f"❌ CustomUser.USER_ROLES still exists: {user_roles}")
        except AttributeError:
            print("✅ CustomUser.USER_ROLES correctly doesn't exist")
        
        # Test admin dashboard view context
        print("\nTesting admin dashboard views...")
        from admin_dashboard.views import user_management
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        from accounts.models import CustomUser
        
        # Create a test admin user
        admin_user = CustomUser.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = CustomUser.objects.create_user(
                username='testadmin',
                email='admin@test.com',
                password='testpass123',
                is_staff=True,
                role='admin'
            )
        
        # Create request
        factory = RequestFactory()
        request = factory.get('/admin-dashboard/users/')
        request.user = admin_user
        
        # This should not raise AttributeError anymore
        response = user_management(request)
        print("✅ user_management view works without AttributeError")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    print("=== Testing USER_ROLES AttributeError Fix ===")
    success = test_user_roles_fix()
    
    if success:
        print("\n🎉 All tests passed! The admin dashboard should work now.")
        print("\nYou can now access:")
        print("- http://127.0.0.1:8000/admin-dashboard/users/")
        print("- Other admin dashboard pages")
    else:
        print("\n❌ Some tests failed. Check the errors above.")