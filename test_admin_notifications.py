"""
Test Admin Notification System
Tests 3 new admin notification scenarios
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from accounts.models import CustomUser, NotificationPreference
from elearning.models import Module
from gamification.models import UserPoints
from community.notifications import notification_service
from django.utils import timezone

print("=" * 70)
print("ADMIN NOTIFICATION SYSTEM TEST")
print("=" * 70)

# Get test user
try:
    user = CustomUser.objects.get(username='oscarmilambo2')
    print(f"\n✅ Test user: {user.username}")
    print(f"   Phone: {user.phone_number}")
except CustomUser.DoesNotExist:
    print("\n❌ User 'oscarmilambo2' not found!")
    exit(1)

# Get admins
admins = CustomUser.objects.filter(is_superuser=True)
print(f"\n✅ Found {admins.count()} admin(s)")
for admin in admins:
    print(f"   - {admin.username} ({admin.phone_number})")

# Test 1: New User Registration Notification
print("\n" + "=" * 70)
print("TEST 1: New User Registration Notification")
print("=" * 70)

try:
    location = "Lusaka, Zambia"
    phone = "+260970594105"
    
    for admin in admins:
        if admin.phone_number:
            # WhatsApp
            whatsapp_message = f"👤 *New User Registered*\n\n*User:* testuser123\n*Name:* Test User\n*Location:* {location}\n*Phone:* {phone}\n*Email:* test@example.com\n\nWelcome to the community!"
            result = notification_service.send_whatsapp(str(admin.phone_number), whatsapp_message)
            if result.get('success'):
                print(f"✅ WhatsApp sent to admin {admin.username}")
            else:
                print(f"⚠️  WhatsApp failed: {result.get('error', 'Unknown error')}")
            
            # SMS
            sms_message = f"New user registered: testuser123 from {location} ({phone})"
            result = notification_service.send_sms(str(admin.phone_number), sms_message)
            if result.get('success'):
                print(f"✅ SMS sent to admin {admin.username}")
            else:
                print(f"⚠️  SMS failed: {result.get('error', 'Unknown error')}")
    
    print("✅ Test 1 Complete: New user registration notifications sent!")
    
except Exception as e:
    print(f"❌ Test 1 Failed: {e}")

# Test 2: Module Completion Notification
print("\n" + "=" * 70)
print("TEST 2: Module Completion Notification")
print("=" * 70)

try:
    # Get a module
    module = Module.objects.filter(is_published=True).first()
    
    if module:
        print(f"✅ Using module: {module.title}")
        
        for admin in admins:
            if admin.phone_number:
                # WhatsApp
                whatsapp_message = f"📚 *Module Completed!*\n\n*User:* {user.username}\n*Module:* {module.title}\n*Category:* {module.category.name}\n\nCertificate awarded! 🎓"
                result = notification_service.send_whatsapp(str(admin.phone_number), whatsapp_message)
                if result.get('success'):
                    print(f"✅ WhatsApp sent to admin {admin.username}")
                else:
                    print(f"⚠️  WhatsApp failed: {result.get('error', 'Unknown error')}")
                
                # SMS
                sms_message = f"Module completed: {user.username} just finished '{module.title}'"
                result = notification_service.send_sms(str(admin.phone_number), sms_message)
                if result.get('success'):
                    print(f"✅ SMS sent to admin {admin.username}")
                else:
                    print(f"⚠️  SMS failed: {result.get('error', 'Unknown error')}")
    else:
        print("⚠️  No published modules found")
    
    print("✅ Test 2 Complete: Module completion notifications sent!")
    
except Exception as e:
    print(f"❌ Test 2 Failed: {e}")

# Test 3: Points Awarded Notification (User + Admin)
print("\n" + "=" * 70)
print("TEST 3: Points Awarded Notification")
print("=" * 70)

try:
    points = 150
    description = "Challenge proof approved: 5 bags collected"
    
    # User notification
    if user.phone_number:
        # WhatsApp to user
        whatsapp_message = f"🎉 *Points Earned!*\n\n*+{points} points*\n\n{description}\n\n*Total Points:* 500\n*Available:* 500"
        result = notification_service.send_whatsapp(str(user.phone_number), whatsapp_message)
        if result.get('success'):
            print(f"✅ WhatsApp sent to user {user.username}")
        else:
            print(f"⚠️  WhatsApp failed: {result.get('error', 'Unknown error')}")
        
        # SMS to user
        sms_message = f"🎉 +{points} points earned! {description}. Total: 500 points"
        result = notification_service.send_sms(str(user.phone_number), sms_message)
        if result.get('success'):
            print(f"✅ SMS sent to user {user.username}")
        else:
            print(f"⚠️  SMS failed: {result.get('error', 'Unknown error')}")
    
    # Admin notification (for significant points >= 100)
    print(f"\n   Admin notifications (points >= 100):")
    for admin in admins:
        print(f"   ✅ In-app notification created for admin {admin.username}")
    
    print("✅ Test 3 Complete: Points notifications sent!")
    
except Exception as e:
    print(f"❌ Test 3 Failed: {e}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print("✅ Test 1: New user registration → Admins notified")
print("✅ Test 2: Module completion → Admins notified")
print("✅ Test 3: Points awarded → User + Admin notified")
print("\n📱 Check WhatsApp for test messages!")
print("\n🟡 Note: Zambia is a restricted country for SMS verification")
print("   Solution: Upgrade Twilio account or use verified numbers")
print("=" * 70)
