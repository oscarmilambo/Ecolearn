#!/usr/bin/env python3
"""
Test Challenge Notifications System
Run this to verify that challenge notifications are being created properly
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
from datetime import timedelta

User = get_user_model()

def test_challenge_notifications():
    print("🧪 Testing Challenge Notification System...")
    print("=" * 50)
    
    # Get all users
    users = User.objects.filter(is_active=True)
    print(f"📊 Found {users.count()} active users")
    
    # Check recent notifications
    recent_notifications = Notification.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-created_at')
    
    print(f"📬 Recent notifications (last 24h): {recent_notifications.count()}")
    
    if recent_notifications.exists():
        print("\n📋 Recent Notifications:")
        for notif in recent_notifications[:10]:
            print(f"  • {notif.user.username}: {notif.title}")
            print(f"    Type: {notif.notification_type}")
            print(f"    Read: {notif.is_read}")
            print(f"    Created: {notif.created_at}")
            print()
    
    # Check challenge notifications specifically
    challenge_notifications = Notification.objects.filter(
        notification_type='challenge_update'
    ).order_by('-created_at')
    
    print(f"🏆 Challenge notifications (all time): {challenge_notifications.count()}")
    
    if challenge_notifications.exists():
        print("\n🏆 Challenge Notifications:")
        for notif in challenge_notifications[:5]:
            print(f"  • {notif.user.username}: {notif.title}")
            print(f"    Message: {notif.message[:100]}...")
            print(f"    Read: {notif.is_read}")
            print(f"    Created: {notif.created_at}")
            print()
    
    # Check recent challenges
    recent_challenges = CommunityChallenge.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-created_at')
    
    print(f"🆕 Recent challenges (last 24h): {recent_challenges.count()}")
    
    if recent_challenges.exists():
        print("\n🆕 Recent Challenges:")
        for challenge in recent_challenges:
            print(f"  • {challenge.title}")
            print(f"    Type: {challenge.challenge_type}")
            print(f"    Active: {challenge.is_active}")
            print(f"    Created: {challenge.created_at}")
            
            # Check notifications for this challenge
            notifs_for_challenge = Notification.objects.filter(
                notification_type='challenge_update',
                title__icontains=challenge.title[:20]
            ).count()
            print(f"    Notifications sent: {notifs_for_challenge}")
            print()
    
    # Test notification creation for a specific user
    if users.exists():
        test_user = users.first()
        print(f"🧪 Testing notification creation for user: {test_user.username}")
        
        # Create a test notification
        test_notification = Notification.objects.create(
            user=test_user,
            notification_type='challenge_update',
            title='🧪 Test Challenge Notification',
            message='This is a test notification to verify the system is working.',
            url='/community/challenges/'
        )
        
        print(f"✅ Test notification created: ID {test_notification.id}")
        
        # Check if it appears in user's notifications
        user_notifications = Notification.objects.filter(user=test_user).order_by('-created_at')[:3]
        print(f"📬 User's recent notifications: {user_notifications.count()}")
        
        for notif in user_notifications:
            print(f"  • {notif.title} (Read: {notif.is_read})")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    test_challenge_notifications()