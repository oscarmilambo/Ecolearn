# community/notifications.py
"""
Notification Service for SMS, WhatsApp, and Email
Handles sending notifications for events, challenges, and community updates
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Unified notification service supporting SMS, WhatsApp, and Email
    """
    
    def __init__(self):
        # Initialize Twilio client if credentials are available
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID:
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.twilio_phone = settings.TWILIO_PHONE_NUMBER
            self.twilio_whatsapp = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
        else:
            self.twilio_client = None
            logger.warning("Twilio credentials not configured")
    
    def send_sms(self, to_number, message):
        """
        Send SMS message via Twilio
        
        Args:
            to_number: Phone number with country code
            message: Message text
        
        Returns:
            dict: {'success': bool, 'message_sid': str, 'error': str}
        """
        if not self.twilio_client:
            return {'success': False, 'error': 'SMS not configured'}
        
        try:
            # Format phone number
            if not to_number.startswith('+'):
                to_number = f'+260{to_number}'
            
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to_number
            )
            
            logger.info(f"SMS sent to {to_number}: {message_obj.sid}")
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status
            }
        
        except Exception as e:
            logger.error(f"SMS send failed to {to_number}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_whatsapp(self, to_number, message, media_url=None):
        """
        Send WhatsApp message via Twilio
        
        Args:
            to_number: Phone number with country code
            message: Message text
            media_url: Optional image/video URL
        
        Returns:
            dict: {'success': bool, 'message_sid': str, 'error': str}
        """
        if not self.twilio_client or not self.twilio_whatsapp:
            return {'success': False, 'error': 'WhatsApp not configured'}
        
        try:
            # Format WhatsApp number
            if not to_number.startswith('whatsapp:'):
                if not to_number.startswith('+'):
                    to_number = f'+260{to_number}'
                to_number = f'whatsapp:{to_number}'
            
            params = {
                'body': message,
                'from_': self.twilio_whatsapp,
                'to': to_number
            }
            
            if media_url:
                params['media_url'] = [media_url]
            
            message_obj = self.twilio_client.messages.create(**params)
            
            logger.info(f"WhatsApp sent to {to_number}: {message_obj.sid}")
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status
            }
        
        except Exception as e:
            logger.error(f"WhatsApp send failed to {to_number}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_email(self, to_email, subject, message, html_message=None):
        """
        Send email via Django
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            message: Plain text message
            html_message: Optional HTML version
        
        Returns:
            dict: {'success': bool, 'error': str}
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Email sent to {to_email}")
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Email send failed to {to_email}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def notify_user(self, user, notification_type, data, channels=None):
        """
        Send notification to user via their preferred channels
        
        Args:
            user: User object
            notification_type: Type of notification (event, challenge, reward, etc.)
            data: Dict with notification data
            channels: List of channels to use (default: user preferences)
        
        Returns:
            dict: Results for each channel
        """
        results = {}
        
        # Get user preferences
        if channels is None:
            prefs = getattr(user, 'notification_preferences', None)
            if prefs:
                channels = []
                if prefs.sms_enabled:
                    channels.append('sms')
                if prefs.whatsapp_enabled:
                    channels.append('whatsapp')
                if prefs.email_enabled:
                    channels.append('email')
            else:
                channels = ['email']  # Default to email
        
        # Generate message based on type
        message = self._generate_message(notification_type, data)
        
        # Send via each channel
        if 'sms' in channels and hasattr(user, 'phone_number') and user.phone_number:
            results['sms'] = self.send_sms(user.phone_number, message['sms'])
        
        if 'whatsapp' in channels and hasattr(user, 'phone_number') and user.phone_number:
            results['whatsapp'] = self.send_whatsapp(
                user.phone_number,
                message['whatsapp'],
                data.get('image_url')
            )
        
        if 'email' in channels and user.email:
            results['email'] = self.send_email(
                user.email,
                message['subject'],
                message['text'],
                message.get('html')
            )
        
        return results
    
    def _generate_message(self, notification_type, data):
        """Generate notification messages for different types"""
        
        messages = {
            'event_reminder': {
                'sms': f"📅 Event: {data['event_name']}\n{data['date']} at {data['time']}\nLocation: {data['location']}\nRegister: {data['url']}",
                'whatsapp': f"📅 *Upcoming Event Alert!*\n\n*Event:* {data['event_name']}\n*Date:* {data['date']}\n*Time:* {data['time']}\n*Location:* {data['location']}\n\nRegister now: {data['url']}\n\nSee you there! 🌱",
                'subject': f"Reminder: {data['event_name']}",
                'text': f"You have an upcoming event: {data['event_name']} on {data['date']} at {data['time']}. Location: {data['location']}. Register: {data['url']}",
            },
            'challenge_update': {
                'sms': f"🏆 {data['challenge_name']}\nProgress: {data['progress']}%\nRank: #{data['rank']}\nKeep going!",
                'whatsapp': f"🏆 *Challenge Update!*\n\n*Challenge:* {data['challenge_name']}\n*Your Progress:* {data['progress']}% complete\n*Rank:* #{data['rank']} out of {data['total']}\n\nKeep going! You're doing great! 💪",
                'subject': f"Challenge Update: {data['challenge_name']}",
                'text': f"Your progress in {data['challenge_name']}: {data['progress']}% complete. You're ranked #{data['rank']}!",
            },
            'reward_redeemed': {
                'sms': f"🎁 Reward: {data['reward_name']}\nCode: {data['code']}\nStatus: {data['status']}",
                'whatsapp': f"🎁 *Reward Redeemed!*\n\n*Reward:* {data['reward_name']}\n*Redemption Code:* {data['code']}\n*Status:* {data['status']}\n\nCollect at: {data.get('location', 'TBA')}\nContact: {data.get('contact', 'TBA')}",
                'subject': f"Reward Redeemed: {data['reward_name']}",
                'text': f"Your reward '{data['reward_name']}' has been redeemed. Code: {data['code']}. Status: {data['status']}",
            },
            'campaign_launch': {
                'sms': f"🚀 New: {data['campaign_name']}\n{data['duration']}\nJoin: {data['url']}",
                'whatsapp': f"🚀 *New Campaign Launched!*\n\n*Campaign:* {data['campaign_name']}\n*Duration:* {data['duration']}\n*Goal:* {data['goal']}\n\nJoin now: {data['url']}\n\nTogether we can make a difference! 🌱",
                'subject': f"New Campaign: {data['campaign_name']}",
                'text': f"A new campaign has been launched: {data['campaign_name']}. Duration: {data['duration']}. Join: {data['url']}",
            },
            'test': {
                'sms': data.get('message', 'Test notification from EcoLearn! 🎉'),
                'whatsapp': data.get('message', '✅ *Test Notification*\n\nThis is a test notification from EcoLearn!\n\nYour notifications are working correctly. 🎉'),
                'subject': 'Test Notification - EcoLearn',
                'text': data.get('message', 'This is a test notification from EcoLearn! Your notifications are working correctly. 🎉'),
            }
        }
        
        return messages.get(notification_type, {
            'sms': data.get('message', ''),
            'whatsapp': data.get('message', ''),
            'subject': data.get('subject', 'EcoLearn Notification'),
            'text': data.get('message', '')
        })
    
    def bulk_notify(self, users, notification_type, data, channels=None):
        """
        Send notifications to multiple users
        
        Args:
            users: QuerySet or list of User objects
            notification_type: Type of notification
            data: Notification data
            channels: Channels to use
        
        Returns:
            dict: Summary of results
        """
        results = {
            'total': len(users),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for user in users:
            try:
                user_results = self.notify_user(user, notification_type, data, channels)
                if any(r.get('success') for r in user_results.values()):
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"User {user.id}: {str(e)}")
        
        return results


# Singleton instance
notification_service = NotificationService()


# Helper functions for common notifications
def notify_event_reminder(event, hours_before=24):
    """Send event reminder to all registered participants"""
    from .models import EventParticipant
    
    participants = EventParticipant.objects.filter(
        event=event,
        status='registered'
    ).select_related('user')
    
    data = {
        'event_name': event.title,
        'date': event.start_date.strftime('%B %d, %Y'),
        'time': event.start_date.strftime('%I:%M %p'),
        'location': event.location,
        'url': f"{settings.SITE_URL}/community/events/{event.id}/"
    }
    
    users = [p.user for p in participants]
    return notification_service.bulk_notify(users, 'event_reminder', data)


def notify_challenge_update(challenge, user, progress, rank, total):
    """Send challenge progress update to user"""
    data = {
        'challenge_name': challenge.title,
        'progress': progress,
        'rank': rank,
        'total': total
    }
    
    return notification_service.notify_user(user, 'challenge_update', data)


def notify_reward_redemption(redemption):
    """Send reward redemption confirmation"""
    data = {
        'reward_name': redemption.reward.name,
        'code': redemption.redemption_code,
        'status': redemption.get_status_display(),
        'location': getattr(redemption.reward, 'collection_location', 'TBA'),
        'contact': getattr(redemption.reward, 'contact_info', 'TBA')
    }
    
    return notification_service.notify_user(redemption.user, 'reward_redeemed', data)



def send_notification(user, title, message, notification_type='general', link=None):
    """
    Helper function to send in-app notification and create notification record
    
    Args:
        user: User object
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        link: Optional URL link
    
    Returns:
        Notification object
    """
    from .models import Notification
    
    # Create in-app notification
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        url=link
    )
    
    # Optionally send via other channels based on user preferences
    try:
        if hasattr(user, 'notification_preferences'):
            prefs = user.notification_preferences
            
            # Send SMS if enabled
            if prefs.sms_enabled and user.phone_number:
                result = notification_service.send_sms(
                    str(user.phone_number),
                    f"[EcoLearn] {message[:140]}"
                )
                if result.get('success'):
                    notification.is_sent_sms = True
            
            # Send WhatsApp if enabled
            if prefs.whatsapp_enabled and user.phone_number:
                result = notification_service.send_whatsapp(
                    str(user.phone_number),
                    f"*{title}*\n\n{message}"
                )
                if result.get('success'):
                    notification.is_sent_whatsapp = True
            
            notification.save()
    except Exception as e:
        logger.error(f"Error sending multi-channel notification: {str(e)}")
    
    return notification


def send_emergency_alert(alert_type, severity, title, message, location, affected_areas='', 
                        hygiene_tips='', nearest_clinics='', target_locations=None, created_by=None):
    """
    Send emergency health alert to users
    
    Args:
        alert_type: Type of alert (cholera, flooding, hazardous_waste, etc.)
        severity: Severity level (critical, high, medium, low)
        title: Alert title
        message: Alert message
        location: Primary location
        affected_areas: Comma-separated affected areas
        hygiene_tips: Safety instructions
        nearest_clinics: Emergency contacts
        target_locations: List of locations to target (None = all users)
        created_by: User creating the alert
    
    Returns:
        dict: Results of alert sending
    """
    from .models import HealthAlert, Notification
    from accounts.models import CustomUser
    from django.db.models import Q
    
    # Create health alert record
    alert = HealthAlert.objects.create(
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        location=location,
        affected_areas=affected_areas,
        hygiene_tips=hygiene_tips,
        nearest_clinics=nearest_clinics,
        created_by=created_by,
        is_active=True
    )
    
    # Get target users
    users = CustomUser.objects.filter(is_active=True)
    
    if target_locations:
        location_q = Q()
        for loc in target_locations:
            location_q |= Q(location__icontains=loc)
        users = users.filter(location_q)
    
    # Prepare emergency messages
    severity_emoji = {
        'low': '⚠️',
        'medium': '🚨',
        'high': '🔴',
        'critical': '🚨🔴'
    }
    
    emoji = severity_emoji.get(severity, '⚠️')
    
    # SMS message (short)
    sms_message = f"{emoji} HEALTH ALERT: {title}. {message[:100]}... Safety: {hygiene_tips[:50]}..."
    
    # WhatsApp message (detailed)
    whatsapp_message = f"""
{emoji} *HEALTH ALERT - {severity.upper()}*

*{title}*

*Location:* {location}
{f"*Affected Areas:* {affected_areas}" if affected_areas else ""}

*Alert:*
{message}

*Safety Tips:*
{hygiene_tips}

{f"*Nearest Clinics:*\n{nearest_clinics}" if nearest_clinics else ""}

Stay safe! - EcoLearn Emergency System
    """.strip()
    
    # Send to users
    results = {
        'alert_id': alert.id,
        'total_users': users.count(),
        'sms_sent': 0,
        'whatsapp_sent': 0,
        'inapp_sent': 0,
        'failed': 0
    }
    
    for user in users:
        try:
            # SMS
            if user.phone_number:
                result = notification_service.send_sms(
                    str(user.phone_number),
                    sms_message[:160]
                )
                if result.get('success'):
                    results['sms_sent'] += 1
                else:
                    results['failed'] += 1
            
            # WhatsApp
            if user.phone_number:
                result = notification_service.send_whatsapp(
                    str(user.phone_number),
                    whatsapp_message
                )
                if result.get('success'):
                    results['whatsapp_sent'] += 1
                else:
                    results['failed'] += 1
            
            # In-app notification (always create for emergencies)
            Notification.objects.create(
                user=user,
                notification_type='emergency',
                title=f"{emoji} {title}",
                message=message,
                url=f'/health-alerts/{alert.id}/'
            )
            results['inapp_sent'] += 1
            
        except Exception as e:
            results['failed'] += 1
            logger.error(f"Emergency alert send error: {str(e)}")
    
    return results


def send_cholera_alert(location, affected_areas='', nearest_clinics='', target_locations=None, created_by=None):
    """Quick function to send cholera outbreak alert"""
    return send_emergency_alert(
        alert_type='cholera',
        severity='critical',
        title=f'Cholera Outbreak Alert - {location}',
        message=f'Cholera cases confirmed in {location}. Immediate precautions required to prevent spread.',
        location=location,
        affected_areas=affected_areas,
        hygiene_tips='Boil all drinking water for 5 minutes. Wash hands with soap frequently. Avoid raw or undercooked food. Use ORS if symptoms occur. Seek immediate medical care for severe symptoms.',
        nearest_clinics=nearest_clinics or 'Contact nearest health facility immediately if symptoms develop.',
        target_locations=target_locations,
        created_by=created_by
    )


def send_flooding_alert(location, affected_areas='', target_locations=None, created_by=None):
    """Quick function to send flooding warning"""
    return send_emergency_alert(
        alert_type='flooding',
        severity='high',
        title=f'Flooding Warning - {location}',
        message=f'Heavy rainfall causing flooding in {location}. Avoid flooded areas and take safety precautions.',
        location=location,
        affected_areas=affected_areas,
        hygiene_tips='Avoid walking or driving through flood water. Move to higher ground. Boil water after floods. Watch for contamination. Stay away from downed power lines.',
        nearest_clinics='Contact emergency services if trapped: 999. Seek medical attention for injuries or illness after flood exposure.',
        target_locations=target_locations,
        created_by=created_by
    )


def send_medical_waste_alert(location, affected_areas='', target_locations=None, created_by=None):
    """Quick function to send medical waste hazard alert"""
    return send_emergency_alert(
        alert_type='hazardous_waste',
        severity='high',
        title=f'Medical Waste Alert - {location}',
        message=f'Medical waste discovered at {location}. Avoid contact and keep children away from the area.',
        location=location,
        affected_areas=affected_areas,
        hygiene_tips='Do not touch medical waste. Keep children and pets away. Wash hands thoroughly if accidental contact occurs. Do not burn or bury medical waste.',
        nearest_clinics='Seek immediate medical attention if injured by medical waste or if exposure occurs. Contact nearest clinic for advice.',
        target_locations=target_locations,
        created_by=created_by
    )