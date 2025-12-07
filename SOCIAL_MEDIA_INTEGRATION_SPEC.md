# 📱 Social Media Integration & Notification System - Complete Specification

## Overview
This document outlines the complete implementation of social media sharing, WhatsApp/SMS notifications, and enhanced forum features for EcoLearn.

---

## 1️⃣ WHATSAPP & FACEBOOK INTEGRATION

### A. Success Stories Sharing

#### Features:
- **One-Click Sharing** to WhatsApp and Facebook
- **Pre-formatted Messages** with story highlights
- **Image Sharing** with story photos
- **Deep Links** back to EcoLearn platform
- **Share Tracking** for analytics

#### Implementation Components:

**1. Share Buttons on Success Stories**
- Location: Story detail page, story cards
- Platforms: WhatsApp, Facebook, Twitter, LinkedIn
- Format: Native share APIs + fallback URLs

**2. WhatsApp Sharing**
```python
# WhatsApp Web API
https://wa.me/?text={encoded_message}

# WhatsApp Business API (for automated messages)
- Requires WhatsApp Business Account
- Template messages for notifications
- Interactive buttons
```

**3. Facebook Sharing**
```javascript
// Facebook Share Dialog
FB.ui({
  method: 'share',
  href: 'https://ecolearn.zm/stories/123',
  quote: 'Check out this amazing environmental success story!'
});
```

**4. Share Message Template**
```
🌍 EcoLearn Success Story

{story_title}

{story_excerpt}

Impact: {impact_metric}
Location: {location}

Read more: {story_url}

#EcoLearn #EnvironmentalAction #Zambia
```

---

### B. Challenge Sharing

#### Features:
- **Challenge Invitations** via WhatsApp
- **Group Challenges** with WhatsApp groups
- **Progress Updates** shared automatically
- **Completion Certificates** shareable

#### Implementation:

**1. Challenge Invitation System**
```python
def generate_challenge_invite(challenge, user):
    message = f"""
    🏆 Join me in the {challenge.title}!
    
    📅 {challenge.start_date} - {challenge.end_date}
    🎯 Goal: {challenge.goal}
    🏅 Reward: {challenge.reward_points} points
    
    Join now: {challenge_url}
    
    Let's make a difference together! 🌱
    """
    return message
```

**2. WhatsApp Group Integration**
- Create challenge-specific WhatsApp groups
- Auto-post updates to groups
- Share participant progress
- Celebrate completions

---

## 2️⃣ ENHANCED DISCUSSION FORUM

### Current Status:
✅ Forum exists with categories, topics, replies
✅ Basic moderation features

### Enhancements Needed:

#### A. Best Practices Section
- **Dedicated Category** for best practices
- **Verified Tips** badge for admin-approved posts
- **Rating System** for helpful posts
- **Search & Filter** by topic, location, waste type

#### B. Feedback System
- **Suggestion Box** for platform improvements
- **Feature Requests** voting system
- **Bug Reports** with priority levels
- **Admin Response** tracking

#### C. Rich Media Support
- **Image Uploads** in posts
- **Video Embeds** (YouTube, Vimeo)
- **File Attachments** (PDFs, documents)
- **Polls & Surveys**

