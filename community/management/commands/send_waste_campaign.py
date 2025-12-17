"""
Django Management Command: Send Waste Management Campaigns
Usage: python manage.py send_waste_campaign --type cleanup --location "Community Center"
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from community.notifications import send_waste_management_campaign
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send waste management campaigns via SMS using Africa\'s Talking'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            required=True,
            choices=['cleanup', 'recycling', 'education', 'emergency', 'general', 'reminder'],
            help='Type of campaign to send'
        )
        
        parser.add_argument(
            '--location',
            type=str,
            help='Location for the campaign (optional)'
        )
        
        parser.add_argument(
            '--message',
            type=str,
            help='Custom message (overrides default campaign message)'
        )
        
        parser.add_argument(
            '--users',
            type=str,
            help='Comma-separated list of usernames to target (default: all active users with phones)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending'
        )

    def handle(self, *args, **options):
        campaign_type = options['type']
        location = options.get('location')
        custom_message = options.get('message')
        target_usernames = options.get('users')
        dry_run = options['dry_run']
        
        User = get_user_model()
        
        # Get target users
        if target_usernames:
            usernames = [u.strip() for u in target_usernames.split(',')]
            target_users = User.objects.filter(
                username__in=usernames,
                is_active=True,
                phone_number__isnull=False
            ).exclude(phone_number='')
            
            if not target_users.exists():
                raise CommandError(f"No active users found with usernames: {usernames}")
                
        else:
            target_users = User.objects.filter(
                is_active=True,
                phone_number__isnull=False
            ).exclude(phone_number='')
        
        if not target_users.exists():
            raise CommandError("No users with phone numbers found")
        
        # Show campaign details
        self.stdout.write(self.style.SUCCESS(f"\n📢 WASTE MANAGEMENT CAMPAIGN"))
        self.stdout.write(f"Campaign Type: {campaign_type}")
        self.stdout.write(f"Target Users: {target_users.count()}")
        
        if location:
            self.stdout.write(f"Location: {location}")
        
        # Show target users
        self.stdout.write(f"\n📱 Target Recipients:")
        for user in target_users[:10]:  # Show first 10
            self.stdout.write(f"   - {user.username}: {user.phone_number}")
        
        if target_users.count() > 10:
            self.stdout.write(f"   ... and {target_users.count() - 10} more users")
        
        # Generate message preview
        if custom_message:
            message_preview = custom_message
        else:
            # Use default messages from notification service
            messages = {
                'cleanup': f"🧹 EcoLearn Community Cleanup this Saturday 8AM! Location: {location or 'Community Center'}. Bring gloves & bags. Together we keep Zambia clean! 🇿🇲 Info: marabo.co.zm",
                'recycling': "♻️ Did you know plastic bottles take 450 years to decompose? Join our recycling program! Learn proper waste sorting & earn points. Start: marabo.co.zm/learn",
                'education': "📚 New Waste Management Course! Learn the 3 R's: Reduce, Reuse, Recycle. Complete modules for certificates & points. Enroll: marabo.co.zm/courses",
                'emergency': f"🚨 URGENT: Illegal dumping reported{f' near {location}' if location else ''}! Help keep communities clean. Report: marabo.co.zm/report or call authorities. Act now!",
                'general': "🌍 EcoLearn: Join our mission for cleaner communities! Learn waste management, join challenges, earn rewards. Start today: marabo.co.zm",
                'reminder': f"⏰ Reminder: Community event{f' at {location}' if location else ''} starts soon! Don't miss out on making a difference. Details: marabo.co.zm"
            }
            message_preview = messages.get(campaign_type, "Campaign message")
        
        self.stdout.write(f"\n💬 Message Preview:")
        self.stdout.write(f"   {message_preview}")
        self.stdout.write(f"   (Length: {len(message_preview)} characters)")
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f"\n🧪 DRY RUN - No messages will be sent"))
            self.stdout.write(f"Campaign would target {target_users.count()} users")
            return
        
        # Confirm before sending
        self.stdout.write(f"\n⚠️  This will send SMS messages to {target_users.count()} users.")
        confirm = input("Continue? (y/N): ")
        
        if confirm.lower() != 'y':
            self.stdout.write(self.style.WARNING("Campaign cancelled"))
            return
        
        # Send campaign
        self.stdout.write(f"\n📤 Sending campaign...")
        
        try:
            result = send_waste_management_campaign(
                campaign_type=campaign_type,
                target_users=target_users,
                custom_message=custom_message,
                location=location
            )
            
            # Display results
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f"\n✅ CAMPAIGN SENT SUCCESSFULLY!"))
                self.stdout.write(f"📊 SMS Results:")
                self.stdout.write(f"   ✅ Delivered: {result['sms_sent']}")
                self.stdout.write(f"   ❌ Failed: {result['sms_failed']}")
                self.stdout.write(f"   📱 In-app notifications: {result['in_app_created']}")
                
                if result.get('african_numbers'):
                    self.stdout.write(f"   🌍 African numbers: {result['african_numbers']} (via Africa's Talking)")
                
                if result.get('international_numbers'):
                    self.stdout.write(f"   🌐 International numbers: {result['international_numbers']} (via Twilio)")
                
                # Show detailed results for failed messages
                failed_results = [r for r in result.get('detailed_results', []) if not r['success']]
                if failed_results:
                    self.stdout.write(f"\n❌ Failed Deliveries:")
                    for failure in failed_results[:5]:  # Show first 5 failures
                        self.stdout.write(f"   - {failure['phone']}: {failure.get('error', 'Unknown error')}")
                    
                    if len(failed_results) > 5:
                        self.stdout.write(f"   ... and {len(failed_results) - 5} more failures")
            
            else:
                self.stdout.write(self.style.ERROR(f"\n❌ CAMPAIGN FAILED"))
                self.stdout.write(f"Error: {result.get('error', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"Campaign command failed: {str(e)}")
            raise CommandError(f"Campaign failed: {str(e)}")
        
        self.stdout.write(f"\n🎉 Campaign command completed!")