"""
READY-TO-USE NOTIFICATION EXAMPLES
Copy and paste these into your views!
"""

from community.notifications import send_notification, notification_service
from community.models import Notification, NotificationLog
from django.utils import timezone

# ============================================================================
# EXAMPLE 1: Simple Notification (Recommended - Easiest)
# ============================================================================

def send_simple_notification(user):
    """Send notification via all enabled channels"""
    send_notification(
        user=user,
        title="Welcome to EcoLearn!",
        message="Start your environmental journey today.",
        notification_type='general',
        link='/dashboard/'
    )
    # That's it! User receives SMS, WhatsApp, Email, and In-app notification


# ============================================================================
# EXAMPLE 2: Report Status Update
# ============================================================================

def notify_report_verified(report):
    """Notify user when their report is verified"""
    if report.reporter and not report.is_anonymous:
        send_notification(
            user=report.reporter,
            title=f'Report Verified: {report.reference_number}',
            message='Your report has been verified and forwarded to authorities. Thank you!',
            notification_type='report_update',
            link=f'/reporting/reports/{report.id}/'
        )


# ============================================================================
# EXAMPLE 3: Challenge Progress Update
# ============================================================================

def notify_challenge_milestone(user, challenge, progress):
    """Notify user at challenge milestones (25%, 50%, 75%, 100%)"""
    if progress in [25, 50, 75, 100]:
        send_notification(
            user=user,
            title=f'Challenge Progress: {progress}%',
            message=f'Great work! You\'re {progress}% complete in {challenge.title}!',
            notification_type='challenge_update',
            link=f'/community/challenges/{challenge.id}/'
        )


# ============================================================================
# EXAMPLE 4: Badge Earned
# ============================================================================

def notify_badge_earned(user, badge):
    """Notify user when they earn a badge"""
    send_notification(
        user=user,
        title=f'Badge Earned: {badge.name}! 🏆',
        message=f'Congratulations! You earned the {badge.name} badge.',
        notification_type='achievement',
        link='/gamification/badges/'
    )


# ============================================================================
# EXAMPLE 5: Event Reminder (24 hours before)
# ============================================================================

def send_event_reminder(event, participant):
    """Send reminder 24 hours before event"""
    send_notification(
        user=participant.user,
        title=f'Event Tomorrow: {event.title}',
        message=f'Join us tomorrow at {event.start_date.strftime("%I:%M %p")} at {event.location}',
        notification_type='event_reminder',
        link=f'/community/events/{event.id}/'
    )


# ============================================================================
# EXAMPLE 6: Bulk Notification to Multiple Users
# ============================================================================

def send_bulk_campaign(users, title, message):
    """Send notification to multiple users"""
    from community.models import NotificationLog
    
    sent_count = 0
    failed_count = 0
    
    for user in users:
        try:
            send_notification(
                user=user,
                title=title,
                message=message,
                notification_type='campaign'
            )
            sent_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to send to {user.username}: {e}")
    
    return {
        'sent': sent_count,
        'failed': failed_count
    }


# ============================================================================
# EXAMPLE 7: SMS Only (Specific Channel)
# ============================================================================

def send_sms_only(user, message):
    """Send SMS notification only"""
    if user.phone_number:
        result = notification_service.send_sms(
            to_number=str(user.phone_number),
            message=f"[EcoLearn] {message}"
        )
        
        if result['success']:
            print(f"SMS sent! Message ID: {result['message_sid']}")
        else:
            print(f"SMS failed: {result['error']}")
        
        return result
    return {'success': False, 'error': 'No phone number'}


# ============================================================================
# EXAMPLE 8: WhatsApp with Rich Formatting
# ============================================================================

def send_whatsapp_rich(user, title, message, link=None):
    """Send WhatsApp with rich formatting"""
    if user.phone_number:
        formatted_message = f"""
*{title}* 🌱

{message}

{f'View: {link}' if link else ''}

_EcoLearn - Together for a cleaner Zambia_
        """.strip()
        
        result = notification_service.send_whatsapp(
            to_number=str(user.phone_number),
            message=formatted_message
        )
        
        return result
    return {'success': False, 'error': 'No phone number'}


# ============================================================================
# EXAMPLE 9: Email with HTML
# ============================================================================

