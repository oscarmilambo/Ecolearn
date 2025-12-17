#!/usr/bin/env python
"""
🎤 PRESENTATION READY: EcoLearn SMS Demo
One-click demo for waste management SMS notifications

PERFECT FOR LIVE PRESENTATION!
"""

import os
import sys
import django
from datetime import datetime
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

def presentation_banner():
    """Show presentation banner"""
    print("🎤" * 60)
    print("🎤" + " " * 56 + "🎤")
    print("🎤" + "  ECOLEARN: WASTE MANAGEMENT SMS NOTIFICATIONS  ".center(56) + "🎤")
    print("🎤" + "  Live Demo - Africa's Talking Integration  ".center(56) + "🎤")
    print("🎤" + " " * 56 + "🎤")
    print("🎤" * 60)
    
    print(f"\n📅 Presentation Date: {datetime.now().strftime('%B %d, %Y')}")
    print(f"⏰ Demo Time: {datetime.now().strftime('%I:%M %p')}")
    print(f"🌍 Platform: Africa's Talking SMS Gateway")
    print(f"🎯 Focus: Community Waste Management Education")

def check_demo_ready():
    """Quick check if demo is ready"""
    print(f"\n{'='*50}")
    print("🔍 PRE-DEMO SYSTEM CHECK")
    print(f"{'='*50}")
    
    checks = []
    
    # Check Africa's Talking
    try:
        from africas_talking_integration import africas_talking_service
        if africas_talking_service.sms:
            checks.append("✅ Africa's Talking: Connected")
        else:
            checks.append("❌ Africa's Talking: Not configured")
    except Exception as e:
        checks.append(f"❌ Africa's Talking: Error - {e}")
    
    # Check database users
    try:
        from accounts.models import CustomUser
        users = CustomUser.objects.filter(phone_number__isnull=False).exclude(phone_number='')
        if users.count() > 0:
            checks.append(f"✅ Demo Users: {users.count()} users with phone numbers")
        else:
            checks.append("⚠️  Demo Users: No users with phones (will use hardcoded)")
    except Exception as e:
        checks.append(f"❌ Database: Error - {e}")
    
    # Check existing notification system
    try:
        from community.notifications import notification_service
        checks.append("✅ Notification System: Available")
    except Exception as e:
        checks.append(f"⚠️  Notification System: {e}")
    
    # Display results
    for check in checks:
        print(f"   {check}")
    
    # Overall status
    if all("✅" in check for check in checks):
        print(f"\n🎉 SYSTEM STATUS: READY FOR DEMO!")
        return True
    elif any("❌" in check for check in checks):
        print(f"\n⚠️  SYSTEM STATUS: ISSUES DETECTED")
        print(f"   Demo may have limited functionality")
        return False
    else:
        print(f"\n✅ SYSTEM STATUS: READY (with minor warnings)")
        return True

