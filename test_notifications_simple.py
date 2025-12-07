#!/usr/bin/env python
"""
Simple Notification Test
Run: python test_notifications_simple.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from community.notifications import notification_service
from accounts.models import CustomUser

print("=" * 60)
print("SIMPLE NOTIFICATION TEST")
print("=" * 60)

# Get test user
test_user = CustomUser.objects.filter(phone_number__isnull=False).first()

if not test_user:
    print("\n❌ No user with phone number found!")
    print("Please add a phone number to a user first.")
    sys.exit(1)

print(f"\n✅ Test User: {test_user.username}")
print(f"📱 Phone: {test_user.phone_number}")

# Test 1: Simple SMS
print("\n" + "=" * 60)
print("TEST 1: SIMPLE SMS")
print("=" * 60)

sms_msg = "🎉 Test from EcoLearn! Your notifications are working!"
print(f"\nSending: {sms_msg}")

result = notification_service.send_sms(str(test_user.phone_number), sms_msg)

if result.get('success'):
    print(f"✅ SMS sent successfully!")
    print(f"   SID: {result.get('message_sid')}")
    print(f"   Status: {result.get('status')}")
else:
    print(f"❌ SMS failed: {result.get('error')}")

# Test 2: Simple WhatsApp
print("\n" + "=" * 60)
print("TEST 2: SIMPLE WHATSAPP")
print("=" * 60)

whatsapp_msg = "🎉 Test from EcoLearn! Your WhatsApp notifications are working!"
print(f"\nSending: {whatsapp_msg}")

result = notification_service.send_whatsapp(str(test_user.phone_number), whatsapp_msg)

if result.get('success'):
    print(f"✅ WhatsApp sent successfully!")
    print(f"   SID: {result.get('message_sid')}")
    print(f"   Status: {result.get('status')}")
else:
    print(f"❌ WhatsApp failed: {result.get('error')}")

# Test 3: PRO Challenge Welcome
print("\n" + "=" * 60)
print("TEST 3: PRO CHALLENGE WELCOME")
print("=" * 60)

user_name = test_user.get_full_name() or test_user.username
challenge_name = "Clean Kalingalinga Challenge"
pro_msg = f"🎉 {user_name}, welcome to {challenge_name}! Top 3 win airtime. Submit proof now!"

print(f"\nSending: {pro_msg}")

result = notification_service.send_sms(str(test_user.phone_number), pro_msg)
if result.get('success'):
    print(f"✅ SMS sent!")
else:
    print(f"❌ SMS failed: {result.get('error')}")

result = notification_service.send_whatsapp(str(test_user.phone_number), pro_msg)
if result.get('success'):
    print(f"✅ WhatsApp sent!")
else:
    print(f"❌ WhatsApp failed: {result.get('error')}")

# Test 4: PRO Proof Approved
print("\n" + "=" * 60)
print("TEST 4: PRO PROOF APPROVED")
print("=" * 60)

pro_msg = f"✅ APPROVED! You earned 50 points (5 bags). You are now #3 in {challenge_name}! Keep cleaning Zambia!"

print(f"\nSending: {pro_msg}")

result = notification_service.send_sms(str(test_user.phone_number), pro_msg)
if result.get('success'):
    print(f"✅ SMS sent!")
else:
    print(f"❌ SMS failed: {result.get('error')}")

result = notification_service.send_whatsapp(str(test_user.phone_number), pro_msg)
if result.get('success'):
    print(f"✅ WhatsApp sent!")
else:
    print(f"❌ WhatsApp failed: {result.get('error')}")

print("\n" + "=" * 60)
print("✅ TESTS COMPLETED!")
print("=" * 60)
print("\nCheck your phone for 6 messages (3 SMS + 3 WhatsApp)")
print("\n💡 If messages didn't arrive:")
print("   1. Check Twilio credentials: python check_credentials.py")
print("   2. Verify phone number format: +260971234567")
print("   3. Check Twilio console: https://console.twilio.com")
print("   4. Verify account balance")