def send_html_email(user, subject, message, button_text='View Details', button_link='#'):
    """Send HTML email"""
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto;">
                <h2 style="color: #22c55e;">{subject}</h2>
                <p style="font-size: 16px; line-height: 1.6;">{message}</p>
                <a href="{button_link}" 
                   style="display: inline-block; background: #22c55e; color: white; 
                          padding: 12px 24px; text-decoration: none; border-radius: 5px; 
                          margin-top: 20px;">
                    {button_text}
                </a>
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                <p style="font-size: 12px; color: #666;">
                    EcoLearn - Environmental Education Platform<br>
                    Lusaka, Zambia
                </p>
            </div>
        </body>
    </html>
    """
    
    if user.email:
        result = notification_service.send_email(
            to_email=user.email,
            subject=subject,
            message=message,
            html_message=html_message
        )
        return result
    return {'success': False, 'error': 'No email'}


# ============================================================================
# EXAMPLE 10: In-App Notification Only
# ============================================================================

def create_inapp_notification(user, title, message, url=None):
    """Create in-app notification only (no SMS/WhatsApp/Email)"""
    notification = Notification.objects.create(
        user=user,
        notification_type='general',
        title=title,
        message=message,
        url=url
    )
    return notification


# ============================================================================
# EXAMPLE 11: Check User Preferences Before Sending
# ============================================================================

def send_with_preference_check(user, title, message, notification_type='general'):
    """Send notification only if user preferences allow"""
    try:
        prefs = user.notification_preferences
        
        # Check if user wants this type
        if notification_type == 'event_reminder' and not prefs.event_reminders:
            return {'success': False, 'error': 'User disabled event reminders'}
        
        # Check quiet hours
        if prefs.is_quiet_hours():
            return {'success': False, 'error': 'Quiet hours active'}
        
        # Send notification
        send_notification(user, title, message, notification_type)
        return {'success': True}
        
    except Exception as e:
        # No preferences set, send anyway
        send_notification(user, title, message, notification_type)
        return {'success': True}


# ============================================================================
# EXAMPLE 12: Scheduled Notification (for Celery/Cron)
# ============================================================================

def schedule_event_reminders():
    """Send reminders for events starting in 24 hours (run daily)"""
    from community.models import CommunityEvent, EventParticipant
    from datetime import timedelta
    
    tomorrow = timezone.now() + timedelta(hours=24)
    events = CommunityEvent.objects.filter(
        start_date__date=tomorrow.date(),
        is_active=True
    )
    
    for event in events:
        participants = EventParticipant.objects.filter(event=event)
        
        for participant in participants:
            send_event_reminder(event, participant)


# ============================================================================
# EXAMPLE 13: Notification with Tracking
# ============================================================================

def send_tracked_notification(user, title, message):
    """Send notification and track delivery"""
    # Send notification
    send_notification(user, title, message)
    
    # Check delivery status
    recent_logs = NotificationLog.objects.filter(
        user=user,
        message__icontains=message[:50]
    ).order_by('-sent_at')[:3]
    
    results = {
        'sms': None,
        'whatsapp': None,
        'email': None
    }
    
    for log in recent_logs:
        results[log.channel] = {
            'status': log.status,
            'message_sid': log.message_sid,
            'error': log.error_message
        }
    
    return results


# ============================================================================
# EXAMPLE 14: Emergency Notification (High Priority)
# ============================================================================

def send_emergency_alert(users, title, message):
    """Send urgent notification to multiple users"""
    for user in users:
        # Send via all channels immediately
        if user.phone_number:
            notification_service.send_sms(
                str(user.phone_number),
                f"🚨 URGENT: {message[:140]}"
            )
            notification_service.send_whatsapp(
                str(user.phone_number),
                f"🚨 *URGENT ALERT*\n\n*{title}*\n\n{message}"
            )
        
        if user.email:
            notification_service.send_email(
                user.email,
                f"🚨 URGENT: {title}",
                message
            )
        
        # In-app notification
        Notification.objects.create(
            user=user,
            notification_type='emergency',
            title=title,
            message=message
        )


# ============================================================================
# EXAMPLE 15: Test Notification (for debugging)
# ============================================================================

def test_notification_system(user):
    """Test all notification channels"""
    results = {}
    
    # Test SMS
    if user.phone_number:
        results['sms'] = notification_service.send_sms(
            str(user.phone_number),
            "Test SMS from EcoLearn! 🎉"
        )
    
    # Test WhatsApp
    if user.phone_number:
        results['whatsapp'] = notification_service.send_whatsapp(
            str(user.phone_number),
            "*Test WhatsApp*\n\nThis is a test notification from EcoLearn! ✅"
        )
    
    # Test Email
    if user.email:
        results['email'] = notification_service.send_email(
            user.email,
            "Test Email from EcoLearn",
            "This is a test email notification. If you received this, your email notifications are working!"
        )
    
    # Test In-App
    results['inapp'] = Notification.objects.create(
        user=user,
        notification_type='test',
        title='Test Notification',
        message='This is a test in-app notification. If you see this, it works!'
    )
    
    return results


# ============================================================================
# HOW TO USE THESE EXAMPLES
# ============================================================================

"""
1. Copy the function you need
2. Import it in your view:
   from notification_examples import send_simple_notification
   
3. Call it:
   send_simple_notification(request.user)

4. User receives notification immediately!

MOST COMMON USE CASES:
- send_simple_notification() - General notifications
- notify_report_verified() - Report updates
- notify_challenge_milestone() - Challenge progress
- notify_badge_earned() - Achievements
- send_bulk_campaign() - Marketing campaigns
"""
