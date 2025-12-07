"""
Test PRO WhatsApp/SMS Notifications
Run: python test_pro_notifications.py
"""

import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from community.notifications import notification_service
from accounts.models import CustomUser
from community.models import CommunityChallenge, ChallengeParticipant, ChallengeProof, Notification
from reporting.models import DumpingReport
from elearning.models import Module, Enrollment
from django.utils import timezone

print("=" * 60)
print("TESTING PRO WHATSAPP/SMS NOTIFICATIONS")
print("=" * 60)

# Get test user (replace with your phone number)
try:
    test_user = CustomUser.objects.filter(phone_number__isnull=False).first()
    if not test_user:
        print("❌ No user with phone number found!")
        print("Please add a phone number to a user first.")
        exit()
    
    print(f"\n✅ Test User: {test_user.username}")
    print(f"📱 Phone: {test_user.phone_number}")
    
    # Test 1: Join Challenge Notification
    print("\n" + "=" * 60)
    print("TEST 1: JOIN CHALLENGE NOTIFICATION")
    print("=" * 60)
    
    challenge = CommunityChallenge.objects.first()
    if challenge:
        user_name = test_user.get_full_name() or test_user.username
        sms_msg = f"🎉 {user_name}, welcome to {challenge.title}! Top 3 win airtime. Submit proof now!"
        whatsapp_msg = f"🎉 {user_name}, welcome to {challenge.title}! Top 3 win airtime. Submit proof now!"
        
        print(f"\n📱 SMS Message:\n{sms_msg}")
        print(f"\n💬 WhatsApp Message:\n{whatsapp_msg}")
        
        # Send SMS
        result = notification_service.send_sms(str(test_user.phone_number), sms_msg)
        if result.get('success'):
            print(f"\n✅ SMS sent successfully! SID: {result.get('message_sid')}")
        else:
            print(f"\n❌ SMS failed: {result.get('error')}")
        
        # Send WhatsApp
        result = notification_service.send_whatsapp(str(test_user.phone_number), whatsapp_msg)
        if result.get('success'):
            print(f"✅ WhatsApp sent successfully! SID: {result.get('message_sid')}")
        else:
            print(f"❌ WhatsApp failed: {result.get('error')}")
    else:
        print("❌ No challenge found")
    
    # Test 2: Proof Approved Notification
    print("\n" + "=" * 60)
    print("TEST 2: PROOF APPROVED NOTIFICATION")
    print("=" * 60)
    
    points = 50
    bags = 5
    rank = 3
    challenge_name = "Clean Kalingalinga Challenge"
    
    sms_msg = f"✅ APPROVED! You earned {points} points ({bags} bags). You are now #{rank} in {challenge_name}! Keep cleaning Zambia!"
    whatsapp_msg = f"✅ APPROVED! You earned {points} points ({bags} bags). You are now #{rank} in {challenge_name}! Keep cleaning Zambia!"
    
    print(f"\n📱 SMS Message:\n{sms_msg}")
    print(f"\n💬 WhatsApp Message:\n{whatsapp_msg}")
    
    # Send SMS
    result = notification_service.send_sms(str(test_user.phone_number), sms_msg)
    if result.get('success'):
        print(f"\n✅ SMS sent successfully! SID: {result.get('message_sid')}")
    else:
        print(f"\n❌ SMS failed: {result.get('error')}")
    
    # Send WhatsApp
    result = notification_service.send_whatsapp(str(test_user.phone_number), whatsapp_msg)
    if result.get('success'):
        print(f"✅ WhatsApp sent successfully! SID: {result.get('message_sid')}")
    else:
        print(f"❌ WhatsApp failed: {result.get('error')}")
    
    # Test 3: New Dumping Report (Admin Notification)
    print("\n" + "=" * 60)
    print("TEST 3: NEW ILLEGAL DUMP NOTIFICATION (ADMIN)")
    print("=" * 60)
    
    location = "Kalingalinga Market"
    photos = 3
    
    sms_msg = f"🚨 NEW ILLEGAL DUMP in {location}! {photos} photos attached. Act now!"
    whatsapp_msg = f"🚨 NEW ILLEGAL DUMP in {location}! {photos} photos attached. Act now!"
    
    print(f"\n📱 SMS Message:\n{sms_msg}")
    print(f"\n💬 WhatsApp Message:\n{whatsapp_msg}")
    
    # Send to admin (using test user for demo)
    result = notification_service.send_sms(str(test_user.phone_number), sms_msg)
    if result.get('success'):
        print(f"\n✅ SMS sent successfully! SID: {result.get('message_sid')}")
    else:
        print(f"\n❌ SMS failed: {result.get('error')}")
    
    result = notification_service.send_whatsapp(str(test_user.phone_number), whatsapp_msg)
    if result.get('success'):
        print(f"✅ WhatsApp sent successfully! SID: {result.get('message_sid')}")
    else:
        print(f"❌ WhatsApp failed: {result.get('error')}")
    
    # Test 4: Lesson Completed Notification
    print("\n" + "=" * 60)
    print("TEST 4: LESSON COMPLETED NOTIFICATION")
    print("=" * 60)
    
    user_name = test_user.get_full_name() or test_user.username
    module_title = "Waste Management Basics"
    
    sms_msg = f"✅ Well done {user_name}! You finished '{module_title}'. +20 points added!"
    whatsapp_msg = f"✅ Well done {user_name}! You finished '{module_title}'. +20 points added!"
    
    print(f"\n📱 SMS Message:\n{sms_msg}")
    print(f"\n💬 WhatsApp Message:\n{whatsapp_msg}")
    
    # Send SMS
    result = notification_service.send_sms(str(test_user.phone_number), sms_msg)
    if result.get('success'):
        print(f"\n✅ SMS sent successfully! SID: {result.get('message_sid')}")
    else:
        print(f"\n❌ SMS failed: {result.get('error')}")
    
    # Send WhatsApp
    result = notification_service.send_whatsapp(str(test_user.phone_number), whatsapp_msg)
    if result.get('success'):
        print(f"✅ WhatsApp sent successfully! SID: {result.get('message_sid')}")
    else:
        print(f"❌ WhatsApp failed: {result.get('error')}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 60)
    print("\nCheck your phone for 8 messages (4 SMS + 4 WhatsApp)")
    print("All messages use PRO ZNBC-style formatting!")
    print("\n💡 TIP: If messages didn't arrive, check:")
    print("   1. Twilio credentials in .env")
    print("   2. Phone number has +260 prefix")
    print("   3. Twilio account balance")
    print("   4. User notification preferences")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    pass  # Script runs on import
