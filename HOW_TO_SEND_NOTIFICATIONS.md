# 📧 How to Send Real-Time Notifications to Users

## Complete Guide to Multi-Channel Notifications

Your notification system is **already implemented**! Here's how to use it.

---

## 🚀 QUICK START (3 Steps)

### Step 1: Configure Twilio (for SMS & WhatsApp)

Add these to your `.env` file:

```env
# Twilio Configuration (for SMS and WhatsApp)
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Email Configuration (already in Django settings)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=EcoLearn <your-email@gmail.com>
```

**Get Twilio Credentials:**
1. Sign up at https://www.twilio.com/try-twilio
2. Get $15 free credit
3. Copy Account SID and Auth Token
4. Get a phone number for SMS
5. Enable WhatsApp sandbox

### Step 2: Import the Notification Service

```python
from community.notifications import notification_service, send_notification
```

### Step 3: Send Notifications!

```python
# Send to a single user
send_notification(
    user=user,
    title="Welcome to EcoLearn!",
    message="Thank you for joining our community.",
    notification_type='general',
    link='/dashboard/'
)
```

That's it! The system automatically sends via all enabled channels.

---

## 📱 METHOD 1: Simple Helper Function (Recommended)

### Send to One User (All Channels)

```python
from community.notifications import send_notification

# Example: Welcome new user
send_notification(
    user=request.user,
    title="Welcome to EcoLearn!",
    message="Start your environmental journey today.",
    notification_type='general',
    link='/elearning/modules/'
)
```

**What happens:**
- ✅ Creates in-app notification (always)
- ✅ Sends SMS (if user has SMS enabled + phone number)
- ✅ Sends WhatsApp (if user has WhatsApp enabled + phone number)
- ✅ User sees notification immediately

---

## 📨 METHOD 2: Specific Channel

### Send SMS Only

```python
from community.notifications import notification_service

result = notification_service.send_sms(
    to_number='+260971234567',  # Zambian number
    message='Your report has been verified! Thank you.'
)

if result['success']:
    print(f"SMS sent! Message ID: {result['message_sid']}")
else:
    print(f"Failed: {result['error']}")
```

### Send WhatsApp Only

```python
result = notification_service.send_whatsapp(
    to_number='+260971234567',
    message='*EcoLearn Update*\n\nYour challenge progress: 75% complete! 🎉',
    media_url='https://example.com/image.jpg'  # Optional
)
```

### Send Email Only

```python
result = notification_service.send_email(
    to_email='user@example.com',
    subject='Challenge Completed!',
    message='Congratulations! You completed the Recycling Challenge.',
    html_message='<h1>Congratulations!</h1><p>You completed the challenge.</p>'
)
```

### Create In-App Notification Only

```python
from community.models import Notification

notification = Notification.objects.create(
    user=user,
    notification_type='achievement',
    title='Badge Earned!',
    message='You earned the Eco Warrior badge!',
    url='/gamification/badges/'
)
```

---

## 👥 METHOD 3: Bulk Notifications

### Send to Multiple Users

```python
from community.notifications import notification_service
from accounts.models import CustomUser

# Get users
users = CustomUser.objects.filter(location__icontains='Kalingalinga')

# Send to all
data = {
    'campaign_name': 'Community Cleanup',
    'duration': '2 weeks',
    'goal': 'Collect 500 bags',
    'url': 'https://ecolearn.com/challenges/1/'
}

results = notification_service.bulk_notify(
    users=users,
    notification_type='campaign_launch',
    data=data,
    channels=['sms', 'whatsapp']  # Optional: specify channels
)

print(f"Sent: {results['success']}, Failed: {results['failed']}")
```

---

## 🎯 REAL-WORLD EXAMPLES

### Example 1: Report Status Update

