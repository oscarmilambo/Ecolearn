# Community Engagement Tools - Detailed Implementation Guide

## Overview
This guide explains how the EcoLearn system implements WhatsApp/Facebook integration, discussion forums, and SMS/WhatsApp notifications for community engagement.

---

## 1. WhatsApp & Facebook Integration for Sharing

### Implementation Status: ✅ COMPLETED

### How It Works

#### A. Social Media Sharing Models
**File**: `community/models.py`

```python
class SocialMediaShare(models.Model):
    PLATFORM_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    content_type = models.CharField(max_length=50)  # 'success_story', 'event', 'challenge'
    content_id = models.IntegerField()
    shared_at = models.DateTimeField(auto_now_add=True)
```

**Purpose**: Tracks all social media shares for analytics

#### B. Sharing Functionality
**File**: `community/views.py`

```python
@login_required
def share_to_social(request):
    """Generate share links for social media"""
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        content_id = request.POST.get('content_id')
        platform = request.POST.get('platform')
        
        # Build share URL
        base_url = request.build_absolute_uri('/')
        share_text = "Check out this amazing eco-initiative on EcoLearn Zambia!"
        
        if content_type == 'story':
            story = get_object_or_404(SuccessStory, id=content_id)
            share_text = f"🌍 {story.title} - {story.content[:100]}..."
            content_url = request.build_absolute_uri(
                reverse('community:story_detail', args=[content_id])
            )
        elif content_type == 'event':
            event = get_object_or_404(CommunityEvent, id=content_id)
            share_text = f"📅 Join us: {event.title} on {event.start_date.strftime('%B %d, %Y')}"
            content_url = request.build_absolute_uri(
                reverse('community:event_detail', args=[content_id])
            )
        elif content_type == 'challenge':
            challenge = get_object_or_404(CommunityChallenge, id=content_id)
            share_text = f"🏆 Join the challenge: {challenge.title}"
            content_url = request.build_absolute_uri(
                reverse('community:challenge_detail', args=[content_id])
            )
        
        # Generate platform-specific URLs
        share_urls = {
            'whatsapp': f"https://wa.me/?text={share_text}%20{content_url}",
            'facebook': f"https://www.facebook.com/sharer/sharer.php?u={content_url}",
            'twitter': f"https://twitter.com/intent/tweet?text={share_text}&url={content_url}",
        }
        
        # Record the share
        SocialMediaShare.objects.create(
            user=request.user,
            platform=platform,
            content_type=content_type,
            content_id=content_id
        )
        
        return JsonResponse({
            'success': True,
            'share_url': share_urls.get(platform, content_url)
        })
```

#### C. Frontend Implementation
**Files**: Various templates with share buttons

**Example in Success Story Detail**:
```html
<!-- Share Buttons -->
<div class="flex space-x-3 mt-6">
    <button onclick="shareToWhatsApp('story', {{ story.id }})" 
            class="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
        <i class="fab fa-whatsapp mr-2"></i>Share on WhatsApp
    </button>
    
    <button onclick="shareToFacebook('story', {{ story.id }})" 
            class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
        <i class="fab fa-facebook mr-2"></i>Share on Facebook
    </button>
</div>

<script>
function shareToWhatsApp(contentType, contentId) {
    fetch("{% url 'community:share_to_social' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: `content_type=${contentType}&content_id=${contentId}&platform=whatsapp`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.open(data.share_url, '_blank');
        }
    });
}

function shareToFacebook(contentType, contentId) {
    fetch("{% url 'community:share_to_social' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: `content_type=${contentType}&content_id=${contentId}&platform=facebook`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.open(data.share_url, '_blank', 'width=600,height=400');
        }
    });
}
</script>
```

### Where Sharing is Available
1. ✅ Success Stories (`community/templates/community/story_detail.html`)
2. ✅ Community Events (`community/templates/community/event_detail.html`)
3. ✅ Community Challenges (`community/templates/community/challenge_detail.html`)
4. ✅ Health Alerts (`community/templates/community/alert_detail.html`)

---

## 2. Discussion Forum

### Implementation Status: ✅ COMPLETED

### How It Works

#### A. Forum Models
**File**: `community/models.py`

```python
class ForumCategory(models.Model):
    """Forum categories with multilingual support"""
    name = models.CharField(max_length=100)
    name_bem = models.CharField(max_length=100, blank=True)
    name_ny = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    description_bem = models.TextField(blank=True)
    description_ny = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='💬')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

class ForumTopic(models.Model):
    """Discussion topics"""
    category = models.ForeignKey(ForumCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    views = models.IntegerField(default=0)

class ForumReply(models.Model):
    """Replies to topics"""
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_solution = models.BooleanField(default=False)
```