def live_demo_scenario_1():
    """Scenario 1: Community Cleanup Campaign"""
    print(f"\n{'🧹'*50}")
    print("🧹 SCENARIO 1: COMMUNITY CLEANUP CAMPAIGN")
    print(f"{'🧹'*50}")
    
    print(f"\n📋 Scenario Description:")
    print(f"   • Saturday community cleanup event")
    print(f"   • Bulk SMS to all registered users")
    print(f"   • Encourage participation & provide details")
    
    # Demo phone numbers (use real ones for actual demo)
    demo_phones = [
        "+260970594105",  # Your number from .env
        "+260977123456",  # Demo number 1  
        "+260966789012",  # Demo number 2
    ]
    
    message = "🧹 EcoLearn Community Cleanup this Saturday 8AM! Join us at Community Center. Bring gloves & bags. Together we keep Zambia clean! 🇿🇲 Register: marabo.co.zm"
    
    print(f"\n📱 Target Recipients: {len(demo_phones)}")
    for i, phone in enumerate(demo_phones, 1):
        print(f"   {i}. {phone}")
    
    print(f"\n💬 Campaign Message:")
    print(f"   {message}")
    
    input(f"\n⏸️  Press ENTER to send LIVE SMS messages...")
    
    # Send actual SMS
    from africas_talking_integration import africas_talking_service
    
    print(f"\n📤 Sending SMS messages...")
    
    result = africas_talking_service.send_bulk_sms(demo_phones, message)
    
    if result['success']:
        print(f"\n✅ CAMPAIGN SENT SUCCESSFULLY!")
        print(f"   📊 Delivered: {result['total_sent']}/{len(demo_phones)}")
        
        for r in result['results']:
            if r['success']:
                cost = f" (Cost: {r.get('cost', 'N/A')})" if r.get('cost') else ""
                print(f"   ✅ {r['phone']}: Delivered{cost}")
            else:
                print(f"   ❌ {r['phone']}: Failed - {r.get('error', 'Unknown error')}")
    else:
        print(f"\n❌ CAMPAIGN FAILED: {result['error']}")
    
    print(f"\n💡 Key Benefits Demonstrated:")
    print(f"   • Instant community engagement")
    print(f"   • Cost-effective bulk messaging")
    print(f"   • Real-time delivery confirmation")

def live_demo_scenario_2():
    """Scenario 2: Individual Achievement Notification"""
    print(f"\n{'🏆'*50}")
    print("🏆 SCENARIO 2: INDIVIDUAL ACHIEVEMENT NOTIFICATION")
    print(f"{'🏆'*50}")
    
    print(f"\n📋 Scenario Description:")
    print(f"   • User completes waste sorting challenge")
    print(f"   • Automatic achievement notification")
    print(f"   • Points awarded & progress tracking")
    
    target_phone = "+260970594105"  # Your number
    
    message = "🏆 Congratulations! You earned 75 points for 'Plastic Bottle Collection Challenge'! Total: 425 points. You're now an Eco Champion! Keep making a difference! 🌟"
    
    print(f"\n📱 Target User: {target_phone}")
    print(f"\n💬 Achievement Message:")
    print(f"   {message}")
    
    input(f"\n⏸️  Press ENTER to send achievement notification...")
    
    # Send SMS
    from africas_talking_integration import africas_talking_service
    
    print(f"\n📤 Sending achievement notification...")
    
    result = africas_talking_service.send_sms(target_phone, message)
    
    if result['success']:
        print(f"\n✅ NOTIFICATION SENT!")
        print(f"   📱 Phone: {result['phone']}")
        print(f"   🆔 Message ID: {result['message_id']}")
        print(f"   💰 Cost: {result.get('cost', 'N/A')}")
    else:
        print(f"\n❌ NOTIFICATION FAILED: {result['error']}")
    
    print(f"\n💡 Key Benefits Demonstrated:")
    print(f"   • Instant user engagement")
    print(f"   • Automated reward system")
    print(f"   • Gamification through notifications")

