"""
Enhanced Notification Service with Africa's Talking Integration
Combines existing Twilio functionality with Africa's Talking for better African coverage
"""

from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client
import logging
from africas_talking_integration import africas_talking_service

logger = logging.getLogger(__name__)

class EnhancedNotificationService:
    """
    Enhanced notification service with dual SMS providers:
    - Africa's Talking (primary for African numbers)
    - Twilio (backup/international)
    """
    
    def __init__(self):
        # Initialize Twilio (backup)
        if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID:
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.twilio_phone = settings.TWILIO_PHONE_NUMBER
            self.twilio_whatsapp = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)
        else:
            self.twilio_client = None
        
        # Africa's Talking is initialized in africas_talking_integration
        self.africas_talking = africas_talking_service
    
    def send_sms(self, to_number, message, provider='auto'):
        """
        Send SMS with intelligent provider selection
        
        Args:
            to_number: Phone number
            message: Message text
            provider: 'auto', 'africas_talking', or 'twilio'
        
        Returns:
            dict: Result with success status and details
        """
        # Format phone number
        if not to_number.startswith('+'):
            if to_number.startswith('0'):
                to_number = '+260' + to_number[1:]  # Zambian numbers
            else:
                to_number = '+260' + to_number
        
        # Auto-select provider based on number
        if provider == 'auto':
            if to_number.startswith('+260'):  # Zambian numbers
                provider = 'africas_talking'
            else:
                provider = 'twilio'
        
        # Try Africa's Talking first for African numbers
        if provider == 'africas_talking':
            result = self.africas_talking.send_sms(to_number, message)
            if result['success']:
                result['provider'] = 'africas_talking'
                return result
            else:
                # Fallback to Twilio if Africa's Talking fails
                logger.warning(f"Africa's Talking failed for {to_number}, trying Twilio: {result['error']}")
                provider = 'twilio'
        
        # Use Twilio
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
                    'phone': to_number
                }
            
            except Exception as e:
                logger.error(f"Twilio SMS failed to {to_number}: {str(e)}")
                return {'success': False, 'error': str(e), 'provider': 'twilio'}
        
        return {'success': False, 'error': 'No SMS provider available'}
    
    def send_bulk_sms(self, phone_numbers, message):
        """
        Send bulk SMS with intelligent routing
        """
        african_numbers = []
        international_numbers = []
        
        # Separate numbers by region
        for phone in phone_numbers:
            if not phone.startswith('+'):
                if phone.startswith('0'):
                    phone = '+260' + phone[1:]
                else:
                    phone = '+260' + phone
            
            if phone.startswith(('+260', '+254', '+256', '+255', '+234')):  # African countries
                african_numbers.append(phone)
            else:
                international_numbers.append(phone)
        
        results = []
        
        # Send African numbers via Africa's Talking
        if african_numbers:
            at_result = self.africas_talking.send_bulk_sms(african_numbers, message)
            if at_result['success']:
                for r in at_result['results']:
                    r['provider'] = 'africas_talking'
                results.extend(at_result['results'])
        
        # Send international numbers via Twilio
        if international_numbers and self.twilio_client:
            for phone in international_numbers:
                twilio_result = self.send_sms(phone, message, provider='twilio')
                results.append({
                    'phone': phone,
                    'success': twilio_result['success'],
                    'message_id': twilio_result.get('message_sid'),
                    'error': twilio_result.get('error'),
                    'provider': 'twilio'
                })
        
        return {
            'success': True,
            'results': results,
            'total_sent': len([r for r in results if r['success']]),
            'total_failed': len([r for r in results if not r['success']])
        }
    
    def send_whatsapp(self, to_number, message, media_url=None):
        """
        Send WhatsApp via Twilio (Africa's Talking WhatsApp coming soon)
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
                'provider': 'twilio_whatsapp'
            }
        
        except Exception as e:
            logger.error(f"WhatsApp send failed to {to_number}: {str(e)}")
            return {'success': False, 'error': str(e)}

# Create enhanced service instance
enhanced_notification_service = EnhancedNotificationService()

# Waste Management Campaign Functions
def send_waste_management_campaign(campaign_type, target_users=None, custom_message=None):
    """
    Send waste management campaigns to users
    
    Args:
        campaign_type: 'cleanup', 'recycling', 'education', 'emergency'
        target_users: QuerySet of users (None = all active users)
        custom_message: Custom message override
    
    Returns:
        dict: Campaign results
    """
    from accounts.models import CustomUser
    
    if target_users is None:
        target_users = CustomUser.objects.filter(is_active=True, phone_number__isnull=False)
    
    # Campaign messages
    messages = {
        'cleanup': "🧹 EcoLearn Community Cleanup this Saturday 8AM! Join us at Community Center. Bring gloves & bags. Together we keep Zambia clean! 🇿🇲 Register: marabo.co.zm",
        
        'recycling': "♻️ Did you know plastic bottles take 450 years to decompose? Join our recycling education program! Learn proper waste sorting & earn points. Start: marabo.co.zm/learn",
        
        'education': "📚 New Waste Management Course Available! Learn the 3 R's: Reduce, Reuse, Recycle. Complete modules to earn certificates & points. Enroll: marabo.co.zm/courses",
        
        'emergency': "🚨 URGENT: Illegal dumping reported in your area! Help us keep communities clean. Report incidents at marabo.co.zm/report or call local authorities. Act now!",
        
        'general': "🌍 EcoLearn: Join our mission for cleaner communities! Learn waste management, join challenges, earn rewards. Make a difference today: marabo.co.zm"
    }
    
    message = custom_message or messages.get(campaign_type, messages['general'])
    
    # Get phone numbers
    phone_numbers = [str(user.phone_number) for user in target_users if user.phone_number]
    
    print(f"\n📢 LAUNCHING {campaign_type.upper()} CAMPAIGN")
    print(f"📱 Targeting {len(phone_numbers)} users")
    print(f"💬 Message: {message}")
    
    # Send bulk SMS
    result = enhanced_notification_service.send_bulk_sms(phone_numbers, message)
    
    # Create in-app notifications
    from community.models import Notification
    for user in target_users:
        Notification.objects.create(
            user=user,
            notification_type='campaign',
            title=f"{campaign_type.title()} Campaign",
            message=message,
            url='/community/campaigns/'
        )
    
    print(f"\n✅ Campaign Results:")
    print(f"   📤 Total sent: {result['total_sent']}")
    print(f"   ❌ Failed: {result['total_failed']}")
    print(f"   📱 In-app notifications: {target_users.count()}")
    
    # Show provider breakdown
    providers = {}
    for r in result['results']:
        provider = r.get('provider', 'unknown')
        if provider not in providers:
            providers[provider] = {'sent': 0, 'failed': 0}
        
        if r['success']:
            providers[provider]['sent'] += 1
        else:
            providers[provider]['failed'] += 1
    
    print(f"\n📊 Provider Breakdown:")
    for provider, stats in providers.items():
        print(f"   {provider}: {stats['sent']} sent, {stats['failed']} failed")
    
    return result

def send_individual_eco_notification(user, notification_type, **kwargs):
    """
    Send individual eco-focused notifications
    """
    messages = {
        'challenge_joined': f"🎉 Welcome to '{kwargs.get('challenge_name', 'Eco Challenge')}'! Start collecting waste, earn points, climb leaderboards. Track: marabo.co.zm/challenges",
        
        'points_earned': f"🏆 +{kwargs.get('points', 10)} points for '{kwargs.get('activity', 'eco activity')}'! Total: {kwargs.get('total_points', 100)} points. You're making a difference! 🌍",
        
        'achievement_unlocked': f"🌟 Achievement: '{kwargs.get('achievement', 'Eco Warrior')}'! Your environmental impact is growing. Share your success & inspire others! 💚",
        
        'waste_report_received': f"📋 Thank you for reporting waste issue! Report #{kwargs.get('report_id', '001')} received. We'll investigate within 24hrs. Keep our communities clean! 🧹",
        
        'course_completed': f"🎓 Congratulations! Course '{kwargs.get('course_name', 'Waste Management')}' completed! Certificate earned. Apply your knowledge in real life! 📚",
        
        'reminder_cleanup': f"⏰ Reminder: Community cleanup starts in {kwargs.get('time_left', '1 hour')}! Location: {kwargs.get('location', 'Community Center')}. Don't miss out! 🧹"
    }
    
    message = messages.get(notification_type, kwargs.get('custom_message', 'EcoLearn notification'))
    
    # Send SMS
    result = enhanced_notification_service.send_sms(str(user.phone_number), message)
    
    # Create in-app notification
    from community.models import Notification
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=kwargs.get('title', notification_type.replace('_', ' ').title()),
        message=message,
        url=kwargs.get('url', '/dashboard/')
    )
    
    return result

# Demo function for presentation
def demo_enhanced_notifications():
    """
    Demo the enhanced notification system for presentation
    """
    from accounts.models import CustomUser
    
    print("🚀" * 25)
    print("🚀 ENHANCED NOTIFICATION SYSTEM DEMO")
    print("🚀 Africa's Talking + Twilio Integration")
    print("🚀" * 25)
    
    # Get demo users
    demo_users = CustomUser.objects.filter(phone_number__isnull=False)[:3]
    
    if not demo_users:
        print("❌ No users with phone numbers found for demo")
        return
    
    print(f"\n📋 Demo Users ({demo_users.count()}):")
    for user in demo_users:
        print(f"   - {user.username}: {user.phone_number}")
    
    # Demo 1: Waste Management Campaign
    print(f"\n{'='*50}")
    print("DEMO 1: COMMUNITY CLEANUP CAMPAIGN")
    print(f"{'='*50}")
    
    send_waste_management_campaign('cleanup', demo_users)
    
    input("\nPress ENTER to continue to individual notifications...")
    
    # Demo 2: Individual Notifications
    print(f"\n{'='*50}")
    print("DEMO 2: INDIVIDUAL USER NOTIFICATIONS")
    print(f"{'='*50}")
    
    user = demo_users.first()
    
    # Challenge joined
    send_individual_eco_notification(
        user, 
        'challenge_joined',
        challenge_name='Zero Waste Challenge'
    )
    
    # Points earned
    send_individual_eco_notification(
        user,
        'points_earned',
        points=75,
        activity='Plastic Bottle Collection',
        total_points=425
    )
    
    input("\nPress ENTER to continue to emergency alert...")
    
    # Demo 3: Emergency Alert
    print(f"\n{'='*50}")
    print("DEMO 3: EMERGENCY WASTE ALERT")
    print(f"{'='*50}")
    
    send_waste_management_campaign('emergency', demo_users)
    
    print(f"\n{'🎉'*50}")
    print("🎉 ENHANCED NOTIFICATION DEMO COMPLETE!")
    print(f"{'🎉'*50}")
    
    print(f"\n💡 Key Features Demonstrated:")
    print(f"   ✅ Intelligent SMS routing (Africa's Talking + Twilio)")
    print(f"   ✅ Bulk waste management campaigns")
    print(f"   ✅ Individual user notifications")
    print(f"   ✅ Emergency alert system")
    print(f"   ✅ In-app notification integration")
    print(f"   ✅ Cost optimization for African markets")

if __name__ == "__main__":
    demo_enhanced_notifications()