```python
# In admin_dashboard/views.py or reporting/views.py

from community.notifications import send_notification

def update_report_status(request, report_id):
    report = get_object_or_404(DumpingReport, id=report_id)
    
    # Update status
    report.status = 'verified'
    report.save()
    
    # Notify user immediately
    if report.reporter and not report.is_anonymous:
        send_notification(
            user=report.reporter,
            title=f'Report Update: {report.reference_number}',
            message=f'Your report has been verified and forwarded to authorities.',
            notification_type='report_update',
            link=f'/reporting/reports/{report.id}/'
        )
    
    return redirect('admin_dashboard:reports')
```

**User receives:**
- 📱 SMS: "[EcoLearn] Report ZMR0042: Your report has been verified..."
- 💬 WhatsApp: "*Report Update: ZMR0042*\n\nYour report has been verified..."
- 🔔 In-app: Notification appears in their dashboard

---

### Example 2: Challenge Progress Update

```python
# In gamification/views.py or community/views.py

from community.notifications import send_notification

def update_challenge_progress(challenge, user, contribution):
    # Update progress
    participant = ChallengeParticipant.objects.get(
        challenge=challenge,
        user=user
    )
    participant.contribution += contribution
    participant.save()
    
    # Calculate progress
    progress = int((participant.contribution / challenge.target_goal) * 100)
    
    # Notify user at milestones
    if progress in [25, 50, 75, 100]:
        send_notification(
            user=user,
            title=f'Challenge Progress: {progress}%',
            message=f'Great work! You\'re {progress}% complete in {challenge.title}!',
            notification_type='challenge_update',
            link=f'/community/challenges/{challenge.id}/'
        )
```

---

### Example 3: Event Reminder (24 hours before)

```python
# In a scheduled task (celery, cron, etc.)

from community.notifications import notification_service
from community.models import CommunityEvent, EventParticipant
from django.utils import timezone
from datetime import timedelta

def send_event_reminders():
    # Get events starting in 24 hours
    tomorrow = timezone.now() + timedelta(hours=24)
    events = CommunityEvent.objects.filter(
        start_date__date=tomorrow.date(),
        is_active=True
    )
    
    for event in events:
        # Get all registered participants
        participants = EventParticipant.objects.filter(
            event=event
        ).select_related('user')
        
        for participant in participants:
            data = {
                'event_name': event.title,
                'date': event.start_date.strftime('%B %d, %Y'),
                'time': event.start_date.strftime('%I:%M %p'),
                'location': event.location,
                'url': f'https://ecolearn.com/community/events/{event.id}/'
            }
            
            notification_service.notify_user(
                user=participant.user,
                notification_type='event_reminder',
                data=data
            )
```

---

### Example 4: Welcome New User

```python
# In accounts/views.py after user registration

from community.notifications import send_notification

def register(request):
    if request.method == 'POST':
        # ... registration logic ...
        
        user = form.save()
        
        # Send welcome notification
        send_notification(
            user=user,
            title='Welcome to EcoLearn! 🌱',
            message='Start your environmental journey by completing your first module.',
            notification_type='general',
            link='/elearning/modules/'
        )
        
        return redirect('dashboard')
```

---

### Example 5: Badge Earned

```python
# In gamification/views.py

from community.notifications import send_notification

def award_badge(user, badge):
    # Award the badge
    user_badge = UserBadge.objects.create(
        user=user,
        badge=badge
    )
    
    # Notify immediately
    send_notification(
        user=user,
        title=f'Badge Earned: {badge.name}! 🏆',
        message=f'Congratulations! You earned the {badge.name} badge for {badge.description}',
        notification_type='achievement',
        link='/gamification/badges/'
    )
```

---

## 🎨 CUSTOM NOTIFICATION TEMPLATES

### Create Custom Message Format