def live_demo_scenario_3():
    """Scenario 3: Emergency Environmental Alert"""
    print(f"\n{'🚨'*50}")
    print("🚨 SCENARIO 3: EMERGENCY ENVIRONMENTAL ALERT")
    print(f"{'🚨'*50}")
    
    print(f"\n📋 Scenario Description:")
    print(f"   • Illegal dumping reported in community")
    print(f"   • Immediate alert to nearby residents")
    print(f"   • Call to action for reporting")
    
    demo_phones = ["+260970594105", "+260977123456"]
    
    message = "🚨 URGENT: Illegal dumping reported near Community Center! Help us keep our area clean. Report incidents at marabo.co.zm/report or call local authorities. Act now for our environment! 🌍"
    
    print(f"\n📱 Emergency Recipients: {len(demo_phones)}")
    for phone in demo_phones:
        print(f"   • {phone}")
    
    print(f"\n💬 Emergency Alert:")
    print(f"   {message}")
    
    input(f"\n⏸️  Press ENTER to send EMERGENCY ALERT...")
    
    # Send emergency SMS
    from africas_talking_integration import africas_talking_service
    
    print(f"\n🚨 Sending emergency alert...")
    
    result = africas_talking_service.send_bulk_sms(demo_phones, message)
    
    if result['success']:
        print(f"\n✅ EMERGENCY ALERT SENT!")
        print(f"   📊 Delivered: {result['total_sent']}/{len(demo_phones)}")
        
        for r in result['results']:
            if r['success']:
                print(f"   ✅ {r['phone']}: Alert delivered")
            else:
                print(f"   ❌ {r['phone']}: Failed - {r.get('error')}")
    else:
        print(f"\n❌ ALERT FAILED: {result['error']}")
    
    print(f"\n💡 Key Benefits Demonstrated:")
    print(f"   • Rapid emergency response")
    print(f"   • Community safety alerts")
    print(f"   • Environmental protection")

def demo_summary():
    """Show demo summary and next steps"""
    print(f"\n{'🎉'*60}")
    print("🎉" + " LIVE DEMO COMPLETE! ".center(58) + "🎉")
    print(f"{'🎉'*60}")
    
    print(f"\n📊 DEMO STATISTICS:")
    print(f"   🎯 Scenarios Demonstrated: 3")
    print(f"   📱 SMS Messages Sent: Live delivery")
    print(f"   ⚡ Platform: Africa's Talking")
    print(f"   🌍 Use Case: Waste Management Education")
    print(f"   💰 Cost: ~$0.01 per SMS in Zambia")
    
    print(f"\n💡 KEY FEATURES SHOWCASED:")
    print(f"   ✅ Bulk community campaigns")
    print(f"   ✅ Individual user notifications")
    print(f"   ✅ Emergency alert system")
    print(f"   ✅ Real-time delivery tracking")
    print(f"   ✅ Cost-effective African SMS")
    print(f"   ✅ Django integration")
    
    print(f"\n🚀 PRODUCTION DEPLOYMENT BENEFITS:")
    print(f"   💰 75% cost reduction vs international providers")
    print(f"   📶 Better delivery rates in Zambia")
    print(f"   ⚡ Instant community engagement")
    print(f"   🎯 Targeted environmental education")
    print(f"   📈 Scalable to thousands of users")
    
    print(f"\n🔮 NEXT STEPS:")
    print(f"   1. Deploy to production with live API key")
    print(f"   2. Configure branded sender ID")
    print(f"   3. Set up automated campaign scheduling")
    print(f"   4. Add WhatsApp Business integration")
    print(f"   5. Implement delivery analytics dashboard")
    
    print(f"\n{'='*60}")
    print("Thank you for watching the EcoLearn SMS Demo! 🙏")
    print("Questions about implementation or deployment?")
    print(f"{'='*60}")

def main():
    """Main presentation flow"""
    presentation_banner()
    
    # Pre-demo check
    if not check_demo_ready():
        print(f"\n⚠️  Some issues detected. Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            print("Demo cancelled. Fix issues and try again.")
            return
    
    print(f"\n🎤 READY FOR LIVE DEMO!")
    input("Press ENTER when ready to start presentation...")
    
    # Run demo scenarios
    try:
        live_demo_scenario_1()
        
        print(f"\n{'⏸️ '*20}")
        input("Press ENTER to continue to individual notifications...")
        
        live_demo_scenario_2()
        
        print(f"\n{'⏸️ '*20}")
        input("Press ENTER to continue to emergency alerts...")
        
        live_demo_scenario_3()
        
        # Demo summary
        demo_summary()
        
    except KeyboardInterrupt:
        print(f"\n\n⏸️  Demo paused by presenter.")
        print("Resume anytime by running this script again.")
    
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Check your setup and try again.")

if __name__ == "__main__":
    main()