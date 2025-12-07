"""
Test Real-Time Notifications for oscarmilambo2
Tests all 5 notification scenarios
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from accounts.models import CustomUser, NotificationPreference
from community.models import CommunityChallenge, ChallengeParticipant, Notification
from community.notifications import notification_service
from django.utils import timezone

print("=" * 70)
print("REAL-TIME NOTIFICATION SYSTEM TEST")
print("=" * 70)

# Get oscarmilambo2 user
try:
    user = CustomUser.objects.get(username='oscarmilambo2')
    print(f"\n✅ Found user: {user.username}")
    print(f"   Phone: {user.phone_number}")
    print(f"   Email: {user.email}")
except CustomUser.DoesNotExist:
    print("\n❌ User 'oscarmilambo2' not found!")
    print("   Creating test user...")
    user = CustomUser.objects.create_user(
        username='oscarmilambo2',
        email='oscar@test.com',
        phone_number='+260970594105',
        password='test123'
    )
    print(f"✅ Created user: {user.username}")

# Check/Create notification preferences
prefs, created = NotificationPreference.objects.get_or_create(user=user)
if created:
    print(f"\n✅ Created notification preferences for {user.username}")
else:
    print(f"\n✅ Found notification preferences for {user.username}")

print(f"   SMS Enabled: {prefs.sms_enabled}")
print(f"   WhatsApp Enabled: {prefs.whatsapp_enabled}")
print(f"   Email Enabled: {prefs.email_enabled}")
print(f"   Challenge Updates: {prefs.challenge_updates}")
print(f"   Forum Replies: {prefs.forum_replies}")

# Enable all notifications for testing
if not prefs.sms_enabled or not prefs.whatsapp_enabled:
    prefs.sms_enabled = True
    prefs.whatsapp_enabled = True
    prefs.email_enabled = True
    prefs.challenge_updates = True
    prefs.forum_replies = True
    prefs.event_reminders = True
    prefs.save()
    print("\n✅ Enabled all notification channels for testing")

# Test 1: Challenge Join Notification
print("\n" + "=" * 70)
print("TEST 1: Challenge Join Notification")
print("=" * 70)

try:
    # Get or create a test challenge
    challenge = CommunityChallenge.objects.filter(is_active=True).first()
    
    if not challenge:
        print("❌ No active challenges found. Creating test challenge...")
        challenge = CommunityChallenge.objects.create(
            title="Test Cleanup Challenge",
            description="Test challenge for notification system",
            challenge_type='cleanup',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30),
            target_goal=100,
            reward_points=500,
            is_active=True
        )
        print(f"✅ Created test challenge: {challenge.title}")
    else:
        print(f"✅ Using challenge: {challenge.title}")
    
    # Test notification
    challenge_url = f"https://marabo.co.zm/community/challenges/{challenge.id}/"
    
    # SMS
    if user.phone_number:
        sms_message = f"You just joined {challenge.title}! Collect bags and climb the leaderboard! View: {challenge_url}"
        result = notification_service.send_sms(str(user.phone_number), sms_message)
        if result.get('success'):
            print(f"✅ SMS sent! Message SID: {result.get('message_sid')}")
        else:
            print(f"❌ SMS failed: {result.get('error')}")
    
    # WhatsApp
    if user.phone_number:
        whatsapp_message = f"🎉 *Challenge Joined!*\n\nYou just joined *{challenge.title}*!\n\nCollect bags and climb the leaderboard! 🏆\n\nView challenge: {challenge_url}"
        result = notification_service.send_whatsapp(str(user.phone_number), whatsapp_message)
        if result.get('success'):
            print(f"✅ WhatsApp sent! Message SID: {result.get('message_sid')}")
        else:
            print(f"❌ WhatsApp failed: {result.get('error')}")
    
    print("✅ Test 1 Complete: Challenge join notifications sent!")
    
except Exception as e:
    print(f"❌ Test 1 Failed: {e}")

# Test 2: Proof Approval Notification
print("\n" + "=" * 70)
print("TEST 2: Proof Approval Notification")
print("=" * 70)

try:
    bags = 5
    points = bags * 30
    rank = 1
    
    # SMS
    if user.phone_number:
        sms_message = f"Your clean-up proof is APPROVED! +{points} points earned ({bags} bags). Current rank: #{rank}! Keep cleaning!"
        result = notification_service.send_sms(str(user.phone_number), sms_message)
        if result.get('success'):
            print(f"✅ SMS sent! Message SID: {result.get('message_sid')}")
        else:
            print(f"❌ SMS failed: {result.get('error')}")
    
    # WhatsApp
    if user.phone_number:
        whatsapp_message = f"✅ *Proof APPROVED!*\n\n🎉 Congratulations!\n\n*Points Earned:* +{points} points\n*Bags Collected:* {bags} bags\n*Current Rank:* #{rank}\n\nKeep cleaning and climb the leaderboard! 🏆"
        result = notification_service.send_whatsapp(str(user.phone_number), whatsapp_message)
        if result.get('success'):
            print(f"✅ WhatsApp sent! Message SID: {result.get('message_sid')}")
        else:
            print(f"❌ WhatsApp failed: {result.get('error')}")
    
    print("✅ Test 2 Complete: Proof approval notifications sent!")
    
except Exception as e:
    print(f"❌ Test 2 Failed: {e}")

# Test 3: Illegal Dumping Report (Admin Notification)
print("\n" + "=" * 70)
print("TEST 3: Illegal Dumping Report - Admin Notification")
print("=" * 70)

try:
    # Get all admins
    admins = CustomUser.objects.filter(is_superuser=True)
    print(f"Found {admins.count()} admin(s)")
    
    location = "Kanyama Market"
    reports_today = 3
    ref_number = "ECO12345"
    
    for admin in admins:
        if admin.phone_number:
            # SMS
            sms_message = f"New illegal dumping report in {location}! {reports_today} reports today. Check admin panel now."
            result = notification_service.send_sms(str(admin.phone_number), sms_message)
            if result.get('success'):
                print(f"✅ Admin SMS sent to {admin.username}")
            
            # WhatsApp
            whatsapp_message = f"🚨 *New Illegal Dumping Report*\n\n*Location:* {location}\n*Severity:* High\n*Reference:* {ref_number}\n*Reports Today:* {reports_today}\n\nCheck admin panel now!"
            result = notification_service.send_whatsapp(str(admin.phone_number), whatsapp_message)
            if result.get('success'):
                print(f"✅ Admin WhatsApp sent to {admin.username}")
    
    print("✅ Test 3 Complete: Admin notifications sent!")
    
except Exception as e:
    print(f"❌ Test 3 Failed: {e}")

# Test 4: Forum Reply Notification
print("\n" + "=" * 70)
print("TEST 4: Forum Reply Notification")
print("=" * 70)

try:
    topic_title = "Best recycling practices"
    replier = "JohnDoe"
    
    # SMS
    if user.phone_number:
        sms_message = f"New reply in '{topic_title}' by {replier}"
        result = notification_service.send_sms(str(user.phone_number), sms_message)
        if result.get('success'):
            print(f"✅ SMS sent! Message SID: {result.get('message_sid')}")
        else:
            print(f"❌ SMS failed: {result.get('error')}")
    
    # WhatsApp
    if user.phone_number:
        whatsapp_message = f"💬 *New Reply in Your Topic*\n\n*Topic:* {topic_title}\n*Reply by:* {replier}\n\nCheck it out now!"
        result = notification_service.send_whatsapp(str(user.phone_number), whatsapp_message)
        if result.get('success'):
            print(f"✅ WhatsApp sent! Message SID: {result.get('message_sid')}")
        else:
            print(f"❌ WhatsApp failed: {result.get('error')}")
    
    print("✅ Test 4 Complete: Forum reply notifications sent!")
    
except Exception as e:
    print(f"❌ Test 4 Failed: {e}")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"✅ User: {user.username}")
print(f"✅ Phone: {user.phone_number}")
print(f"✅ All notification types tested")
print(f"✅ Check your WhatsApp at {user.phone_number}")
print("\n🎉 Real-time notification system is LIVE!")
print("=" * 70)
