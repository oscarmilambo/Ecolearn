"""
Django management command to test PRO notifications
Run: python manage.py test_notifications
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from community.notifications import notification_service
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Test PRO WhatsApp/SMS notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number to test (e.g., +260971234567)',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("PRO NOTIFICATION TEST"))
        self.stdout.write("=" * 60)

        # Get test user
        if options['phone']:
            phone = options['phone']
            test_user = CustomUser.objects.filter(phone_number=phone).first()
            if not test_user:
                self.stdout.write(self.style.ERROR(f"\n❌ No user found with phone: {phone}"))
                return
        else:
            test_user = CustomUser.objects.filter(phone_number__isnull=False).first()
            if not test_user:
                self.stdout.write(self.style.ERROR("\n❌ No user with phone number found!"))
                self.stdout.write("Add --phone +260971234567 to specify a number")
                return

        self.stdout.write(f"\n✅ Test User: {test_user.username}")
        self.stdout.write(f"📱 Phone: {test_user.phone_number}")

        user_name = test_user.get_full_name() or test_user.username
        challenge_name = "Clean Kalingalinga Challenge"

        # Test 1: Join Challenge
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.WARNING("TEST 1: JOIN CHALLENGE"))
        self.stdout.write("=" * 60)

        msg = f"🎉 {user_name}, welcome to {challenge_name}! Top 3 win airtime. Submit proof now!"
        self.stdout.write(f"\n📱 Message: {msg}")

        result = notification_service.send_sms(str(test_user.phone_number), msg)
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"✅ SMS sent! SID: {result.get('message_sid')}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ SMS failed: {result.get('error')}"))

        result = notification_service.send_whatsapp(str(test_user.phone_number), msg)
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"✅ WhatsApp sent! SID: {result.get('message_sid')}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ WhatsApp failed: {result.get('error')}"))

        # Test 2: Proof Approved
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.WARNING("TEST 2: PROOF APPROVED"))
        self.stdout.write("=" * 60)

        msg = f"✅ APPROVED! You earned 50 points (5 bags). You are now #3 in {challenge_name}! Keep cleaning Zambia!"
        self.stdout.write(f"\n📱 Message: {msg}")

        result = notification_service.send_sms(str(test_user.phone_number), msg)
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"✅ SMS sent! SID: {result.get('message_sid')}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ SMS failed: {result.get('error')}"))

        result = notification_service.send_whatsapp(str(test_user.phone_number), msg)
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"✅ WhatsApp sent! SID: {result.get('message_sid')}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ WhatsApp failed: {result.get('error')}"))

        # Test 3: New Dump (Admin Alert)
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.WARNING("TEST 3: NEW ILLEGAL DUMP"))
        self.stdout.write("=" * 60)

        msg = "🚨 NEW ILLEGAL DUMP in Kalingalinga Market! 3 photos attached. Act now!"
        self.stdout.write(f"\n📱 Message: {msg}")

        result = notification_service.send_sms(str(test_user.phone_number), msg)
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"✅ SMS sent! SID: {result.get('message_sid')}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ SMS failed: {result.get('error')}"))

        result = notification_service.send_whatsapp(str(test_user.phone_number), msg)
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"✅ WhatsApp sent! SID: {result.get('message_sid')}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ WhatsApp failed: {result.get('error')}"))

        # Test 4: Lesson Completed
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.WARNING("TEST 4: LESSON COMPLETED"))
        self.stdout.write("=" * 60)

        msg = f"✅ Well done {user_name}! You finished 'Waste Management Basics'. +20 points added!"
        self.stdout.write(f"\n📱 Message: {msg}")

        result = notification_service.send_sms(str(test_user.phone_number), msg)
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"✅ SMS sent! SID: {result.get('message_sid')}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ SMS failed: {result.get('error')}"))

        result = notification_service.send_whatsapp(str(test_user.phone_number), msg)
        if result.get('success'):
            self.stdout.write(self.style.SUCCESS(f"✅ WhatsApp sent! SID: {result.get('message_sid')}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ WhatsApp failed: {result.get('error')}"))

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("✅ ALL TESTS COMPLETED!"))
        self.stdout.write("=" * 60)
        self.stdout.write("\nCheck your phone for 8 messages (4 SMS + 4 WhatsApp)")
        self.stdout.write("\n💡 If messages didn't arrive:")
        self.stdout.write("   1. Check Twilio credentials: python check_credentials.py")
        self.stdout.write("   2. Verify phone number format: +260971234567")
        self.stdout.write("   3. Check Twilio console: https://console.twilio.com")
        self.stdout.write("   4. Verify account balance")