#### D. Engagement Features
- **Mentions** (@username)
- **Hashtags** (#recycling, #cleanup)
- **Reactions** (like, helpful, inspiring)
- **Bookmarks** for saving posts
- **Follow Topics** for notifications

---

## 3️⃣ SMS/WHATSAPP NOTIFICATION SYSTEM

### A. Notification Types

#### 1. Event Notifications
```
📅 Upcoming Event Alert!

Event: Community Cleanup - Matero
Date: Saturday, Nov 25, 2025
Time: 8:00 AM
Location: Matero Market

Register: {event_url}

See you there! 🌱
```

#### 2. Campaign Notifications
```
🚀 New Campaign Launched!

Campaign: Plastic-Free December
Duration: Dec 1-31, 2025
Goal: Reduce plastic use by 50%

Join now: {campaign_url}

Together we can make a difference!
```

#### 3. Challenge Updates
```
🏆 Challenge Update!

Challenge: Weekly Recycling Challenge
Your Progress: 75% complete
Rank: #12 out of 150

Keep going! You're almost there! 💪
```

#### 4. Reward Notifications
```
🎁 Reward Redeemed!

Reward: EcoLearn T-Shirt
Redemption Code: ECO-2025-1234
Status: Approved

Collect at: Lusaka Office
Contact: +260 XXX XXXX
```

---

### B. Notification Channels

#### SMS (via Twilio)
- **Use Cases:** Critical alerts, event reminders
- **Character Limit:** 160 characters
- **Cost:** ~$0.05 per SMS
- **Delivery:** Instant

#### WhatsApp (via Twilio/WhatsApp Business API)
- **Use Cases:** Rich notifications, images, buttons
- **Character Limit:** 4096 characters
- **Cost:** ~$0.005 per message
- **Delivery:** Instant
- **Features:** Images, buttons, templates

#### Email (Backup)
- **Use Cases:** Detailed notifications, newsletters
- **Cost:** Free (via Django)
- **Delivery:** Near-instant

---

### C. Notification Preferences

Users can control:
- ✅ Event reminders (SMS/WhatsApp/Email)
- ✅ Challenge updates (WhatsApp/Email)
- ✅ Forum replies (Email only)
- ✅ Reward status (SMS/WhatsApp)
- ✅ Community news (Email/WhatsApp)
- ✅ Frequency (Instant, Daily digest, Weekly)

---

## 4️⃣ TECHNICAL IMPLEMENTATION

### A. Required Services

#### 1. Twilio (SMS & WhatsApp)
```python
# Install
pip install twilio

# Configuration
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+1234567890'
```

#### 2. Facebook SDK
```javascript
// Facebook JavaScript SDK
<script async defer crossorigin="anonymous" 
  src="https://connect.facebook.net/en_US/sdk.js#xfbml=1&version=v18.0&appId=YOUR_APP_ID">
</script>
```

#### 3. WhatsApp Business API
- Requires business verification
- Template message approval
- Webhook setup for responses

---

### B. Database Models

#### NotificationPreference Model
```python
class NotificationPreference(models.Model):
    user = models.OneToOneField(User)
    
    # Channels
    sms_enabled = models.BooleanField(default=True)
    whatsapp_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    
    # Types
    event_reminders = models.BooleanField(default=True)
    challenge_updates = models.BooleanField(default=True)
    forum_replies = models.BooleanField(default=True)
    reward_updates = models.BooleanField(default=True)
    
    # Frequency
    frequency = models.CharField(
        choices=[
            ('instant', 'Instant'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Summary')
        ],
        default='instant'
    )
```

#### SocialShare Model
```python
class SocialShare(models.Model):
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    
    platform = models.CharField(
        choices=[
            ('whatsapp', 'WhatsApp'),
            ('facebook', 'Facebook'),
            ('twitter', 'Twitter'),
            ('linkedin', 'LinkedIn')
        ]
    )
    
    shared_at = models.DateTimeField(auto_now_add=True)
    clicks = models.IntegerField(default=0)
```

#### NotificationLog Model
```python
class NotificationLog(models.Model):
    user = models.ForeignKey(User)
    channel = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(
        choices=[
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed'),
            ('pending', 'Pending')
        ]
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True)
    error_message = models.TextField(blank=True)
```

---

### C. API Endpoints

#### Social Sharing
```python
POST /api/share/
{
    "content_type": "story",
    "object_id": 123,
    "platform": "whatsapp"
}

Response:
{
    "share_url": "https://wa.me/?text=...",
    "success": true
}
```

#### Send Notification
```python
POST /api/notifications/send/
{
    "user_ids": [1, 2, 3],
    "channel": "whatsapp",
    "template": "event_reminder",
    "data": {
        "event_name": "Community Cleanup",
        "event_date": "2025-11-25"
    }
}
```

---

## 5️⃣ USER INTERFACE COMPONENTS

### A. Share Buttons Component
```html
<div class="share-buttons">
    <button class="share-whatsapp">
        <i class="fab fa-whatsapp"></i> Share on WhatsApp
    </button>
    <button class="share-facebook">
        <i class="fab fa-facebook"></i> Share on Facebook
    </button>
    <button class="share-twitter">
        <i class="fab fa-twitter"></i> Share on Twitter
    </button>
    <button class="copy-link">
        <i class="fas fa-link"></i> Copy Link
    </button>
</div>
```

### B. Notification Preferences Page
- Toggle switches for each notification type
- Channel selection (SMS/WhatsApp/Email)
- Frequency settings
- Test notification button
- Notification history

### C. Forum Enhancements
- Rich text editor (TinyMCE/CKEditor)
- Image upload with preview
- Mention autocomplete
- Hashtag suggestions
- Reaction buttons
- Bookmark icon

---

## 6️⃣ IMPLEMENTATION PHASES

### Phase 1: Social Sharing (Week 1-2)
- ✅ Add share buttons to stories
- ✅ Implement WhatsApp sharing
- ✅ Implement Facebook sharing
- ✅ Track share analytics
- ✅ Test on mobile devices

### Phase 2: SMS/WhatsApp Notifications (Week 3-4)
- ✅ Set up Twilio account
- ✅ Create notification templates
- ✅ Build notification service
- ✅ Implement event reminders
- ✅ Add user preferences

### Phase 3: Forum Enhancements (Week 5-6)
- ✅ Add rich text editor
- ✅ Implement image uploads
- ✅ Add reactions system
- ✅ Build mention system
- ✅ Create best practices section

### Phase 4: Testing & Optimization (Week 7-8)
- ✅ User acceptance testing
- ✅ Performance optimization
- ✅ Bug fixes
- ✅ Documentation
- ✅ Training materials

---

## 7️⃣ COST ESTIMATES

### Monthly Costs (for 1000 active users):

**Twilio SMS:**
- 500 SMS/month × $0.05 = $25/month

**Twilio WhatsApp:**
- 2000 messages/month × $0.005 = $10/month

**Facebook API:**
- Free (no cost for sharing)

**WhatsApp Business API:**
- $0 setup (if using Twilio)
- Pay per message (included above)

**Total: ~$35/month** for 1000 users

---

## 8️⃣ SECURITY & PRIVACY

### Data Protection:
- ✅ User consent for notifications
- ✅ Opt-out mechanism
- ✅ Phone number encryption
- ✅ GDPR compliance
- ✅ Rate limiting on shares

### API Security:
- ✅ API key rotation
- ✅ Webhook signature verification
- ✅ HTTPS only
- ✅ Rate limiting
- ✅ Input validation

---

## 9️⃣ ANALYTICS & REPORTING

### Track:
- Share counts by platform
- Notification delivery rates
- User engagement with shared content
- Most shared stories/challenges
- Notification open rates
- Forum activity metrics

### Dashboard Metrics:
- Total shares this month
- WhatsApp vs Facebook shares
- Notification success rate
- Most active forum topics
- User engagement trends

---

## 🔟 SUCCESS METRICS

### KPIs:
- **Share Rate:** 20% of users share content monthly
- **Notification Delivery:** 95% success rate
- **Forum Engagement:** 40% of users post/reply monthly
- **Event Attendance:** 30% increase via notifications
- **User Satisfaction:** 4.5/5 rating for notifications

---

## NEXT STEPS

1. **Approve Specification** ✅
2. **Set up Twilio Account** 
3. **Create Facebook App**
4. **Implement Phase 1** (Social Sharing)
5. **Test with Beta Users**
6. **Roll out to All Users**

---

**Status:** Ready for Implementation
**Priority:** High
**Estimated Time:** 8 weeks
**Team Required:** 2 developers, 1 QA tester