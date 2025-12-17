#!/usr/bin/env python3
"""
Fix Challenge Notifications - Create notifications for existing challenge
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

def fix_recent_challenge_notifications():
    print("🔧 Fixing Challenge Notifications...")
    print("=" * 50)
    
    # Get the most recent challenge
    recent_challenge = CommunityChallenge.objects.filter(
        created_at__gte=timezone.now() - timedelta(hours=24)
    ).order_by('-created_at').first()
    
    if not recent_challenge:
        print("❌ No recent challenges found")
        return
    
    print(f"🏆 Found recent challenge: {recent_challenge.title}")
    print(f"   Created: {recent_challenge.created_at}")
    print(f"   Active: {recent_challenge.is_active}")
    
    # Check if notifications already exist for this challenge
    existing_notifications = Notification.objects.filter(
        notification_type='challenge_update',
        title__icontains=recent_challenge.title[:20]
    ).count()
    
    print(f"📬 Existing notifications: {existing_notifications}")
    
    if existing_notifications > 0:
        print("✅ Notifications already exist for this challenge")
        return
    
    # Get all active users
    active_users = User.objects.filter(is_active=True)
    print(f"👥 Active users: {active_users.count()}")
    
    # Create notifications for all users
    notifications_created = 0
    for user in active_users:
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type='challenge_update',
                title=f'🏆 New Challenge: {recent_challenge.title}',
                message=f'{recent_challenge.description[:150]}... Reward: {recent_challenge.reward_points} points!',
                url=f'/community/challenges/{recent_challenge.id}/'
            )
            notifications_created += 1
            print(f"✅ Created notification for {user.username}")
        except Exception as e:
            print(f"❌ Error creating notification for {user.username}: {e}")
    
    print(f"\n🎉 Created {notifications_created} notifications!")
    
    # Verify notifications were created
    new_notifications = Notification.objects.filter(
        notification_type='challenge_update',
        title__icontains=recent_challenge.title[:20]
    ).count()
    
    print(f"✅ Verification: {new_notifications} notifications now exist")
    print("=" * 50)

if __name__ == "__main__":
    fix_recent_challenge_notifications()