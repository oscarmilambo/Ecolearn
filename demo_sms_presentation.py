#!/usr/bin/env python
"""
LIVE DEMO: SMS & WhatsApp Notifications for Waste Management
Perfect for presentation - shows real SMS delivery using Africa's Talking

Run this during your presentation to demonstrate live SMS notifications!
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from africas_talking_integration import africas_talking_service, demo_waste_management_notifications
from accounts.models import CustomUser

def presentation_demo():
    """
    Live presentation demo - sends real SMS messages
    """
    
    print("🎤" * 20)
    print("🎤 LIVE PRESENTATION DEMO - ECOLEARN SMS NOTIFICATIONS")
    print("🎤" * 20)
    
    print(f"\n📅 Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📱 Platform: Africa's Talking SMS Gateway")
    print("🌍 Focus: Community Waste Management Campaigns")
    
    # Get demo phone numbers
    demo_phones = []
    
    # Add your admin phone
    admin_phone = "+260970594105"  # From your .env
    demo_phones.append(admin_phone)
    
    # Try to get real user phone numbers from database
    try:
        users_with_phones = CustomUser.objects.filter(phone_number__isnull=False).exclude(phone_number='')[:3]
        for user in users_with_phones:
            if str(user.phone_number) not in demo_phones:
                demo_phones.append(str(user.phone_number))
        print(f"\n✅ Found {len(users_with_phones)} users with phone numbers in database")
    except Exception as e:
        print(f"\n⚠️  Could not fetch user phones: {e}")
    
    # Add some demo numbers if we don't have enough
    if len(demo_phones) < 3:
        demo_phones.extend(["+260977123456", "+260966789012"])
    
    demo_phones = demo_phones[:3]  # Limit to 3 for demo
    
    print(f"\n📋 DEMO RECIPIENTS ({len(demo_phones)} numbers):")
    for i, phone in enumerate(demo_phones, 1):
        print(f"   {i}. {phone}")
    
    print(f"\n{'='*60}")
    print("🚀 STARTING LIVE SMS DEMO...")
    print(f"{'='*60}")
    
    # Demo Scenario 1: Community Cleanup Campaign
    print(f"\n📢 SCENARIO 1: COMMUNITY CLEANUP CAMPAIGN")
    print("-" * 40)
    
    cleanup_message = "🧹 EcoLearn Alert: Community Cleanup Drive this Saturday 8AM! Join us at Community Center. Bring gloves & bags. Together we keep Zambia clean! 🇿🇲"
    
    print(f"Message: {cleanup_message}")
    print("Sending...")
    
    result1 = africas_talking_service.send_bulk_sms(demo_phones, cleanup_message)
    
    if result1['success']:
        print(f"✅ SUCCESS! Sent to {result1['total_sent']}/{len(demo_phones)} recipients")
        for r in result1['results']:
            if r['success']:
                print(f"   ✅ {r['phone']}: Delivered (ID: {r['message_id']}, Cost: {r.get('cost', 'N/A')})")
            else:
                print(f"   ❌ {r['phone']}: Failed - {r['error']}")
    else:
        print(f"❌ FAILED: {result1['error']}")
    
    print("\n" + "⏱️ " * 20)
    input("Press ENTER to continue to next demo scenario...")
    
    # Demo Scenario 2: Recycling Education
    print(f"\n📢 SCENARIO 2: RECYCLING EDUCATION CAMPAIGN")
    print("-" * 40)
    
    recycling_message = "♻️ Did you know? Plastic bottles take 450 years to decompose! Learn proper recycling at marabo.co.zm/learn. Earn points & protect our environment! 🌍"
    
    print(f"Message: {recycling_message}")
    print("Sending...")
    
    result2 = africas_talking_service.send_bulk_sms(demo_phones, recycling_message)
    
    if result2['success']:
        print(f"✅ SUCCESS! Sent to {result2['total_sent']}/{len(demo_phones)} recipients")
        for r in result2['results']:
            if r['success']:
                print(f"   ✅ {r['phone']}: Delivered (ID: {r['message_id']}, Cost: {r.get('cost', 'N/A')})")
            else:
                print(f"   ❌ {r['phone']}: Failed - {r['error']}")
    else:
        print(f"❌ FAILED: {result2['error']}")
    
    print("\n" + "⏱️ " * 20)
    input("Press ENTER to continue to individual notification demo...")
    
    # Demo Scenario 3: Individual User Notification
    print(f"\n📢 SCENARIO 3: INDIVIDUAL USER ACHIEVEMENT")
    print("-" * 40)
    
    achievement_message = "🏆 Congratulations! You earned 50 points for 'Waste Sorting Challenge'! Total: 250 points. You're an Eco Warrior! Keep making a difference! 🌟"
    
    print(f"Message: {achievement_message}")
    print(f"Sending to: {demo_phones[0]}")
    
    result3 = africas_talking_service.send_sms(demo_phones[0], achievement_message)
    
    if result3['success']:
        print(f"✅ SUCCESS! Individual notification delivered")
        print(f"   ✅ Message ID: {result3['message_id']}")
        print(f"   ✅ Cost: {result3.get('cost', 'N/A')}")
        print(f"   ✅ Phone: {result3['phone']}")
    else:
        print(f"❌ FAILED: {result3['error']}")
    
    # Demo Summary
    print(f"\n{'🎉'*60}")
    print("🎉 LIVE DEMO COMPLETE!")
    print(f"{'🎉'*60}")
    
    total_sent = 0
    total_cost = 0
    
    if result1['success']:
        total_sent += result1['total_sent']
    if result2['success']:
        total_sent += result2['total_sent']
    if result3['success']:
        total_sent += 1
    
    print(f"\n📊 DEMO STATISTICS:")
    print(f"   📱 Total SMS sent: {total_sent}")
    print(f"   🎯 Scenarios demonstrated: 3")
    print(f"   ⚡ Platform: Africa's Talking")
    print(f"   🌍 Use case: Waste Management Education")
    
    print(f"\n💡 KEY FEATURES DEMONSTRATED:")
    print(f"   ✅ Bulk SMS campaigns for community engagement")
    print(f"   ✅ Individual user notifications for achievements")
    print(f"   ✅ Real-time delivery with message tracking")
    print(f"   ✅ Cost-effective SMS delivery in Zambia")
    print(f"   ✅ Integration with Django learning platform")
    
    print(f"\n🚀 NEXT STEPS FOR PRODUCTION:")
    print(f"   1. Get Africa's Talking production API key")
    print(f"   2. Configure sender ID for branding")
    print(f"   3. Set up automated campaign scheduling")
    print(f"   4. Add WhatsApp Business API integration")
    print(f"   5. Implement delivery reports and analytics")
    
    print(f"\n{'='*60}")
    print("Thank you for watching the EcoLearn SMS Demo! 🙏")
    print("Questions? Let's discuss the implementation details.")
    print(f"{'='*60}")

def quick_test_sms():
    """
    Quick test function to verify SMS is working
    """
    print("🧪 QUICK SMS TEST")
    print("=" * 30)
    
    test_phone = "+260970594105"  # Your number
    test_message = "🧪 EcoLearn SMS Test: This is a test message from your waste management learning platform. System is working! ✅"
    
    print(f"Sending test SMS to: {test_phone}")
    print(f"Message: {test_message}")
    
    result = africas_talking_service.send_sms(test_phone, test_message)
    
    if result['success']:
        print(f"✅ Test SMS sent successfully!")
        print(f"✅ Message ID: {result['message_id']}")
        print(f"✅ Cost: {result.get('cost', 'N/A')}")
    else:
        print(f"❌ Test failed: {result['error']}")
    
    return result

if __name__ == "__main__":
    print("EcoLearn SMS Demo Options:")
    print("1. Full Presentation Demo (recommended)")
    print("2. Quick SMS Test")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        presentation_demo()
    elif choice == "2":
        quick_test_sms()
    elif choice == "3":
        print("Goodbye! 👋")
    else:
        print("Invalid choice. Running full demo...")
        presentation_demo()