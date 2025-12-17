# community/notifications.py
"""
Enhanced Notification Service with Africa's Talking Integration
Primary SMS via Africa's Talking, WhatsApp via Twilio, Email via Django
Optimized for African markets with cost-effective SMS delivery
"""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from twilio.rest import Client
import logging
import africastalking

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Enhanced notification service with Africa's Talking as primary SMS provider
    - Africa's Talking: Primary SMS (cost-effective for African numbers)
    - Twilio: WhatsApp and backup SMS
    - Django: Email notifications
    """
    
    def __init__(self):
        # Initialize Africa's Talking
        self.africas_talking_username = getattr(settings, 'AFRICAS_TALKING_USERNAME', 'sandbox')
        self.africas_talking_api_key = getattr(settings, 'AFRICAS_TALKING_API_KEY', '')
        
        if self.africas_talking_api_key:
            try:
                africastalking.initialize(self.africas_talking_username, self.africas_talking_api_key)
                self.africas_talking_sms = africastalking.SMS
                logger.info(f"Africa's Talking initialized for {self.africas_talking_username}")
            except Exception as e:
                self.africas_talking_sms = None
                logger.error(f"Africa's Talking initialization failed: {e}")
        else:
            self.africas_talking_sms = None
            logger.warning("Africa's Talking credentials not configured")
        
        # Initialize Twilio client (for WhatsApp and backup SMS)
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID:
            try:
                self.twilio_client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )
                self.twilio_phone = settings.TWILIO_PHONE_NUMBER
                self.twilio_whatsapp = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
                logger.info("Twilio client initialized for WhatsApp and backup SMS")
            except Exception as e:
                self.twilio_client = None
                logger.error(f"Twilio initialization failed: {e}")
        else:
            self.twilio_client = None
            logger.warning("Twilio credentials not configured")
    
    def send_sms(self, to_number, message, provider='auto'):
        """
        Send SMS with intelligent provider selection
        Primary: Africa's Talking (cost-effective for African numbers)
        Backup: Twilio (international numbers or fallback)
        
        Args:
            to_number: Phone number with country code
            message: Message text
            provider: 'auto', 'africas_talking', or 'twilio'
        
        Returns:
            dict: {'success': bool, 'message_sid': str, 'provider': str, 'error': str}
        """
        # Format phone number
        if not to_number.startswith('+'):
            if to_number.startswith('0'):
                to_number = '+260' + to_number[1:]  # Zambian numbers
            else:
                to_number = '+260' + to_number
        
        # Auto-select provider based on number
        if provider == 'auto':
            # Use Africa's Talking for African numbers (cheaper and better delivery)
            african_prefixes = ['+260', '+254', '+256', '+255', '+234', '+233', '+27']
            if any(to_number.startswith(prefix) for prefix in african_prefixes):
                provider = 'africas_talking'
            else:
                provider = 'twilio'
        
        # Try Africa's Talking first
        if provider == 'africas_talking' and self.africas_talking_sms:
            try:
                response = self.africas_talking_sms.send(message, [to_number])
                
                if response['SMSMessageData']['Recipients']:
                    recipient = response['SMSMessageData']['Recipients'][0]
                    if recipient['status'] == 'Success':
                        logger.info(f"SMS sent via Africa's Talking to {to_number}: {recipient['messageId']}")
                        return {
                            'success': True,
                            'message_sid': recipient['messageId'],
                            'provider': 'africas_talking',
                            'cost': recipient.get('cost', 'N/A'),
                            'status': recipient['status']
                        }
                    else:
                        # Africa's Talking failed, try Twilio as backup
                        logger.warning(f"Africa's Talking failed for {to_number}: {recipient['status']}")
                        provider = 'twilio'
                else:
                    logger.warning(f"Africa's Talking: No recipients processed for {to_number}")
                    provider = 'twilio'
                    
            except Exception as e:
                logger.error(f"Africa's Talking SMS failed to {to_number}: {str(e)}")
                provider = 'twilio'
        
        # Use Twilio as backup or for international numbers
        if provider == 'twilio' and self.twilio_client:
            try:
                message_obj = self.twilio_client.messages.create(
                    body=message,
                    from_=self.twilio_phone,
                    to=to_number
                )
                
                logger.info(f"SMS sent via Twilio to {to_number}: {message_obj.sid}")
                return {
                    'success': True,
                    'message_sid': message_obj.sid,
                    'provider': 'twilio',
                    'status': message_obj.status
                }
            
            except Exception as e:
                logger.error(f"Twilio SMS failed to {to_number}: {str(e)}")
                return {'success': False, 'error': str(e), 'provider': 'twilio'}
        
        # No SMS provider available
        return {'success': False, 'error': 'No SMS provider available or configured'}
    
    def send_bulk_sms(self, phone_numbers, message):
        """
        Send bulk SMS using Africa's Talking for efficiency
        
        Args:
            phone_numbers: List of phone numbers
            message: Message text
        
        Returns:
            dict: Bulk send results with per-number status
        """
        if not phone_numbers:
            return {'success': False, 'error': 'No phone numbers provided'}
        
        # Format phone numbers
        formatted_numbers = []
        for phone in phone_numbers:
            if not phone.startswith('+'):
                if phone.startswith('0'):
                    phone = '+260' + phone[1:]
                else:
                    phone = '+260' + phone
            formatted_numbers.append(phone)
        
        results = []
        
        # Separate African and international numbers
        african_numbers = []
        international_numbers = []
        
        african_prefixes = ['+260', '+254', '+256', '+255', '+234', '+233', '+27']
        
        for phone in formatted_numbers:
            if any(phone.startswith(prefix) for prefix in african_prefixes):
                african_numbers.append(phone)
            else:
                international_numbers.append(phone)
        
        # Send African numbers via Africa's Talking (bulk)
        if african_numbers and self.africas_talking_sms:
            try:
                response = self.africas_talking_sms.send(message, african_numbers)
                
                if response['SMSMessageData']['Recipients']:
                    for recipient in response['SMSMessageData']['Recipients']:
                        results.append({
                            'phone': recipient['number'],
                            'success': recipient['status'] == 'Success',
                            'message_id': recipient.get('messageId'),
                            'cost': recipient.get('cost'),
                            'provider': 'africas_talking',
                            'error': recipient['status'] if recipient['status'] != 'Success' else None
                        })
                        
                        if recipient['status'] == 'Success':
                            logger.info(f"Bulk SMS sent to {recipient['number']}: {recipient.get('messageId')}")
                        else:
                            logger.warning(f"Bulk SMS failed to {recipient['number']}: {recipient['status']}")
                            
            except Exception as e:
                logger.error(f"Africa's Talking bulk SMS failed: {str(e)}")
                # Add failed results for African numbers
                for phone in african_numbers:
                    results.append({
                        'phone': phone,
                        'success': False,
                        'provider': 'africas_talking',
                        'error': str(e)
                    })
        
        # Send international numbers via Twilio (individual)
        if international_numbers and self.twilio_client:
            for phone in international_numbers:
                try:
                    message_obj = self.twilio_client.messages.create(
                        body=message,
                        from_=self.twilio_phone,
                        to=phone
                    )
                    
                    results.append({
                        'phone': phone,
                        'success': True,
                        'message_id': message_obj.sid,
                        'provider': 'twilio',
                        'status': message_obj.status
                    })
                    
                    logger.info(f"International SMS sent to {phone}: {message_obj.sid}")
                    
                except Exception as e:
                    results.append({
                        'phone': phone,
                        'success': False,
                        'provider': 'twilio',
                        'error': str(e)
                    })
                    logger.error(f"International SMS failed to {phone}: {str(e)}")
        
        # Calculate summary
        total_sent = len([r for r in results if r['success']])
        total_failed = len([r for r in results if not r['success']])
        
        return {
            'success': total_sent > 0,
            'results': results,
            'total_sent': total_sent,
            'total_failed': total_failed,
            'african_numbers': len(african_numbers),
            'international_numbers': len(international_numbers)
        }

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


# Waste Management Campaign Functions
def send_waste_management_campaign(campaign_type, target_users=None, custom_message=None, location=None):
    """
    Send waste management campaigns to users using Africa's Talking
    
    Args:
        campaign_type: 'cleanup', 'recycling', 'education', 'emergency', 'general'
        target_users: QuerySet of users (None = all active users with phones)
        custom_message: Custom message override
        location: Specific location for the campaign
    
    Returns:
        dict: Campaign results with delivery statistics
    """
    from accounts.models import CustomUser
    
    if target_users is None:
        target_users = CustomUser.objects.filter(
            is_active=True, 
            phone_number__isnull=False
        ).exclude(phone_number='')
    
    # Pre-defined campaign messages optimized for SMS length
    messages = {
        'cleanup': f"🧹 EcoLearn Community Cleanup this Saturday 8AM! Location: {location or 'Community Center'}. Bring gloves & bags. Together we keep Zambia clean! 🇿🇲 Info: marabo.co.zm",
        
        'recycling': "♻️ Did you know plastic bottles take 450 years to decompose? Join our recycling program! Learn proper waste sorting & earn points. Start: marabo.co.zm/learn",
        
        'education': "📚 New Waste Management Course! Learn the 3 R's: Reduce, Reuse, Recycle. Complete modules for certificates & points. Enroll: marabo.co.zm/courses",
        
        'emergency': f"🚨 URGENT: Illegal dumping reported{f' near {location}' if location else ''}! Help keep communities clean. Report: marabo.co.zm/report or call authorities. Act now!",
        
        'general': "🌍 EcoLearn: Join our mission for cleaner communities! Learn waste management, join challenges, earn rewards. Start today: marabo.co.zm",
        
        'reminder': f"⏰ Reminder: Community event{f' at {location}' if location else ''} starts soon! Don't miss out on making a difference. Details: marabo.co.zm"
    }
    
    message = custom_message or messages.get(campaign_type, messages['general'])
    
    # Get phone numbers
    phone_numbers = [str(user.phone_number) for user in target_users if user.phone_number]
    
    if not phone_numbers:
        return {
            'success': False,
            'error': 'No users with phone numbers found',
            'total_users': target_users.count()
        }
    
    logger.info(f"Launching {campaign_type} campaign to {len(phone_numbers)} users")
    
    # Send bulk SMS via enhanced notification service
    sms_result = notification_service.send_bulk_sms(phone_numbers, message)
    
    # Create in-app notifications for all users
    from .models import Notification
    in_app_created = 0
    
    for user in target_users:
        try:
            Notification.objects.create(
                user=user,
                notification_type='campaign',
                title=f"{campaign_type.title()} Campaign",
                message=message,
                url='/community/campaigns/'
            )
            in_app_created += 1
        except Exception as e:
            logger.error(f"Failed to create in-app notification for user {user.id}: {e}")
    
    # Compile results
    result = {
        'success': sms_result['success'],
        'campaign_type': campaign_type,
        'message': message,
        'total_users': target_users.count(),
        'sms_sent': sms_result['total_sent'],
        'sms_failed': sms_result['total_failed'],
        'in_app_created': in_app_created,
        'african_numbers': sms_result.get('african_numbers', 0),
        'international_numbers': sms_result.get('international_numbers', 0),
        'detailed_results': sms_result.get('results', [])
    }
    
    # Log campaign summary
    logger.info(f"Campaign '{campaign_type}' completed: {result['sms_sent']} SMS sent, {result['in_app_created']} in-app notifications created")
    
    return result


def send_challenge_notification(user, challenge, notification_type, **kwargs):
    """
    Send challenge-related notifications (joins, completions, achievements)
    
    Args:
        user: User object
        challenge: Challenge object
        notification_type: 'joined', 'completed', 'achievement', 'reminder'
        **kwargs: Additional data for message customization
    """
    messages = {
        'joined': f"🎉 Welcome to '{challenge.title}'! Start collecting waste, earn points, climb leaderboards. Track progress: marabo.co.zm/challenges/{challenge.id}",
        
        'completed': f"🏆 Challenge '{challenge.title}' completed! You earned {kwargs.get('points', 0)} points. Total: {kwargs.get('total_points', 0)}. Well done! 🌍",
        
        'achievement': f"🌟 Achievement unlocked in '{challenge.title}': {kwargs.get('achievement', 'Eco Warrior')}! Your environmental impact is growing. Keep it up! 💚",
        
        'reminder': f"⏰ Challenge '{challenge.title}' ends in {kwargs.get('time_left', '24 hours')}! Complete your activities to earn points. Go: marabo.co.zm/challenges/{challenge.id}",
        
        'leaderboard': f"🏆 You're #{kwargs.get('rank', 1)} in '{challenge.title}'! {kwargs.get('points', 0)} points earned. Keep climbing the leaderboard! 📈"
    }
    
    message = messages.get(notification_type, kwargs.get('custom_message', f"Update for challenge: {challenge.title}"))
    
    # Send SMS if user has phone number
    sms_result = {'success': False}
    if user.phone_number:
        sms_result = notification_service.send_sms(str(user.phone_number), message)
    
    # Create in-app notification
    from .models import Notification
    try:
        notification = Notification.objects.create(
            user=user,
            notification_type='challenge',
            title=f"Challenge: {challenge.title}",
            message=message,
            url=f'/community/challenges/{challenge.id}/'
        )
        in_app_success = True
    except Exception as e:
        logger.error(f"Failed to create challenge notification for user {user.id}: {e}")
        in_app_success = False
    
    return {
        'success': sms_result['success'] or in_app_success,
        'sms_sent': sms_result['success'],
        'in_app_created': in_app_success,
        'message': message,
        'provider': sms_result.get('provider'),
        'message_id': sms_result.get('message_sid')
    }


def send_points_notification(user, points_earned, activity, total_points=None):
    """
    Send points earned notification
    """
    total_display = f"Total: {total_points}" if total_points else ""
    message = f"🏆 +{points_earned} points for '{activity}'! {total_display} You're making a real environmental impact! Keep going! 🌍"
    
    # Send SMS
    sms_result = {'success': False}
    if user.phone_number:
        sms_result = notification_service.send_sms(str(user.phone_number), message)
    
    # Create in-app notification
    from .models import Notification
    try:
        Notification.objects.create(
            user=user,
            notification_type='points',
            title=f"Points Earned: +{points_earned}",
            message=message,
            url='/dashboard/'
        )
        in_app_success = True
    except Exception as e:
        logger.error(f"Failed to create points notification for user {user.id}: {e}")
        in_app_success = False
    
    return {
        'success': sms_result['success'] or in_app_success,
        'sms_sent': sms_result['success'],
        'in_app_created': in_app_success,
        'points': points_earned,
        'provider': sms_result.get('provider')
    }