#!/usr/bin/env python3
"""
Complete Password Reset System Test
Tests the entire password reset flow including SMS verification
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import CustomUser, PasswordResetCode
from django.utils import timezone
from datetime import timedelta

def test_password_reset_flow():
    """Test the complete password reset flow"""
    print("🧪 Testing Complete Password Reset System")
    print("=" * 60)
    
    # Step 1: Create test user
    print("\n1. Creating test user...")
    CustomUser.objects.filter(username='resettest').delete()
    
    user = CustomUser.objects.create_user(
        username='resettest',
        email='reset@test.com',
        password='oldpassword123',
        phone_number='+260977123456',
        first_name='Reset',
        last_name='Test',
        is_active=True
    )
    print(f"   ✅ Created user: {user.username} with phone: {user.phone_number}")
    
    # Step 2: Test password reset request
    print("\n2. Testing password reset request...")
    client = Client()
    
    # Get reset request page
    response = client.get(reverse('accounts:password_reset_request'))
    print(f"   Reset request page status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Password reset request page loads")
        
        # Submit reset request
        reset_response = client.post(reverse('accounts:password_reset_request'), {
            'phone_number': '+260977123456'
        })
        
        print(f"   Reset request submission status: {reset_response.status_code}")
        
        if reset_response.status_code == 302:  # Redirect to verify page
            print("   ✅ Reset request submitted successfully")
            
            # Check if reset code was created
            reset_codes = PasswordResetCode.objects.filter(user=user, is_used=False)
            if reset_codes.exists():
                reset_code = reset_codes.first()
                print(f"   ✅ Reset code generated: {reset_code.code}")
                
                # Step 3: Test verification
                print("\n3. Testing code verification...")
                
                # Get verification page
                verify_response = client.get(reverse('accounts:password_reset_verify'))
                print(f"   Verify page status: {verify_response.status_code}")
                
                if verify_response.status_code == 200:
                    print("   ✅ Verification page loads")
                    
                    # Submit verification with new password
                    verify_submit = client.post(reverse('accounts:password_reset_verify'), {
                        'code': reset_code.code,
                        'new_password': 'newpassword123',
                        'confirm_password': 'newpassword123'
                    })
                    
                    print(f"   Verification submission status: {verify_submit.status_code}")
                    
                    if verify_submit.status_code == 302:  # Redirect to login
                        print("   ✅ Password reset verification successful")
                        
                        # Step 4: Test login with new password
                        print("\n4. Testing login with new password...")
                        
                        from django.contrib.auth import authenticate
                        auth_test = authenticate(username='resettest', password='newpassword123')
                        
                        if auth_test:
                            print("   ✅ Login with new password successful!")
                            
                            # Test old password doesn't work
                            old_auth = authenticate(username='resettest', password='oldpassword123')
                            if not old_auth:
                                print("   ✅ Old password correctly invalidated")
                            else:
                                print("   ❌ Old password still works (ERROR)")
                            
                            # Check reset code is marked as used
                            reset_code.refresh_from_db()
                            if reset_code.is_used:
                                print("   ✅ Reset code marked as used")
                            else:
                                print("   ❌ Reset code not marked as used")
                            
                            return True
                        else:
                            print("   ❌ Login with new password failed")
                    else:
                        print("   ❌ Password reset verification failed")
                else:
                    print("   ❌ Verification page failed to load")
            else:
                print("   ❌ No reset code generated")
        else:
            print("   ❌ Reset request submission failed")
    else:
        print("   ❌ Password reset request page failed to load")
    
    return False

def test_password_reset_security():
    """Test security aspects of password reset"""
    print("\n🔒 Testing Password Reset Security")
    print("=" * 50)
    
    # Test 1: Invalid phone number
    print("\n1. Testing invalid phone number...")
    client = Client()
    
    response = client.post(reverse('accounts:password_reset_request'), {
        'phone_number': '+260999999999'  # Non-existent number
    })
    
    if response.status_code == 200:  # Should stay on same page with error
        print("   ✅ Invalid phone number handled correctly")
    else:
        print("   ❌ Invalid phone number not handled properly")
    
    # Test 2: Expired code
    print("\n2. Testing expired reset code...")
    
    # Create user and expired reset code
    user = CustomUser.objects.filter(username='resettest').first()
    if user:
        # Create expired code
        expired_code = PasswordResetCode.objects.create(
            user=user,
            phone_number=user.phone_number,
            code='123456',
            is_used=False,
            expires_at=timezone.now() - timedelta(minutes=1)  # Expired 1 minute ago
        )
        
        # Try to use expired code
        client.post(reverse('accounts:password_reset_request'), {
            'phone_number': user.phone_number
        })
        
        response = client.post(reverse('accounts:password_reset_verify'), {
            'code': '123456',
            'new_password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        
        if response.status_code == 200:  # Should stay on page with error
            print("   ✅ Expired code rejected correctly")
        else:
            print("   ❌ Expired code not handled properly")
    
    # Test 3: Password mismatch
    print("\n3. Testing password mismatch...")
    
    if user:
        # Create fresh code
        fresh_code = PasswordResetCode.objects.create(
            user=user,
            phone_number=user.phone_number,
            code='654321',
            is_used=False
        )
        
        client.post(reverse('accounts:password_reset_request'), {
            'phone_number': user.phone_number
        })
        
        response = client.post(reverse('accounts:password_reset_verify'), {
            'code': '654321',
            'new_password': 'password1',
            'confirm_password': 'password2'  # Different password
        })
        
        if response.status_code == 200:  # Should stay on page with error
            print("   ✅ Password mismatch handled correctly")
        else:
            print("   ❌ Password mismatch not handled properly")

def test_password_reset_ui():
    """Test the UI components of password reset"""
    print("\n🎨 Testing Password Reset UI")
    print("=" * 40)
    
    client = Client()
    
    # Test request page
    print("\n1. Testing request page UI...")
    response = client.get(reverse('accounts:password_reset_request'))
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for required form elements
        if 'phone_number' in content:
            print("   ✅ Phone number field present")
        else:
            print("   ❌ Phone number field missing")
        
        if 'csrf' in content.lower():
            print("   ✅ CSRF protection present")
        else:
            print("   ❌ CSRF protection missing")
    
    # Test verify page (with session)
    print("\n2. Testing verify page UI...")
    
    # Set session data
    session = client.session
    session['reset_phone'] = '+260977123456'
    session.save()
    
    response = client.get(reverse('accounts:password_reset_verify'))
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for required elements
        if 'code' in content:
            print("   ✅ Code input field present")
        else:
            print("   ❌ Code input field missing")
        
        if 'new_password' in content:
            print("   ✅ New password field present")
        else:
            print("   ❌ New password field missing")
        
        if 'confirm_password' in content:
            print("   ✅ Confirm password field present")
        else:
            print("   ❌ Confirm password field missing")

def cleanup_test_data():
    """Clean up test data"""
    print("\n🧹 Cleaning up test data...")
    
    # Remove test users
    CustomUser.objects.filter(username__in=['resettest']).delete()
    
    # Remove test reset codes
    PasswordResetCode.objects.filter(phone_number='+260977123456').delete()
    
    print("   ✅ Test data cleaned up")

if __name__ == '__main__':
    try:
        # Run all tests
        success = test_password_reset_flow()
        test_password_reset_security()
        test_password_reset_ui()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 PASSWORD RESET SYSTEM WORKING CORRECTLY!")
            print("\nYou can now:")
            print("1. Go to /accounts/password-reset/ to reset passwords")
            print("2. Use phone number verification")
            print("3. Set new passwords securely")
        else:
            print("❌ Some issues found in password reset system")
            print("\nCheck the error messages above for details")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup_test_data()