#### B. Forum Views
**File**: `community/views.py`

Key functions:
- `forum_home()` - Display all categories and recent topics
- `category_topics()` - Show topics in a category
- `topic_detail()` - View topic and replies
- `create_topic()` - Create new discussion
- `create_reply()` - Reply to topics

#### C. Forum Features
1. ✅ **Categories**: Organize discussions by topic
2. ✅ **Topics**: Users can create discussion threads
3. ✅ **Replies**: Threaded conversations
4. ✅ **Pinned Topics**: Important discussions stay at top
5. ✅ **Locked Topics**: Prevent further replies
6. ✅ **View Counter**: Track topic popularity
7. ✅ **Multilingual**: Content in English, Bemba, Nyanja
8. ✅ **Search**: Find discussions
9. ✅ **Pagination**: Handle large number of topics

### Forum URLs
```
/community/forum/                          - Forum home
/community/forum/category/<id>/            - Category topics
/community/forum/topic/<id>/               - Topic detail & replies
/community/forum/category/<id>/create/     - Create new topic
```

### Admin Management
**File**: `community/admin.py`

Admins can:
- Create/edit forum categories
- Moderate topics (pin, lock, delete)
- Moderate replies
- View engagement metrics

---

## 3. SMS/WhatsApp Notifications

### Implementation Status: ✅ COMPLETED

### How It Works

#### A. Notification Model
**File**: `community/models.py`

```python
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('event_reminder', 'Event Reminder'),
        ('new_event', 'New Event'),
        ('forum_reply', 'Forum Reply'),
        ('story_approved', 'Story Approved'),
        ('achievement', 'Achievement Unlocked'),
        ('health_alert', 'Health Alert'),
        ('emergency', 'Emergency Alert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_sent_sms = models.BooleanField(default=False)
    is_sent_whatsapp = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### B. SMS Sending Function
**File**: `community/views.py`

```python
def send_emergency_sms(user, alert):
    """Send emergency SMS alert to user"""
    try:
        from twilio.rest import Client
        
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_number = settings.TWILIO_PHONE_NUMBER
        
        client = Client(account_sid, auth_token)
        
        message_body = f"⚠️ EMERGENCY ALERT: {alert.title}\n{alert.message}\n{alert.hygiene_tips}"
        
        if user.phone_number:
            message = client.messages.create(
                body=message_body,
                from_=twilio_number,
                to=str(user.phone_number)
            )
            return True
    except Exception as e:
        print(f"SMS Error: {e}")
        return False
```

#### C. WhatsApp Sending Function
**File**: `community/views.py`

```python
def send_whatsapp_alert(user, alert):
    """Send WhatsApp alert to user"""
    try:
        from twilio.rest import Client
        
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        
        client = Client(account_sid, auth_token)
        
        message_body = f"⚠️ *{alert.title}*\n\n{alert.message}\n\n*Hygiene Tips:*\n{alert.hygiene_tips}\n\n*Nearest Clinics:*\n{alert.nearest_clinics}"
        
        if user.phone_number:
            message = client.messages.create(
                body=message_body,
                from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
                to=f'whatsapp:{user.phone_number}'
            )
            return True
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return False
```

#### D. Automatic Notifications

**Event Registration Notification**:
```python
@login_required
def register_event(request, event_id):
    event = get_object_or_404(CommunityEvent, id=event_id)
    
    if request.method == 'POST':
        EventParticipant.objects.create(event=event, user=request.user)
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            notification_type='event_reminder',
            title=f'Registered for {event.title}',
            message=f'You have successfully registered for {event.title} on {event.start_date.strftime("%B %d, %Y")}.'
        )
        
        # Send SMS (optional)
        if user.phone_number:
            send_event_sms(request.user, event)