```python
from community.notifications import notification_service

# Custom formatted message
def send_custom_notification(user, data):
    # SMS (short)
    sms_message = f"[EcoLearn] {data['title']}: {data['message'][:100]}"
    
    # WhatsApp (rich)
    whatsapp_message = f"""
*{data['title']}* 🌱

{data['message']}

{data.get('action', '')}

_EcoLearn - Together for a cleaner Zambia_
    """.strip()
    
    # Email (HTML)
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #22c55e;">{data['title']}</h2>
            <p>{data['message']}</p>
            <a href="{data['url']}" style="background: #22c55e; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                {data.get('button_text', 'View Details')}
            </a>
        </body>
    </html>
    """
    
    # Send via all channels
    if user.phone_number:
        notification_service.send_sms(str(user.phone_number), sms_message)
        notification_service.send_whatsapp(str(user.phone_number), whatsapp_message)
    
    if user.email:
        notification_service.send_email(
            user.email,
            data['title'],
            data['message'],
            html_message
        )
```

---

## 🔔 REAL-TIME IN-APP NOTIFICATIONS

### Display Notifications in Templates

```html
<!-- In your base template or dashboard -->
<div class="notifications-dropdown">
    <button class="notification-bell">
        <i class="fas fa-bell"></i>
        {% if unread_count > 0 %}
        <span class="badge">{{ unread_count }}</span>
        {% endif %}
    </button>
    
    <div class="notifications-list">
        {% for notification in recent_notifications %}
        <div class="notification-item {% if not notification.is_read %}unread{% endif %}">
            <h4>{{ notification.title }}</h4>
            <p>{{ notification.message }}</p>
            <small>{{ notification.created_at|timesince }} ago</small>
            {% if notification.url %}
            <a href="{{ notification.url }}">View</a>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</div>
```

### Get Notifications in View

```python
# In your view
def dashboard(request):
    # Get unread notifications
    unread_notifications = request.user.notifications.filter(
        is_read=False
    ).order_by('-created_at')
    
    # Get recent notifications
    recent_notifications = request.user.notifications.order_by(
        '-created_at'
    )[:10]
    
    context = {
        'unread_count': unread_notifications.count(),
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'dashboard.html', context)
```

### Mark as Read

```python
# In your view
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})
```

---

## 🎯 USER PREFERENCES

### Respect User Notification Preferences

The system automatically checks user preferences:

```python
# User preferences are stored in NotificationPreference model
# Automatically checked by send_notification()

# User can control:
# - SMS enabled/disabled
# - WhatsApp enabled/disabled
# - Email enabled/disabled
# - Notification types (events, challenges, forum, etc.)
# - Quiet hours (no notifications during sleep)
```

### Check Preferences Manually

```python
from accounts.models import NotificationPreference

def should_send_notification(user, notification_type):
    try:
        prefs = user.notification_preferences
        
        # Check if user wants this type
        if notification_type == 'event_reminder' and not prefs.event_reminders:
            return False
        
        # Check quiet hours
        if prefs.is_quiet_hours():
            return False
        
        return True
    except NotificationPreference.DoesNotExist:
        return True  # Send by default
```

---

## 📊 TRACK NOTIFICATION DELIVERY

### Log All Notifications

```python
from community.models import NotificationLog

# Automatically logged when using notification_service
# Check delivery status:

logs = NotificationLog.objects.filter(
    user=user,
    sent_at__date=timezone.now().date()
)

for log in logs:
    print(f"{log.channel}: {log.status} - {log.message[:50]}")
```

### Check Delivery Status

```python
# Get notification statistics
from community.models import NotificationLog
from django.db.models import Count

stats = NotificationLog.objects.values('status').annotate(
    count=Count('id')
)

for stat in stats:
    print(f"{stat['status']}: {stat['count']}")
```

---

## 🚨 ERROR HANDLING

### Handle Failed Notifications

```python
from community.notifications import notification_service

result = notification_service.send_sms(
    to_number=user.phone_number,
    message='Your notification'
)

if not result['success']:
    # Log error
    print(f"SMS failed: {result['error']}")
    
    # Try alternative channel
    notification_service.send_whatsapp(
        to_number=user.phone_number,
        message='Your notification'
    )
```

