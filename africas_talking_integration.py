"""
Africa's Talking SMS and WhatsApp Integration for EcoLearn
Simple demo-ready implementation for waste management campaigns
"""

import os
import africastalking
from django.conf import settings
from decouple import config

class AfricasTalkingService:
    """
    Africa's Talking service for SMS and WhatsApp notifications
    """
    
    def __init__(self):
        # Initialize Africa's Talking
        self.username = config('AFRICAS_TALKING_USERNAME', default='sandbox')
        self.api_key = config('AFRICAS_TALKING_API_KEY', default='')
        
        if self.api_key:
            africastalking.initialize(self.username, self.api_key)
            self.sms = africastalking.SMS
            print(f"✅ Africa's Talking initialized for {self.username}")
        else:
            print("❌ Africa's Talking API key not configured")
            self.sms = None
    
    def send_sms(self, phone_number, message):
        """
        Send SMS via Africa's Talking
        """
        if not self.sms:
            return {'success': False, 'error': 'SMS service not initialized'}
        
        try:
            # Ensure phone number is in international format
            if not phone_number.startswith('+'):
                if phone_number.startswith('0'):
                    phone_number = '+260' + phone_number[1:]  # Zambian numbers
                else:
                    phone_number = '+260' + phone_number
            
            # Send SMS
            response = self.sms.send(message, [phone_number])
            
            if response['SMSMessageData']['Recipients']:
                recipient = response['SMSMessageData']['Recipients'][0]
                if recipient['status'] == 'Success':
                    return {
                        'success': True,
                        'message_id': recipient['messageId'],
                        'cost': recipient['cost'],
                        'phone': phone_number
                    }
                else:
                    return {
                        'success': False,
                        'error': recipient['status'],
                        'phone': phone_number
                    }
            else:
                return {'success': False, 'error': 'No recipients processed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_bulk_sms(self, phone_numbers, message):
        """
        Send SMS to multiple recipients
        """
        if not self.sms:
            return {'success': False, 'error': 'SMS service not initialized'}
        
        try:
            # Format phone numbers
            formatted_numbers = []
            for phone in phone_numbers:
                if not phone.startswith('+'):
                    if phone.startswith('0'):
                        phone = '+260' + phone[1:]
                    else:
                        phone = '+260' + phone
                formatted_numbers.append(phone)
            
            # Send bulk SMS
            response = self.sms.send(message, formatted_numbers)
            
            results = []
            if response['SMSMessageData']['Recipients']:
                for recipient in response['SMSMessageData']['Recipients']:
                    results.append({
                        'phone': recipient['number'],
                        'success': recipient['status'] == 'Success',
                        'message_id': recipient.get('messageId'),
                        'cost': recipient.get('cost'),
                        'error': recipient['status'] if recipient['status'] != 'Success' else None
                    })
            
            return {
                'success': True,
                'results': results,
                'total_sent': len([r for r in results if r['success']])
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Initialize the service
africas_talking_service = AfricasTalkingService()

# Demo functions for waste management campaigns
def send_waste_management_campaign_sms(phone_numbers, campaign_type="general"):
    """
    Send waste management campaign SMS to multiple users
    """
    
    messages = {
        "general": "🌍 EcoLearn Alert: Join our community waste management campaign! Proper waste disposal protects our environment. Learn more at marabo.co.zm",
        
        "recycling": "♻️ Recycling Campaign: Did you know plastic bottles take 450 years to decompose? Join our recycling drive this weekend! Details: marabo.co.zm/campaigns",
        
        "cleanup": "🧹 Community Cleanup: Join us this Saturday 8AM for a neighborhood cleanup! Bring gloves and bags. Meeting point: Community Center. Register: marabo.co.zm",
        
        "education": "📚 Waste Education: Learn the 3 R's - Reduce, Reuse, Recycle! Complete our waste management course and earn points. Start: marabo.co.zm/learn",
        
        "emergency": "🚨 URGENT: Illegal dumping reported in your area! Help us keep our community clean. Report incidents at marabo.co.zm/report or call 911."
    }
    
    message = messages.get(campaign_type, messages["general"])
    
    print(f"\n📱 Sending {campaign_type.upper()} campaign SMS to {len(phone_numbers)} recipients...")
    print(f"Message: {message}")
    
    result = africas_talking_service.send_bulk_sms(phone_numbers, message)
    
    if result['success']:
        print(f"✅ Campaign sent successfully!")
        print(f"✅ Total delivered: {result['total_sent']}/{len(phone_numbers)}")
        
        # Show individual results
        for r in result['results']:
            status = "✅ Sent" if r['success'] else f"❌ Failed: {r['error']}"
            cost = f" (Cost: {r['cost']})" if r.get('cost') else ""
            print(f"   {r['phone']}: {status}{cost}")
    else:
        print(f"❌ Campaign failed: {result['error']}")
    
    return result

def send_individual_notification(phone_number, notification_type, **kwargs):
    """
    Send individual notifications for specific events
    """
    
    messages = {
        "challenge_joined": f"🎉 Welcome to the challenge '{kwargs.get('challenge_name', 'Eco Challenge')}'! Start collecting points and make a difference. Track progress: marabo.co.zm",
        
        "points_earned": f"🏆 Congratulations! You earned {kwargs.get('points', 10)} points for '{kwargs.get('activity', 'eco activity')}'. Total points: {kwargs.get('total_points', 100)}. Keep going!",
        
        "reminder": f"⏰ Reminder: {kwargs.get('event_name', 'Eco event')} starts in {kwargs.get('time_left', '1 hour')}. Don't miss out! Details: marabo.co.zm",
        
        "achievement": f"🌟 Achievement Unlocked: {kwargs.get('achievement', 'Eco Warrior')}! You're making a real impact on our environment. Share your success!",
        
        "report_received": f"📋 Thank you for reporting environmental issues! Your report #{kwargs.get('report_id', '001')} has been received and will be reviewed within 24 hours."
    }
    
    message = messages.get(notification_type, f"EcoLearn notification: {kwargs.get('custom_message', 'Thank you for being part of our eco community!')}")
    
    print(f"\n📱 Sending {notification_type} notification to {phone_number}")
    print(f"Message: {message}")
    
    result = africas_talking_service.send_sms(phone_number, message)
    
    if result['success']:
        print(f"✅ Notification sent successfully!")
        print(f"✅ Message ID: {result['message_id']}")
        print(f"✅ Cost: {result.get('cost', 'N/A')}")
    else:
        print(f"❌ Failed to send: {result['error']}")
    
    return result

# Demo function for presentation
def demo_waste_management_notifications():
    """
    Demo function to showcase SMS notifications for waste management
    Perfect for presentation!
    """
    
    print("=" * 80)
    print("🌍 ECOLEARN WASTE MANAGEMENT SMS DEMO - AFRICA'S TALKING")
    print("=" * 80)
    
    # Demo phone numbers (use your actual numbers for demo)
    demo_numbers = [
        "+260970594105",  # Your number from .env
        "+260977123456",  # Demo number 1
        "+260966789012",  # Demo number 2
    ]
    
    print(f"\n📋 Demo will send to {len(demo_numbers)} numbers:")
    for num in demo_numbers:
        print(f"   - {num}")
    
    # Demo 1: General waste management campaign
    print(f"\n{'='*50}")
    print("DEMO 1: GENERAL WASTE MANAGEMENT CAMPAIGN")
    print(f"{'='*50}")
    send_waste_management_campaign_sms(demo_numbers, "general")
    
    # Demo 2: Recycling campaign
    print(f"\n{'='*50}")
    print("DEMO 2: RECYCLING AWARENESS CAMPAIGN")
    print(f"{'='*50}")
    send_waste_management_campaign_sms(demo_numbers, "recycling")
    
    # Demo 3: Individual notifications
    print(f"\n{'='*50}")
    print("DEMO 3: INDIVIDUAL USER NOTIFICATIONS")
    print(f"{'='*50}")
    
    # Challenge joined notification
    send_individual_notification(
        demo_numbers[0], 
        "challenge_joined", 
        challenge_name="Community Cleanup Challenge"
    )
    
    # Points earned notification
    send_individual_notification(
        demo_numbers[0], 
        "points_earned", 
        points=50, 
        activity="Waste Sorting", 
        total_points=250
    )
    
    # Emergency alert
    print(f"\n{'='*50}")
    print("DEMO 4: EMERGENCY WASTE ALERT")
    print(f"{'='*50}")
    send_waste_management_campaign_sms(demo_numbers, "emergency")
    
    print(f"\n{'='*80}")
    print("🎉 DEMO COMPLETE! Check your phones for messages.")
    print("💡 This demonstrates real-time SMS notifications for:")
    print("   ✅ Community waste management campaigns")
    print("   ✅ Individual user notifications")
    print("   ✅ Emergency environmental alerts")
    print("   ✅ Educational content delivery")
    print(f"{'='*80}")

if __name__ == "__main__":
    demo_waste_management_notifications()