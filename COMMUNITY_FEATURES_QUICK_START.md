# Community Engagement Features - Quick Start Guide

## 🚀 Getting Started

### 1. Social Media Sharing (WhatsApp & Facebook)

#### Where to Find It
- Success Stories: Click share buttons on any story
- Events: Share button on event details
- Challenges: Share button on challenge page
- Health Alerts: Share emergency alerts

#### How It Works
1. User clicks "Share on WhatsApp" or "Share on Facebook"
2. System generates shareable link with pre-filled message
3. Opens WhatsApp/Facebook with content ready to share
4. Tracks share in database for analytics

#### URLs
- Share endpoint: `/community/share-social/`
- Implemented in: `community/views.py` → `share_to_social()`

---

### 2. Discussion Forum

#### Access
- URL: `/community/forum/`
- Navbar: Community → Forum

#### Features
✅ **Categories**: Organized discussion topics
✅ **Create Topics**: Start new discussions
✅ **Reply**: Comment on existing topics
✅ **Search**: Find relevant discussions
✅ **Multilingual**: English, Bemba, Nyanja

#### How to Use

**Create a Topic**:
1. Go to forum category
2. Click "Create New Topic"
3. Enter title and content
4. Submit

**Reply to Topic**:
1. Open any topic
2. Scroll to reply form
3. Enter your response
4. Submit

**Admin Moderation**:
- Pin important topics
- Lock completed discussions
- Delete spam/inappropriate content

---

### 3. SMS/WhatsApp Notifications

#### Setup Required
1. Get Twilio account (https://www.twilio.com)
2. Add credentials to `.env`:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```
3. Install Twilio: `pip install twilio`

#### Automatic Notifications

**Event Registration**:
- User registers for event
- Receives SMS confirmation
- Gets reminder 24 hours before

**Health Alerts**:
- Admin creates health alert
- System sends SMS to affected users
- WhatsApp message with details

**Forum Activity**:
- Get notified when someone replies to your topic
- Opt-in/opt-out available

#### Manual Sending (Admin)
1. Go to Django Admin
2. Select Notifications
3. Choose notifications to send
4. Click "Send SMS" or "Send WhatsApp"

---

## 📊 Analytics Dashboard

### Track Engagement
- Social shares by platform
- Most shared content
- Forum activity metrics
- Notification delivery rates

### Access Analytics
- Admin Dashboard: `/admin-dashboard/`
- Community Impact: `/community/my-impact/`

---

## 🎯 Best Practices

### For Users
1. **Share Responsibly**: Only share accurate information
2. **Engage Respectfully**: Be kind in forum discussions
3. **Report Issues**: Flag inappropriate content
4. **Stay Informed**: Enable notifications for important updates

### For Admins
1. **Moderate Regularly**: Check forum daily
2. **Respond Quickly**: Address user concerns promptly
3. **Create Categories**: Organize forum topics logically
4. **Send Timely Notifications**: Don't spam users
5. **Track Metrics**: Monitor engagement trends

---

## 🔧 Troubleshooting

### Share Buttons Not Working
**Problem**: Clicking share does nothing
**Solution**:
- Check browser console for errors
- Verify CSRF token is present
- Test with different browser

### SMS Not Sending
**Problem**: Users not receiving SMS
**Solution**:
- Verify Twilio credentials in `.env`
- Check phone number format (+260...)
- Confirm Twilio account has credit
- Review Twilio logs for errors

### Forum Not Loading
**Problem**: Forum page shows error
**Solution**:
- Run migrations: `python manage.py migrate`
- Create forum categories in admin
- Check database connection

---

## 📱 Mobile Optimization

All features are mobile-responsive:
- ✅ Touch-friendly buttons
- ✅ Responsive layouts
- ✅ Mobile-optimized forms
- ✅ Fast loading times

---

## 🌍 Multilingual Support

### Available Languages
- English (en)
- Bemba (bem)
- Nyanja (ny)

### How to Switch
1. Click language selector in navbar
2. Choose preferred language
3. Content updates automatically

### For Admins
- Add translations in admin panel
- Use `name`, `name_bem`, `name_ny` fields
- System auto-selects based on user preference

---

## 📞 Support

### For Users
- Forum: Ask questions in discussion forum
- Contact: Use contact form on website
- Help: Check FAQ section

### For Admins
- Documentation: See full implementation guide
- Technical Support: Contact development team
- Training: Request admin training session

---

## ✅ Feature Checklist

### Social Sharing
- [x] WhatsApp integration
- [x] Facebook integration
- [x] Twitter integration
- [x] Share tracking
- [x] Pre-filled messages
- [x] Analytics dashboard

### Discussion Forum
- [x] Categories
- [x] Topics & Replies
- [x] Search functionality
- [x] Pagination
- [x] Moderation tools
- [x] Multilingual support

### Notifications
- [x] SMS sending
- [x] WhatsApp sending
- [x] Event reminders
- [x] Health alerts
- [x] Forum notifications
- [x] Delivery tracking

---

## 🎓 Training Resources

### Video Tutorials (Coming Soon)
- How to use the forum
- Sharing success stories
- Managing notifications
- Admin moderation guide

### Documentation
- Full Implementation Guide
- API Documentation
- Admin Manual
- User Guide

---

**Last Updated**: November 16, 2025
**Version**: 1.0
**Status**: Production Ready ✅