---

## 🎯 BEST PRACTICES

### 1. Keep Messages Short (SMS)
```python
# ✅ Good (under 160 chars)
"Your report ZMR0042 verified! View: ecolearn.com/r/42"

# ❌ Bad (too long)
"Hello! We wanted to inform you that your dumping report with reference number ZMR0042 has been successfully verified by our team and forwarded to the appropriate authorities for action..."
```

### 2. Use Rich Formatting (WhatsApp)
```python
# ✅ Good
message = """
*Report Verified!* ✅

Your report ZMR0042 has been verified.

*Next Steps:*
• Authorities notified
• Action within 48 hours
• Track progress online

View: ecolearn.com/r/42
"""
```

### 3. Personalize Messages
```python
# ✅ Good
f"Hi {user.first_name}! Your challenge progress: 75% 🎉"

# ❌ Generic
"Challenge progress updated"
```

### 4. Include Clear CTAs
```python
# ✅ Good
"New event tomorrow! Register now: ecolearn.com/events/5"

# ❌ Vague
"There's a new event"
```

### 5. Respect Quiet Hours
```python
# Check before sending
if user.notification_preferences.is_quiet_hours():
    # Queue for later or skip
    pass
else:
    send_notification(...)
```

---

## 🔧 TROUBLESHOOTING

### SMS Not Sending?
1. Check Twilio credentials in `.env`
2. Verify phone number format (+260...)
3. Check Twilio account balance
4. View error in NotificationLog

### WhatsApp Not Working?
1. Enable WhatsApp sandbox in Twilio
2. User must opt-in first (send "join" to sandbox)
3. Check TWILIO_WHATSAPP_NUMBER in `.env`

### Email Not Sending?
1. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
2. Enable "Less secure app access" (Gmail)
3. Or use App Password (recommended)

### In-App Notifications Not Showing?
1. Check template includes notification display
2. Verify user.notifications queryset
3. Check is_read status

---

## 📱 COMPLETE WORKING EXAMPLE

```python
# Complete example: Send notification when user completes a module

from community.notifications import send_notification
from community.models import NotificationLog

def complete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    user = request.user
    
    # Mark module as complete
    enrollment = Enrollment.objects.get(user=user, module=module)
    enrollment.completed_at = timezone.now()
    enrollment.save()
    
    # Award points
    user.userprofile.points += module.points_reward
    user.userprofile.save()
    
    # Send multi-channel notification
    send_notification(
        user=user,
        title=f'Module Completed: {module.title}! 🎓',
        message=f'Congratulations! You earned {module.points_reward} points. Keep learning!',
        notification_type='achievement',
        link=f'/elearning/modules/{module.id}/'
    )
    
    # User receives:
    # 1. In-app notification (immediate)
    # 2. SMS (if enabled): "[EcoLearn] Module Completed: Waste Management! You earned 50 points."
    # 3. WhatsApp (if enabled): "*Module Completed: Waste Management!* 🎓\n\nCongratulations! You earned 50 points..."
    # 4. Logged in NotificationLog for tracking
    
    messages.success(request, 'Module completed! Check your notifications.')
    return redirect('elearning:modules')
```

---

## 🎉 YOU'RE READY!

Your notification system is **fully functional**. Just:

1. **Configure Twilio** (add credentials to `.env`)
2. **Import the functions** (`from community.notifications import send_notification`)
3. **Send notifications** (call `send_notification(user, title, message)`)

**That's it!** Users will receive notifications in real-time across all channels.

---

## 📞 NEED HELP?

- Check `NOTIFICATION_SYSTEM_COMPLETE.md` for full documentation
- View examples in `community/notifications.py`
- Test in admin dashboard: `/admin-dashboard/notifications/`

**Happy Notifying!** 📧💬🔔
