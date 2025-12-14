# community/management/commands/create_recurring_campaigns.py
"""
Management command to create next occurrences of recurring campaigns (FR08)
Run this command daily via cron job to automatically create new campaign instances
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from community.models import CommunityCampaign


class Command(BaseCommand):
    help = 'Create next occurrences of recurring campaigns (FR08)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=30,
            help='Create campaigns this many days ahead (default: 30)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_ahead = options['days_ahead']
        
        now = timezone.now()
        cutoff_date = now + timedelta(days=days_ahead)
        
        # Find recurring campaigns that need next occurrence created
        recurring_campaigns = CommunityCampaign.objects.filter(
            is_active=True,
            recurrence__in=['monthly', 'quarterly', 'yearly'],
            end_date__lt=now  # Past campaigns that might need next occurrence
        ).exclude(
            recurrence='one_time'
        )
        
        self.stdout.write(f"\n🔍 Checking {recurring_campaigns.count()} recurring campaigns...")
        self.stdout.write(f"📅 Creating campaigns up to {cutoff_date.strftime('%B %d, %Y')}")
        
        created_count = 0
        
        for campaign in recurring_campaigns:
            # Check if next occurrence already exists
            next_start = self._calculate_next_start(campaign)
            
            if not next_start or next_start > cutoff_date:
                continue
            
            # Check if campaign with same title and start date already exists
            existing = CommunityCampaign.objects.filter(
                title=campaign.title,
                start_date__date=next_start.date(),
                is_active=True
            ).exists()
            
            if existing:
                self.stdout.write(f"   ⏭️  {campaign.title} - Next occurrence already exists")
                continue
            
            self.stdout.write(f"\n📅 {campaign.title}")
            self.stdout.write(f"   Original: {campaign.start_date.strftime('%B %d, %Y')}")
            self.stdout.write(f"   Next: {next_start.strftime('%B %d, %Y')}")
            self.stdout.write(f"   Recurrence: {campaign.get_recurrence_display()}")
            
            if dry_run:
                self.stdout.write(f"   [DRY RUN] Would create next occurrence")
            else:
                try:
                    new_campaign = campaign.create_next_occurrence()
                    if new_campaign:
                        created_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(f"   ✅ Created next occurrence (ID: {new_campaign.id})")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"   ⚠️  Failed to create next occurrence")
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"   ❌ Error creating next occurrence: {e}")
                    )
        
        # Summary
        self.stdout.write(f"\n" + "="*50)
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN COMPLETE - No campaigns actually created"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ CAMPAIGNS CREATED: {created_count} total"))
        
        self.stdout.write(f"📊 Recurring campaigns checked: {recurring_campaigns.count()}")
        self.stdout.write("="*50)

    def _calculate_next_start(self, campaign):
        """Calculate when the next occurrence should start"""
        from dateutil.relativedelta import relativedelta
        
        if campaign.recurrence == 'monthly':
            return campaign.start_date + relativedelta(months=1)
        elif campaign.recurrence == 'quarterly':
            return campaign.start_date + relativedelta(months=3)
        elif campaign.recurrence == 'yearly':
            return campaign.start_date + relativedelta(years=1)
        else:
            return None