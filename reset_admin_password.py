#!/usr/bin/env python3
"""
Script to reset the admin user password
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def reset_admin_password():
    """Reset admin user password"""
    print("🔧 Resetting Admin Password...")
    
    try:
        # Get the admin user
        admin_user = User.objects.get(username='admin')
        
        # Set new password
        new_password = 'admin123'
        admin_user.set_password(new_password)
        admin_user.save()
        
        print(f"✅ Admin password reset successfully!")
        print(f"   Username: admin")
        print(f"   New Password: {new_password}")
        print(f"   Email: {admin_user.email}")
        print(f"   Is Staff: {admin_user.is_staff}")
        print(f"   Is Superuser: {admin_user.is_superuser}")
        
        return True
        
    except User.DoesNotExist:
        print("❌ Admin user not found!")
        return False
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False

def main():
    """Reset admin password"""
    print("🚀 Resetting Django Admin Password\n")
    
    success = reset_admin_password()
    
    if success:
        print(f"\n🎉 Password reset complete!")
        print(f"   You can now login to Django Admin:")
        print(f"   URL: http://127.0.0.1:8000/admin/")
        print(f"   Username: admin")
        print(f"   Password: admin123")
    else:
        print(f"\n❌ Password reset failed!")

if __name__ == '__main__':
    main()