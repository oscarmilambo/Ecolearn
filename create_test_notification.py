"""
Create test notification for oscarmilambo2 to see bell icon
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from accounts.models import CustomUser
from community.models import Notification

print("=" * 70)
print("CREATE TEST NOTIFICATION")
print("=" * 70)

try:
    user = CustomUser.objects.get(username='oscarmilambo2')
    print(f"\n✅ Found user: {user.username}")
    
    # Create test notifications
    notifications = [
        {
            'title': 'Welcome to Real-Time Notifications!',
            'message': 'Your notification system is now live! You will receive instant WhatsApp and SMS alerts.',
            'notification_type': 'general',
            'url': '/accounts/notifications/preferences/'
        },
        {
            'title': 'Challenge Available',
            'message': 'Join the Kanyama Clean-Up Weekend challenge and start earning points!',
            'notification_type': 'challenge_update',
            'url': '/community/challenges/'
        },
        {
            'title': 'System Update',
            'message': 'Real-time notifications are now enabled. Check your notification preferences to customize.',
            'notification_type': 'general',
            'url': '/accounts/notifications/preferences/'
        }
    ]
    
    created_count = 0
    for notif_data in notifications:
        notification = Notification.objects.create(
            user=user,
            **notif_data
        )
        created_count += 1
        print(f"✅ Created: {notification.title}")
    
    print(f"\n🎉 Created {created_count} test notifications!")
    print(f"✅ Unread count: {user.notifications.filter(is_read=False).count()}")
    print(f"\n📍 Check the bell icon in the navbar!")
    print(f"   You should see a red badge with the number {created_count}")
    
except CustomUser.DoesNotExist:
    print("\n❌ User 'oscarmilambo2' not found!")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("=" * 70)
