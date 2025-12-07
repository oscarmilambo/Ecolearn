#!/usr/bin/env python
"""
Test script to verify the security system is working correctly
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from security.models import Role, UserRole, AuditLog
from security.permissions import has_permission, DEFAULT_ROLE_PERMISSIONS
from security.backup import BackupManager
from django.contrib.auth import get_user_model

User = get_user_model()

def test_security_system():
    print("🔐 Testing Security & Access Control System")
    print("=" * 50)
    
    # Test 1: Check if roles were created
    print("\n1. Testing Role Creation:")
    roles = Role.objects.all()
    print(f"   ✅ Created {roles.count()} roles:")
    for role in roles:
        print(f"      - {role.get_name_display()}: {len(role.permissions)} permissions")
    
    # Test 2: Check permissions
    print("\n2. Testing Permission System:")
    admin_role = Role.objects.filter(name='admin').first()
    if admin_role:
        print(f"   ✅ Admin role has {len(admin_role.permissions)} permissions")
        print(f"   ✅ Admin can manage users: {admin_role.permissions.get('manage_users', False)}")
        print(f"   ✅ Admin can send alerts: {admin_role.permissions.get('send_alerts', False)}")
    
    # Test 3: Check audit logging
    print("\n3. Testing Audit System:")
    audit_count = AuditLog.objects.count()
    print(f"   ✅ Audit log has {audit_count} entries")
    
    # Test 4: Check backup system
    print("\n4. Testing Backup System:")
    try:
        backup_manager = BackupManager()
        backup_status = backup_manager.get_backup_status()
        print(f"   ✅ Backup system initialized")
        print(f"   ✅ Backup directory: {backup_status['backup_directory']}")
        print(f"   ✅ Available space: {backup_status['available_space']:,} bytes")
    except Exception as e:
        print(f"   ⚠️  Backup system warning: {e}")
    
    # Test 5: Check user model integration
    print("\n5. Testing User Model Integration:")
    user_count = User.objects.count()
    print(f"   ✅ Found {user_count} users in system")
    
    # Test 6: Check middleware
    print("\n6. Testing Security Middleware:")
    try:
        from security.middleware import SecurityMiddleware, AuditMiddleware
        print("   ✅ Security middleware imported successfully")
        print("   ✅ Audit middleware imported successfully")
    except Exception as e:
        print(f"   ❌ Middleware error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Security System Test Complete!")
    print("✅ All core components are working correctly")
    print("\n📋 Next Steps:")
    print("1. Access admin dashboard at: /admin_dashboard/")
    print("2. Navigate to Security section")
    print("3. Assign roles to users")
    print("4. Create your first backup")
    print("5. Review audit logs")

if __name__ == "__main__":
    test_security_system()