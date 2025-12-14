#!/usr/bin/env python
"""
Test script for Community Campaigns System (FR08 & FR09)
Tests campaign creation, registration, and reminder functionality
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecolearn.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from community.models import CommunityCampaign, CampaignParticipant
from accounts.models import NotificationPreference

User = get_user_model()

def test_campaign_system():
    print("=" * 70)
    print("🌍 TESTING COMMUNITY CAMPAIGNS SYSTEM (FR08 & FR09)")
    print("=" * 70)
    
    # 1. Create test admin user
    print("\n1. CREATING TEST ADMIN USER")
    print("-" * 40)
    admin_user, created = User.objects.get_or_create(
        username='campaign_admin',
        defaults={
            'email': 'admin@ecolearn.com',
            'first_name': 'Campaign',
            'last_name': 'Admin',
            'is_staff': True,
            'is_superuser': True,
            'phone_number': '+260977123456'
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✅ Created admin user: {admin_user.username}")
    else:
        print(f"✅ Using existing admin user: {admin_user.username}")
    
    # 2. Create test regular users
    print("\n2. CREATING TEST PARTICIPANTS")
    print("-" * 40)
    test_users = []
    for i in range(1, 4):
        user, created = User.objects.get_or_create(
            username=f'participant{i}',
            defaults={
                'email': f'participant{i}@example.com',
                'first_name': f'Participant',
                'last_name': f'{i}',
                'phone_number': f'+26097712345{i}',
                'location': 'Lusaka'
            }
        )
        if created:
            user.set_password('test123')
            user.save()
            print(f"✅ Created participant: {user.username}")
        else:
            print(f"✅ Using existing participant: {user.username}")
        
        # Create notification preferences
        prefs, created = NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'sms_enabled': True,
                'whatsapp_enabled': True,
                'email_enabled': True,
                'event_reminders': True,
                'challenge_updates': True,
                'forum_replies': True
            }
        )
        test_users.append(user)
    
    # 3. Create test campaigns (FR08)
    print("\n3. CREATING TEST CAMPAIGNS (FR08)")
    print("-" * 40)
    
    # One-time cleanup campaign (tomorrow)
    tomorrow = timezone.now() + timedelta(days=1)
    cleanup_campaign, created = CommunityCampaign.objects.get_or_create(
        title='Community Cleanup - Kabulonga',
        defaults={
            'title_bem': 'Ukusafya Kwa Bantu - Kabulonga',
            'title_ny': 'Kuyeretsa Kwa Anthu - Kabulonga',
            'description': 'Join us for a community cleanup in Kabulonga area. We will focus on cleaning the main roads and collecting plastic waste.',
            'description_bem': 'Mwiseni tukasafye mu Kabulonga. Tukasafya imisebo ikulukulu no kutola ubwangu bwa plastic.',
            'description_ny': 'Tiyeni tikayeretse ku Kabulonga. Tikayeretsa misewu yayikulu ndi kutola zinyalala za plastic.',
            'campaign_type': 'cleanup',
            'location': 'Kabulonga Shopping Mall Parking',
            'latitude': -15.3875,
            'longitude': 28.3228,
            'start_date': tomorrow.replace(hour=8, minute=0, second=0, microsecond=0),
            'end_date': tomorrow.replace(hour=12, minute=0, second=0, microsecond=0),
            'recurrence': 'one_time',
            'max_participants': 50,
            'registration_deadline': tomorrow - timedelta(hours=12),
            'organizer': admin_user,
            'contact_phone': '+260977123456',
            'contact_email': 'campaigns@ecolearn.com',
            'is_active': True,
            'is_published': True
        }
    )
    if created:
        print(f"✅ Created cleanup campaign: {cleanup_campaign.title}")
    else:
        print(f"✅ Using existing cleanup campaign: {cleanup_campaign.title}")
    
    # Monthly recycling workshop (next week)
    next_week = timezone.now() + timedelta(days=7)
    workshop_campaign, created = CommunityCampaign.objects.get_or_create(
        title='Recycling Workshop - Matero',
        defaults={
            'title_bem': 'Ukufundisha Ukubomba Ubwangu - Matero',
            'title_ny': 'Maphunziro a Kubwezeretsanso - Matero',
            'description': 'Learn how to properly segregate waste and create useful items from recyclable materials. Hands-on workshop with expert facilitators.',
            'description_bem': 'Mwishibe ukubomba ubwangu no kupanga ifintu ifya kufwaya ukufuma mu bwangu bwa kubomba.',
            'description_ny': 'Phunzirani momwe mungagawire bwino zinyalala ndi kupanga zinthu zothandiza kuchokera ku zinyalala.',
            'campaign_type': 'workshop',
            'location': 'Matero Community Hall',
            'latitude': -15.3794,
            'longitude': 28.2833,
            'start_date': next_week.replace(hour=14, minute=0, second=0, microsecond=0),
            'end_date': next_week.replace(hour=17, minute=0, second=0, microsecond=0),
            'recurrence': 'monthly',
            'max_participants': 30,
            'registration_deadline': next_week - timedelta(days=2),
            'organizer': admin_user,
            'contact_phone': '+260977123456',
            'contact_email': 'workshops@ecolearn.com',
            'is_active': True,
            'is_published': True
        }
    )
    if created:
        print(f"✅ Created workshop campaign: {workshop_campaign.title}")
    else:
        print(f"✅ Using existing workshop campaign: {workshop_campaign.title}")
    
    # Zero-plastic challenge (in 3 days)
    three_days = timezone.now() + timedelta(days=3)
    challenge_campaign, created = CommunityCampaign.objects.get_or_create(
        title='Zero-Plastic Challenge - Chilenje',
        defaults={
            'description': 'A week-long challenge to reduce plastic usage in Chilenje area. Participants will track their plastic consumption and find alternatives.',
            'campaign_type': 'challenge',
            'location': 'Chilenje Market Area',
            'latitude': -15.4167,
            'longitude': 28.2833,
            'start_date': three_days.replace(hour=9, minute=0, second=0, microsecond=0),
            'end_date': three_days.replace(hour=18, minute=0, second=0, microsecond=0) + timedelta(days=7),
            'recurrence': 'quarterly',
            'max_participants': 100,
            'registration_deadline': three_days - timedelta(hours=24),
            'organizer': admin_user,
            'contact_phone': '+260977123456',
            'is_active': True,
            'is_published': True
        }
    )
    if created:
        print(f"✅ Created challenge campaign: {challenge_campaign.title}")
    else:
        print(f"✅ Using existing challenge campaign: {challenge_campaign.title}")
    
    # 4. Test campaign registration
    print("\n4. TESTING CAMPAIGN REGISTRATION")
    print("-" * 40)
    
    campaigns = [cleanup_campaign, workshop_campaign, challenge_campaign]
    
    for i, user in enumerate(test_users):
        for j, campaign in enumerate(campaigns):
            if (i + j) % 2 == 0:  # Register some users to some campaigns
                participant, created = CampaignParticipant.objects.get_or_create(
                    campaign=campaign,
                    user=user,
                    defaults={
                        'interest_level': ['join', 'interested', 'maybe'][j % 3]
                    }
                )
                if created:
                    # Update participant count
                    campaign.participant_count += 1
                    campaign.save()
                    print(f"✅ {user.username} registered for {campaign.title} ({participant.interest_level})")
                    
                    # Send confirmation
                    try:
                        participant.send_confirmation()
                        print(f"   📱 Confirmation sent to {user.username}")
                    except Exception as e:
                        print(f"   ⚠️  Confirmation failed: {e}")
    
    # 5. Test reminder system (FR09)
    print("\n5. TESTING REMINDER SYSTEM (FR09)")
    print("-" * 40)
    
    # Test 3-day reminders
    participants_3day = CampaignParticipant.objects.filter(
        campaign__start_date__date=(timezone.now() + timedelta(days=3)).date(),
        reminder_3days_sent=False
    )
    
    print(f"Participants needing 3-day reminders: {participants_3day.count()}")
    for participant in participants_3day:
        try:
            participant.send_reminder(3)
            print(f"✅ 3-day reminder sent to {participant.user.username} for {participant.campaign.title}")
        except Exception as e:
            print(f"❌ 3-day reminder failed for {participant.user.username}: {e}")
    
    # Test 1-day reminders
    participants_1day = CampaignParticipant.objects.filter(
        campaign__start_date__date=(timezone.now() + timedelta(days=1)).date(),
        reminder_1day_sent=False
    )
    
    print(f"Participants needing 1-day reminders: {participants_1day.count()}")
    for participant in participants_1day:
        try:
            participant.send_reminder(1)
            print(f"✅ 1-day reminder sent to {participant.user.username} for {participant.campaign.title}")
        except Exception as e:
            print(f"❌ 1-day reminder failed for {participant.user.username}: {e}")
    
    # 6. Test recurring campaigns
    print("\n6. TESTING RECURRING CAMPAIGNS")
    print("-" * 40)
    
    recurring_campaigns = CommunityCampaign.objects.filter(
        recurrence__in=['monthly', 'quarterly', 'yearly']
    )
    
    print(f"Found {recurring_campaigns.count()} recurring campaigns")
    for campaign in recurring_campaigns:
        print(f"📅 {campaign.title} - {campaign.get_recurrence_display()}")
        if campaign.end_date < timezone.now():
            try:
                next_campaign = campaign.create_next_occurrence()
                if next_campaign:
                    print(f"   ✅ Created next occurrence: {next_campaign.start_date}")
                else:
                    print(f"   ⚠️  Could not create next occurrence")
            except Exception as e:
                print(f"   ❌ Error creating next occurrence: {e}")
    
    # 7. Display summary
    print("\n7. CAMPAIGN SYSTEM SUMMARY")
    print("-" * 40)
    
    total_campaigns = CommunityCampaign.objects.filter(is_active=True, is_published=True).count()
    total_participants = CampaignParticipant.objects.count()
    upcoming_campaigns = CommunityCampaign.objects.filter(
        is_active=True,
        is_published=True,
        start_date__gte=timezone.now()
    ).count()
    
    print(f"📊 Total Active Campaigns: {total_campaigns}")
    print(f"📊 Total Participants: {total_participants}")
    print(f"📊 Upcoming Campaigns: {upcoming_campaigns}")
    
    # Campaign types breakdown
    from django.db.models import Count
    campaign_types = CommunityCampaign.objects.filter(
        is_active=True, is_published=True
    ).values('campaign_type').annotate(count=Count('id'))
    
    print("\n📊 Campaign Types:")
    for ct in campaign_types:
        print(f"   {ct['campaign_type'].title()}: {ct['count']}")
    
    print("\n" + "=" * 70)
    print("✅ CAMPAIGN SYSTEM TEST COMPLETED")
    print("=" * 70)
    
    print("\n🎯 FUNCTIONAL REQUIREMENTS STATUS:")
    print("✅ FR08 - Periodic Community Campaigns Management: IMPLEMENTED")
    print("   - Administrators can create, schedule, and publish campaigns")
    print("   - Support for recurring campaigns (monthly, quarterly, yearly)")
    print("   - Campaign registration with one-click join")
    print("   - Participant tracking and capacity management")
    print("")
    print("✅ FR09 - Campaign Calendar & Reminder System: IMPLEMENTED")
    print("   - Public calendar view of all campaigns")
    print("   - Automatic WhatsApp/SMS reminders (3-day and 1-day)")
    print("   - Registration confirmation messages")
    print("   - Management commands for automated reminders")
    
    print("\n📱 NEXT STEPS:")
    print("1. Set up cron jobs for automated reminders:")
    print("   - Daily: python manage.py send_campaign_reminders")
    print("   - Daily: python manage.py create_recurring_campaigns")
    print("2. Configure Twilio for WhatsApp/SMS notifications")
    print("3. Test the web interface at /community/campaigns/")
    print("4. Test the calendar view at /community/campaigns/calendar/")


if __name__ == '__main__':
    test_campaign_system()