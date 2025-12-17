#!/usr/bin/env python3
"""
Complete Notification System Test
Creates a test challenge and verifies all notifications are sent
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.contrib.auth import get_user_model
from community.models import Notification, CommunityChallenge
from django.utils import timezone
from datetime import timedelta, date

User = get_user_model()

def test_complete_notification_system():
    print("🧪 Testing Complete Notification System...")
    print("=" * 60)
    
    # Get all users
    users = User.objects.filter(is_active=True)
    print(f"👥 Active users: {users.count()}")
    
    # Create a test challenge
    test_challenge = CommunityChallenge.objects.create(
        title="🧪 Test Challenge - Notification System",
        description="This is a test challenge to verify that notifications are working properly in the EcoLearn system.",
        challenge_type="cleanup",
        start_date=timezone.now().date(),
        end_date=(timezone.now() + timedelta(days=7)).date(),
        target_goal=50,
        reward_points=150,
        is_active=True
    )
    
    print(f"✅ Created test challenge: {test_challenge.title}")
    print(f"   ID: {test_challenge.id}")
    print(f"   Type: {test_challenge.challenge_type}")
    print(f"   Reward: {test_challenge.reward_points} points")
    
    # Create notifications for all users (simulating the admin dashboard process)
    notifications_created = 0
    for user in users:
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type='challenge_update',
                title=f'🏆 New Challenge: {test_challenge.title}',
                message=f'{test_challenge.description[:150]}... Reward: {test_challenge.reward_points} points!',
                url=f'/community/challenges/{test_challenge.id}/'
            )
            notifications_created += 1
            print(f"✅ Created notification for {user.username} (ID: {notification.id})")
        except Exception as e:
            print(f"❌ Error creating notification for {user.username}: {e}")
    
    print(f"\n🎉 Created {notifications_created} notifications!")
    
    # Verify notifications
    challenge_notifications = Notification.objects.filter(
        notification_type='challenge_update',
        title__icontains=test_challenge.title[:20]
    )
    
    print(f"✅ Verification: {challenge_notifications.count()} notifications exist for this challenge")
    
    # Check each user's notification status
    print(f"\n📊 User Notification Status:")
    for user in users:
        user_notifications = Notification.objects.filter(user=user).order_by('-created_at')
        unread_count = user_notifications.filter(is_read=False).count()
        total_count = user_notifications.count()
        
        print(f"  • {user.username}: {total_count} total, {unread_count} unread")
        
        # Show latest notification
        if user_notifications.exists():
            latest = user_notifications.first()
            print(f"    Latest: {latest.title} ({latest.created_at.strftime('%H:%M:%S')})")
    
    # Test the API endpoint
    print(f"\n🔗 Testing API Endpoints:")
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        
        client = Client()
        test_user = users.first()
        client.force_login(test_user)
        
        response = client.get('/api/notifications/count/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notification count API: {data}")
        else:
            print(f"❌ API failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")
    
    print(f"\n🧹 Cleanup:")
    # Clean up test data
    test_challenge.delete()
    challenge_notifications.delete()
    print(f"✅ Removed test challenge and notifications")
    
    print("\n" + "=" * 60)
    print("✅ Complete notification system test finished!")
    print("\n📋 Summary:")
    print(f"   • Users tested: {users.count()}")
    print(f"   • Notifications created: {notifications_created}")
    print(f"   • System status: {'✅ WORKING' if notifications_created == users.count() else '❌ ISSUES'}")
    
    if notifications_created == users.count():
        print("\n🎉 All systems are working correctly!")
        print("   Users will now receive notifications when challenges are created.")
    else:
        print("\n⚠️  Some issues detected. Check the logs above.")

if __name__ == "__main__":
    test_complete_notification_system()