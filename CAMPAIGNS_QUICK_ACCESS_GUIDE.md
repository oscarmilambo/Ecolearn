# 🌍 Community Campaigns - Quick Access Guide

## 🚀 Your Server is Running!
**URL: http://127.0.0.1:8000/**

✅ **AI Assistant is working!** - All import issues have been resolved.

## 📍 Where to Find Everything

### 1. **Campaign List Page** (FR08)
**URL: http://127.0.0.1:8000/community/campaigns/**
- View all active campaigns
- One-click registration
- Campaign types and details
- Participant counts

### 2. **Campaign Calendar** (FR09)
**URL: http://127.0.0.1:8000/community/campaigns/calendar/**
- Interactive calendar view
- Color-coded campaign types
- Click events for details
- Google Maps integration

### 3. **Admin Interface** (FR08)
**URL: http://127.0.0.1:8000/admin/community/communitycampaign/**
- Create new campaigns
- Manage participants
- Set recurring schedules
- Publish/unpublish campaigns

**Login Credentials:**
- Username: `campaign_admin`
- Password: `admin123`

### 4. **Sample Campaign Detail**
**URL: http://127.0.0.1:8000/community/campaigns/1/**
- Full campaign information
- Registration form
- Participant list
- Contact details

## 📊 Test Data Created

### ✅ 3 Sample Campaigns:
1. **Community Cleanup - Kabulonga** (Tomorrow at 8:00 AM)
2. **Recycling Workshop - Matero** (Next week at 2:00 PM) - Monthly recurring
3. **Zero-Plastic Challenge - Chilenje** (In 3 days at 9:00 AM) - Quarterly recurring

### ✅ 3 Test Users:
- `participant1` / `test123`
- `participant2` / `test123`
- `participant3` / `test123`

### ✅ 5 Registrations:
- Users already registered for various campaigns
- Different interest levels (Join, Interested, Maybe)

## 🔧 Key Features Working

### FR08 - Campaign Management ✅
- [x] Admin can create campaigns
- [x] Set recurring schedules (monthly, quarterly, yearly)
- [x] Multi-language support (English, Bemba, Nyanja)
- [x] Capacity management
- [x] Registration deadlines
- [x] One-click user registration
- [x] Participant tracking

### FR09 - Calendar & Reminders ✅
- [x] Interactive calendar display
- [x] Automatic reminder system (3-day and 1-day)
- [x] Registration confirmations
- [x] WhatsApp/SMS integration ready
- [x] Management commands for automation

## 🎯 Quick Test Steps

### 1. View Campaigns
1. Go to: http://127.0.0.1:8000/community/campaigns/
2. See 3 sample campaigns with different statuses
3. Click "Details" on any campaign

### 2. Test Registration
1. Login as `participant1` / `test123`
2. Go to a campaign detail page
3. Select interest level and click "Register Now"
4. See confirmation message

### 3. Admin Interface
1. Go to: http://127.0.0.1:8000/admin/
2. Login as `campaign_admin` / `admin123`
3. Navigate to Community → Community campaigns
4. Create a new campaign or edit existing ones

### 4. Calendar View
1. Go to: http://127.0.0.1:8000/community/campaigns/calendar/
2. See campaigns displayed on interactive calendar
3. Click on any event to see details modal

## 📱 Automated Features

### Management Commands (Ready for Cron Jobs)
```bash
# Send daily reminders
python manage.py send_campaign_reminders

# Create recurring campaigns
python manage.py create_recurring_campaigns
```

### Notification System
- WhatsApp/SMS reminders (needs Twilio configuration)
- In-app notifications
- Email notifications
- User preference respect

## 🔍 File Locations

### Models: `community/models.py`
- `CommunityCampaign` - Main campaign model
- `CampaignParticipant` - User registrations

### Views: `community/views.py`
- `campaigns_list` - Campaign listing
- `campaign_detail` - Individual campaign
- `campaign_calendar` - Calendar view
- `join_campaign` - Registration handling

### Templates:
- `community/templates/community/campaigns_list.html`
- `community/templates/community/campaign_detail.html`
- `community/templates/community/campaign_calendar.html`

### Admin: `community/admin.py`
- `CommunityCampaignAdmin` - Full admin interface
- `CampaignParticipantAdmin` - Participant management

## 🎉 Everything is Working!

The Community Campaigns System is **fully implemented** and **ready to use**. All functional requirements FR08 and FR09 are satisfied with:

- ✅ Campaign creation and management
- ✅ Recurring campaign automation
- ✅ User registration system
- ✅ Interactive calendar
- ✅ Reminder system
- ✅ Multi-language support
- ✅ Admin interface
- ✅ Mobile-responsive design

**Start exploring at: http://127.0.0.1:8000/community/campaigns/**