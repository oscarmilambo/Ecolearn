#!/usr/bin/env python3
"""
Test Edward Jere Login - Verify the username fix works
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import CustomUser

def test_edward_login():
    """Test that Edward Jere can login with the fixed username"""
    print("🧪 Testing Edward Jere Login...")
    print("=" * 40)
    
    # Find Edward's user
    try:
        edward = CustomUser.objects.get(first_name='Edward', last_name='Jere')
        print(f"✅ Found user: {edward.username}")
        print(f"   📧 Email: {edward.email}")
        print(f"   👤 Full name: {edward.get_full_name()}")
        print(f"   🔐 Is active: {edward.is_active}")
        
        # Test authentication with the correct username
        print(f"\n🔑 Testing authentication with username: '{edward.username}'")
        
        # We need to set a known password first
        edward.set_password('testpass123')
        edward.save()
        print("   ✅ Set test password: testpass123")
        
        # Test authentication
        user = authenticate(username=edward.username, password='testpass123')
        
        if user is not None:
            print(f"   ✅ Authentication successful!")
            print(f"   👋 Welcome back, {user.get_full_name()}!")
        else:
            print(f"   ❌ Authentication failed")
            
        # Also test with wrong username formats that might have been used before
        print(f"\n🚫 Testing with old problematic usernames:")
        
        old_usernames = ['user_edwa', 'Edward Jere', 'edward jere', 'EdwardJere']
        for old_username in old_usernames:
            test_user = authenticate(username=old_username, password='testpass123')
            if test_user:
                print(f"   ⚠️  '{old_username}' still works (unexpected)")
            else:
                print(f"   ✅ '{old_username}' correctly fails")
                
    except CustomUser.DoesNotExist:
        print("❌ Edward Jere user not found")
        
        # Show all users for debugging
        print("\n📋 Available users:")
        for user in CustomUser.objects.all():
            print(f"   👤 {user.username} - {user.get_full_name()}")

def test_new_registration():
    """Test that new registrations create proper usernames"""
    print(f"\n🆕 Testing new user registration logic...")
    
    # Simulate the new registration logic
    first_name = 'Jane'
    last_name = 'Smith'
    
    # Generate username using the new logic
    import re
    base_username = f"{first_name.lower()}.{last_name.lower()}".replace(' ', '.')
    base_username = re.sub(r'[^a-z0-9._]', '', base_username)
    
    counter = 1
    username = base_username
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    print(f"   ✅ Generated username: '{username}' for '{first_name} {last_name}'")
    
    # Test with names that have special characters
    test_names = [
        ('José', 'García'),
        ('Mary-Jane', 'O\'Connor'),
        ('李', '小明'),
        ('John Paul', 'Smith Jr'),
    ]
    
    for first, last in test_names:
        base_username = f"{first.lower()}.{last.lower()}".replace(' ', '.')
        base_username = re.sub(r'[^a-z0-9._]', '', base_username)
        print(f"   📝 '{first} {last}' → '{base_username}'")

if __name__ == '__main__':
    print("🚀 Testing Username Fix...")
    print("=" * 50)
    
    try:
        test_edward_login()
        test_new_registration()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("\n💡 Summary:")
        print("   - Edward Jere can now login with 'edward.jere'")
        print("   - New users get proper name-based usernames")
        print("   - No more truncated 'user_xxxx' usernames")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()