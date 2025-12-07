# 📧 Notification System - Quick Reference Card

## ⚡ FASTEST WAY TO SEND NOTIFICATIONS

### 1-Line Solution:
```python
from community.notifications import send_notification

send_notification(user, "Title", "Message", 'general', '/link/')
```

**User receives:** SMS + WhatsApp + Email + In-App notification ✅

---

## 🚀 SETUP (One-Time)

Add to `.env`:
```env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
```

Get free Twilio account: https://www.twilio.com/try-twilio

---

## 📱 COMMON USE CASES

### Report Verified
```python
send_notification(
    user=report.reporter,
    title=f'Report {report.reference_number} Verified',
    message='Your report has been verified!',
    notification_type='report_update',
    link=f'/reporting/reports/{report.id}/'
)
```

### Challenge Progress
```python
send_notification(
    user=user,
    title=f'Challenge {progress}% Complete',
    message=f'Great work on {challenge.title}!',
    notification_type='challenge_update',
    link=f'/community/challenges/{challenge.id}/'
)
```

### Badge Earned
```python
send_notification(
    user=user,
    title=f'Badge Earned: {badge.name}!',
    message='Congratulations on your achievement!',
    notification_type='achievement',
    link='/gamification/badges/'
)
```

### Event Reminder
```python
send_notification(
    user=participant.user,
    title=f'Event Tomorrow: {event.title}',
    message=f'Join us at {event.location}',
    notification_type='event_reminder',
    link=f'/community/events/{event.id}/'
)
```

---

## 🎯 SPECIFIC CHANNELS

### SMS Only
```python
from community.notifications import notification_service

notification_service.send_sms(
    to_number='+260971234567',
    message='Your message here'
)
```

### WhatsApp Only
```python
notification_service.send_whatsapp(
    to_number='+260971234567',
    message='*Bold* _italic_ message'
)
```

### Email Only
```python
notification_service.send_email(
    to_email='user@example.com',
    subject='Subject',
    message='Message'
)
```

---

## 👥 BULK NOTIFICATIONS

```python
users = CustomUser.objects.filter(location='Kalingalinga')

for user in users:
    send_notification(
        user=user,
        title='Community Cleanup Tomorrow',
        message='Join us at 9 AM!',
        notification_type='campaign'
    )
```

---

## 📊 CHECK DELIVERY STATUS

```python
from community.models import NotificationLog

# Recent notifications
logs = NotificationLog.objects.filter(
    user=user
).order_by('-sent_at')[:10]

for log in logs:
    print(f"{log.channel}: {log.status}")
```

---

## 🔔 IN-APP NOTIFICATIONS

### Display in Template
```html
{% for notif in user.notifications.all %}
<div class="notification">
    <h4>{{ notif.title }}</h4>
    <p>{{ notif.message }}</p>
    <small>{{ notif.created_at|timesince }} ago</small>
</div>
{% endfor %}
```

### Get in View
```python
def dashboard(request):
    notifications = request.user.notifications.filter(
        is_read=False
    ).order_by('-created_at')[:5]
    
    return render(request, 'dashboard.html', {
        'notifications': notifications
    })
```

---

## ✅ BEST PRACTICES

1. **Keep SMS under 160 characters**
2. **Use rich formatting in WhatsApp** (*bold*, _italic_)
3. **Personalize messages** (use user.first_name)
4. **Include clear CTAs** (links, actions)
5. **Respect quiet hours** (check preferences)

---

## 🎨 MESSAGE TEMPLATES

### Short (SMS)
```
[EcoLearn] Report ZMR0042 verified! View: ecolearn.com/r/42
```

### Rich (WhatsApp)
```
*Report Verified!* ✅

Your report ZMR0042 has been verified.

View details: ecolearn.com/r/42
```

### Detailed (Email)
```html
<h2>Report Verified!</h2>
<p>Your report ZMR0042 has been successfully verified.</p>
<a href="...">View Report</a>
```

---

## 🚨 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| SMS not sending | Check Twilio credentials in `.env` |
| WhatsApp not working | Enable WhatsApp sandbox in Twilio |
| Email not sending | Check EMAIL_HOST_USER in settings |
| In-app not showing | Check template includes notifications |

---

## 📞 ADMIN DASHBOARD

Send campaigns via UI:
1. Go to `/admin-dashboard/notifications/`
2. Click "Send Campaign"
3. Enter message and select channels
4. Choose target audience
5. Send!

---

## 🎯 NOTIFICATION TYPES

- `general` - General notifications
- `event_reminder` - Event reminders
- `challenge_update` - Challenge progress
- `report_update` - Report status changes
- `achievement` - Badges, rewards
- `campaign` - Marketing campaigns
- `emergency` - Urgent alerts

---

## 📚 MORE EXAMPLES

See `notification_examples.py` for 15+ ready-to-use examples!

See `HOW_TO_SEND_NOTIFICATIONS.md` for complete guide!

---

## ⚡ QUICK TEST

```python
from notification_examples import test_notification_system

# Test all channels
results = test_notification_system(request.user)
```

---

**That's it! Start sending notifications now!** 🚀
