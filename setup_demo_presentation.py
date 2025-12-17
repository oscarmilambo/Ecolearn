#!/usr/bin/env python
"""
QUICK SETUP: SMS Demo for Presentation
Sets up Africa's Talking and runs live demo

BEFORE RUNNING:
1. Get Africa's Talking API key from https://africastalking.com/
2. Update .env file with your credentials
3. Run this script during presentation
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

def check_setup():
    """Check if everything is configured correctly"""
    print("🔍 CHECKING SETUP...")
    print("=" * 40)
    
    # Check .env configuration
    from decouple import config
    
    at_username = config('AFRICAS_TALKING_USERNAME', default='')
    at_api_key = config('AFRICAS_TALKING_API_KEY', default='')
    
    print(f"✅ Africa's Talking Username: {at_username}")
    print(f"✅ Africa's Talking API Key: {'*' * len(at_api_key[:10])}..." if at_api_key else "❌ Not configured")
    
    if not at_api_key or at_api_key == 'your_africas_talking_api_key_here':
        print("\n❌ SETUP REQUIRED:")
        print("1. Go to https://africastalking.com/")
        print("2. Sign up and get your API key")
        print("3. Update .env file:")
        print("   AFRICAS_TALKING_USERNAME=your_username")
        print("   AFRICAS_TALKING_API_KEY=your_api_key")
        print("4. Run this script again")
        return False
    
    # Check database users
    from accounts.models import CustomUser
    users_with_phones = CustomUser.objects.filter(phone_number__isnull=False).exclude(phone_number='')
    
    print(f"\n📱 Users with phone numbers: {users_with_phones.count()}")
    if users_with_phones.count() == 0:
        print("⚠️  No users with phone numbers found")
        print("   Demo will use hardcoded numbers")
    else:
        for user in users_with_phones[:3]:
            print(f"   - {user.username}: {user.phone_number}")
    
    # Test Africa's Talking connection
    print(f"\n🔌 Testing Africa's Talking connection...")
    try:
        from africas_talking_integration import africas_talking_service
        if africas_talking_service.sms:
            print("✅ Africa's Talking service initialized")
            return True
        else:
            print("❌ Africa's Talking service not initialized")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_demo_users():
    """Create demo users if none exist"""
    from accounts.models import CustomUser
    
    demo_data = [
        {'username': 'demo_user1', 'phone': '+260970594105', 'email': 'demo1@ecolearn.zm'},
        {'username': 'demo_user2', 'phone': '+260977123456', 'email': 'demo2@ecolearn.zm'},
        {'username': 'demo_user3', 'phone': '+260966789012', 'email': 'demo3@ecolearn.zm'},
    ]
    
    created = 0
    for data in demo_data:
        user, was_created = CustomUser.objects.get_or_create(
            username=data['username'],
            defaults={
                'email': data['email'],
                'phone_number': data['phone'],
                'first_name': 'Demo',
                'last_name': 'User',
                'is_active': True
            }
        )
        if was_created:
            user.set_password('demo123')
            user.save()
            created += 1
    
    if created > 0:
        print(f"✅ Created {created} demo users")
    else:
        print("✅ Demo users already exist")

def run_presentation_demo():
    """Run the full presentation demo"""
    print("\n🎤" * 25)
    print("🎤 LIVE PRESENTATION: ECOLEARN SMS NOTIFICATIONS")
    print("🎤 Platform: Africa's Talking SMS Gateway")
    print("🎤 Focus: Community Waste Management")
    print("🎤" * 25)
    
    print(f"\n📅 Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Import demo functions
    from demo_sms_presentation import presentation_demo
    
    # Run the demo
    presentation_demo()

def quick_sms_test():
    """Send a quick test SMS"""
    print("\n🧪 QUICK SMS TEST")
    print("=" * 30)
    
    phone = input("Enter phone number (e.g., +260970594105): ").strip()
    if not phone:
        phone = "+260970594105"  # Default to your number
    
    from africas_talking_integration import africas_talking_service
    
    test_message = f"🧪 EcoLearn SMS Test ({datetime.now().strftime('%H:%M')}): Your waste management learning platform is ready! System working perfectly. ✅"
    
    print(f"\nSending test SMS to: {phone}")
    print(f"Message: {test_message}")
    
    result = africas_talking_service.send_sms(phone, test_message)
    
    if result['success']:
        print(f"\n✅ SUCCESS!")
        print(f"   Message ID: {result['message_id']}")
        print(f"   Cost: {result.get('cost', 'N/A')}")
        print(f"   Phone: {result['phone']}")
        print(f"\n📱 Check your phone for the message!")
    else:
        print(f"\n❌ FAILED: {result['error']}")
        print(f"\nTroubleshooting:")
        print(f"1. Check your Africa's Talking API key")
        print(f"2. Ensure you have credit in your account")
        print(f"3. Verify phone number format: +260XXXXXXXXX")

def main():
    """Main menu for demo setup"""
    print("🌍 ECOLEARN SMS DEMO SETUP")
    print("=" * 40)
    
    # Check setup first
    if not check_setup():
        return
    
    print("\n✅ Setup complete! Choose demo option:")
    print("1. 🎤 Full Presentation Demo (recommended)")
    print("2. 🧪 Quick SMS Test")
    print("3. 👥 Create Demo Users")
    print("4. 🔍 Check Setup Again")
    print("5. 📖 View Setup Guide")
    print("6. ❌ Exit")
    
    choice = input("\nEnter choice (1-6): ").strip()
    
    if choice == "1":
        print("\n🚀 Starting presentation demo...")
        input("Press ENTER when ready to begin live demo...")
        run_presentation_demo()
    
    elif choice == "2":
        quick_sms_test()
    
    elif choice == "3":
        create_demo_users()
        print("Demo users created! Run option 1 for full demo.")
    
    elif choice == "4":
        check_setup()
    
    elif choice == "5":
        print("\n📖 SETUP GUIDE:")
        print("1. Visit: https://africastalking.com/")
        print("2. Create account and get API key")
        print("3. Update .env file with credentials")
        print("4. Add credit to account ($1 = ~100 SMS)")
        print("5. Run this script again")
        print("\nFor detailed guide, see: AFRICAS_TALKING_SETUP_GUIDE.md")
    
    elif choice == "6":
        print("Goodbye! 👋")
    
    else:
        print("Invalid choice. Try again.")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your setup and try again.")