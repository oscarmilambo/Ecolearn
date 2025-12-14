# community/management/commands/send_campaign_reminders.py
"""
Management command to send campaign reminders (FR09)
Run this command daily via cron job to send 3-day and 1-day reminders
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from community.models import CommunityCampaign, CampaignParticipant


class Command(BaseCommand):
    help = 'Send campaign reminders to registered participants (FR09)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force send reminders even if already sent',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        now = timezone.now()
        
        # Find campaigns starting in 3 days
        three_days_from_now = now + timedelta(days=3)
        campaigns_3days = CommunityCampaign.objects.filter(
            is_active=True,
            is_published=True,
            start_date__date=three_days_from_now.date()
        )
        
        # Find campaigns starting in 1 day
        one_day_from_now = now + timedelta(days=1)
        campaigns_1day = CommunityCampaign.objects.filter(
            is_active=True,
            is_published=True,
            start_date__date=one_day_from_now.date()
        )
        
        total_sent = 0
        
        # Send 3-day reminders
        self.stdout.write(f"\n🔍 Checking 3-day reminders for {campaigns_3days.count()} campaigns...")
        for campaign in campaigns_3days:
            participants = CampaignParticipant.objects.filter(
                campaign=campaign,
                reminder_3days_sent=False if not force else True
            )
            
            self.stdout.write(f"\n📅 Campaign: {campaign.title}")
            self.stdout.write(f"   Start: {campaign.start_date}")
            self.stdout.write(f"   Participants needing 3-day reminder: {participants.count()}")
            
            if dry_run:
                self.stdout.write(f"   [DRY RUN] Would send 3-day reminders to {participants.count()} participants")
            else:
                sent_count = 0
                for participant in participants:
                    try:
                        participant.send_reminder(3)
                        sent_count += 1
                        total_sent += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"   ❌ Failed to send reminder to {participant.user.username}: {e}")
                        )
                
                if sent_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ Sent 3-day reminders to {sent_count} participants")
                    )
        
        # Send 1-day reminders
        self.stdout.write(f"\n🔍 Checking 1-day reminders for {campaigns_1day.count()} campaigns...")
        for campaign in campaigns_1day:
            participants = CampaignParticipant.objects.filter(
                campaign=campaign,
                reminder_1day_sent=False if not force else True
            )
            
            self.stdout.write(f"\n📅 Campaign: {campaign.title}")
            self.stdout.write(f"   Start: {campaign.start_date}")
            self.stdout.write(f"   Participants needing 1-day reminder: {participants.count()}")
            
            if dry_run:
                self.stdout.write(f"   [DRY RUN] Would send 1-day reminders to {participants.count()} participants")
            else:
                sent_count = 0
                for participant in participants:
                    try:
                        participant.send_reminder(1)
                        sent_count += 1
                        total_sent += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"   ❌ Failed to send reminder to {participant.user.username}: {e}")
                        )
                
                if sent_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f"   ✅ Sent 1-day reminders to {sent_count} participants")
                    )
        
        # Summary
        self.stdout.write(f"\n" + "="*50)
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN COMPLETE - No reminders actually sent"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ REMINDERS SENT: {total_sent} total"))
        
        self.stdout.write(f"📊 3-day campaigns: {campaigns_3days.count()}")
        self.stdout.write(f"📊 1-day campaigns: {campaigns_1day.count()}")
        self.stdout.write("="*50)