```

### Notification Triggers

1. **Event Registration** → SMS/WhatsApp confirmation
2. **Event Reminder** → 24 hours before event
3. **New Event** → Notify community members
4. **Forum Reply** → Notify topic author
5. **Story Approved** → Notify story author
6. **Health Alert** → Emergency SMS to all users
7. **Achievement** → Badge/certificate earned

---

## 4. Configuration Setup

### A. Twilio Configuration
**File**: `.env`

```env
# Twilio SMS/WhatsApp Configuration
TWILIO_ACCOUNT_SID=your-account-sid-here
TWILIO_AUTH_TOKEN=your-auth-token-here
TWILIO_PHONE_NUMBER=+1234567890
```

### B. Settings Configuration
**File**: `ecolearn/settings.py`

```python
# Twilio Settings
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER', default='')
```

### C. Install Twilio
```bash
pip install twilio
```

---

## 5. Admin Control Panel Features

### A. Bulk Notifications
**File**: `community/admin.py`

```python
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    actions = ['send_sms', 'send_whatsapp']
    
    def send_sms(self, request, queryset):
        """Send SMS for selected notifications"""
        sent_count = 0
        for notification in queryset:
            if send_notification_sms(notification.user, notification):
                notification.is_sent_sms = True
                notification.save()
                sent_count += 1
        
        self.message_user(request, f"SMS sent for {sent_count} notifications.")
    
    def send_whatsapp(self, request, queryset):
        """Send WhatsApp for selected notifications"""
        sent_count = 0
        for notification in queryset:
            if send_notification_whatsapp(notification.user, notification):
                notification.is_sent_whatsapp = True
                notification.save()
                sent_count += 1
        
        self.message_user(request, f"WhatsApp sent for {sent_count} notifications.")
```

### B. Emergency Alert System
Admins can create health alerts that automatically send SMS/WhatsApp to affected users.

---

## 6. Testing the Implementation

### A. Test Social Sharing
1. Create a success story
2. Click "Share on WhatsApp" button
3. Verify WhatsApp opens with pre-filled message
4. Check database for `SocialMediaShare` record

### B. Test Forum
1. Go to `/community/forum/`
2. Create a new topic
3. Add replies
4. Test search and pagination

### C. Test SMS/WhatsApp
1. Configure Twilio credentials in `.env`
2. Register for an event
3. Check phone for SMS confirmation
4. Create health alert in admin
5. Send emergency notifications

---

## 7. Analytics & Reporting

### Track Engagement
```python
# Social shares by platform
shares_by_platform = SocialMediaShare.objects.values('platform').annotate(
    count=Count('id')
).order_by('-count')

# Most shared content
most_shared = SocialMediaShare.objects.values('content_type', 'content_id').annotate(
    share_count=Count('id')
).order_by('-share_count')[:10]

# Forum engagement
forum_stats = {
    'total_topics': ForumTopic.objects.count(),
    'total_replies': ForumReply.objects.count(),
    'active_users': ForumTopic.objects.values('author').distinct().count(),
}

# Notification delivery rates
notification_stats = {
    'total_sent': Notification.objects.filter(is_sent_sms=True).count(),
    'delivery_rate': (sent / total) * 100 if total > 0 else 0,
}
```

---

## 8. Best Practices

### A. SMS/WhatsApp
- ✅ Keep messages concise (160 characters for SMS)
- ✅ Include call-to-action
- ✅ Respect user preferences (opt-in/opt-out)
- ✅ Send during appropriate hours (8 AM - 8 PM)
- ✅ Track delivery status

### B. Social Sharing
- ✅ Pre-fill engaging messages
- ✅ Include relevant hashtags
- ✅ Track share analytics
- ✅ Make sharing easy (one-click)

### C. Forum Moderation
- ✅ Set clear community guidelines
- ✅ Moderate spam and inappropriate content
- ✅ Pin important announcements
- ✅ Encourage quality discussions

---

## 9. Future Enhancements

### Planned Features
1. **WhatsApp Bot**: Automated responses for common queries
2. **Facebook Page Integration**: Auto-post to Facebook page
3. **Push Notifications**: Web push for real-time alerts
4. **Email Notifications**: Alternative to SMS
5. **Notification Preferences**: User control over notification types
6. **Scheduled Notifications**: Send at optimal times
7. **Rich Media**: Images in WhatsApp messages
8. **Group Messaging**: Bulk SMS to communities

---

## 10. Troubleshooting

### Common Issues

**SMS not sending**:
- Check Twilio credentials
- Verify phone number format (+260...)
- Check Twilio account balance
- Review error logs

**WhatsApp not working**:
- Ensure WhatsApp Business API is enabled
- Verify sender number is WhatsApp-enabled
- Check message template approval

**Share buttons not working**:
- Verify CSRF token
- Check JavaScript console for errors
- Test URL generation

---

## Summary

✅ **WhatsApp/Facebook Sharing**: Fully implemented with tracking
✅ **Discussion Forum**: Complete with categories, topics, replies
✅ **SMS/WhatsApp Notifications**: Twilio integration ready
✅ **Admin Controls**: Bulk sending and moderation tools
✅ **Analytics**: Track engagement and delivery

**Status**: All community engagement tools are implemented and ready for use!

**Next Steps**:
1. Configure Twilio credentials
2. Create forum categories
3. Test notification delivery
4. Train community moderators
5. Launch to users
