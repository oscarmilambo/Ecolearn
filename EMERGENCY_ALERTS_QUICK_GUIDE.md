# 🚨 Emergency Alert System - Quick Usage Guide

## ⚡ FASTEST WAY TO SEND EMERGENCY ALERTS

### 1-Line Emergency Alert:
```python
from community.notifications import send_cholera_alert

send_cholera_alert(
    location="Kalingalinga Compound",
    affected_areas="Blocks A, B, C - Market area",
    nearest_clinics="Kalingalinga Clinic: +260-XXX-XXXX"
)
```

**Users receive:** SMS + WhatsApp + In-App emergency notifications ✅

---

## 🚀 QUICK SETUP (Admin Dashboard)

### Send Emergency Alert via UI:
1. Go to `/admin-dashboard/alerts/`
2. Click "Create Alert"
3. Select type: Cholera, Flooding, Medical Waste, etc.
4. Set severity: Critical, High, Medium, Low
5. Enter location and safety instructions
6. Check "Send immediately"
7. Click "Create Alert"

**Users get notified instantly!** 📱💬🔔

---

## 📱 ALERT TYPES & QUICK FUNCTIONS

### Cholera Outbreak 🦠
```python
from community.notifications import send_cholera_alert

send_cholera_alert(
    location="Kanyama Compound",
    affected_areas="Market area, Block 5",
    nearest_clinics="Kanyama Clinic: +260-XXX-XXXX",
    target_locations=["Kanyama"]  # Optional: target specific areas
)
```

### Flooding Warning 🌊
```python
from community.notifications import send_flooding_alert

send_flooding_alert(
    location="Chawama area",
    affected_areas="Low-lying areas near river",
    target_locations=["Chawama", "Kanyama"]
)
```

### Medical Waste Alert ☠️
```python
from community.notifications import send_medical_waste_alert

send_medical_waste_alert(
    location="Behind Kalingalinga Primary School",
    affected_areas="School playground area"
)
```

### Custom Emergency Alert 🚨
```python
from community.notifications import send_emergency_alert

send_emergency_alert(
    alert_type='water_contamination',
    severity='high',
    title='Water Contamination Alert',
    message='Well water contaminated. Do not use for drinking.',
    location='Kalingalinga Well #3',
    hygiene_tips='Use bottled water. Boil all water for 10 minutes.',
    nearest_clinics='Kalingalinga Health Center: +260-XXX-XXXX'
)
```

---

## 🎯 PRIORITY REPORT ESCALATION

### Automatic Detection:
- High/Critical severity reports
- Medical waste keywords
- Hazardous material mentions
- Hospital/clinic waste

### Manual Escalation:
1. Go to `/admin-dashboard/priority-reports/`
2. Review flagged reports
3. Click "Escalate" for urgent reports
4. Select authority (ZEMA, LCC, MOH)
5. Add urgency notes
6. Click "Escalate Report"

**Authority gets urgent email + User gets notification** ✅

---

## 📊 WHAT USERS RECEIVE

### SMS (160 chars):
```
🚨 HEALTH ALERT: Cholera outbreak in Kalingalinga. 
Boil water, wash hands. Safety: Avoid raw foods...
```

### WhatsApp (Rich format):
```
🚨 *HEALTH ALERT - CRITICAL*

*Cholera Outbreak in Kalingalinga*

*Location:* Kalingalinga Compound
*Affected Areas:* Blocks A, B, C

*Alert:*
Multiple cholera cases confirmed. Immediate action required.

*Safety Tips:*
- Boil all drinking water for 5 minutes
- Wash hands with soap frequently
- Avoid raw or undercooked food
- Use ORS if symptoms occur

*Nearest Clinics:*
- Kalingalinga Clinic: +260-XXX-XXXX
- Lusaka General Hospital: +260-XXX-XXXX

Stay safe! - EcoLearn Emergency System
```

### In-App Notification:
```
🚨 Cholera Outbreak in Kalingalinga
Multiple cases confirmed. Take immediate precautions.
[View Safety Instructions]
```

---

## 🔧 ADMIN DASHBOARD FEATURES

### Emergency Alerts Dashboard:
- **URL:** `/admin-dashboard/alerts/`
- View all alerts
- Filter by type/severity
- Create new alerts
- Send to users
- Track performance

### Priority Reports:
- **URL:** `/admin-dashboard/priority-reports/`
- Auto-flagged high-priority reports
- Medical waste detection
- Escalation to authorities
- Urgent notifications

### Quick Actions:
- Create alert → Send immediately
- Escalate report → Notify authority
- Toggle alert status
- View alert analytics

---

## 🎨 ALERT SEVERITY GUIDE

### 🔴 Critical (Red)
- **Use for:** Immediate life threats
- **Examples:** Cholera outbreak, toxic spill
- **Response:** Send to ALL users immediately

### 🟠 High (Orange)
- **Use for:** Serious health risks
- **Examples:** Medical waste, contaminated water
- **Response:** Send to affected areas

### 🟡 Medium (Yellow)
- **Use for:** Moderate risks
- **Examples:** Flooding warning, air quality
- **Response:** Targeted notifications

### 🟢 Low (Green)
- **Use for:** Precautionary alerts
- **Examples:** Health advisories, prevention tips
- **Response:** Informational only

---

## 📍 LOCATION TARGETING

### Target All Users:
```python
send_cholera_alert(location="Lusaka City")
# Sends to ALL active users
```

### Target Specific Areas:
```python
send_cholera_alert(
    location="Kalingalinga",
    target_locations=["Kalingalinga", "Kanyama"]
)
# Sends only to users in these areas
```

### Common Target Areas:
- Kalingalinga
- Kanyama
- Chawama
- Mtendere
- Ng'ombe
- Garden Compound

---

## 🚨 EMERGENCY SCENARIOS

### Scenario 1: Cholera Outbreak
```python
# Immediate response
send_cholera_alert(
    location="Kalingalinga Market",
    affected_areas="Market stalls, surrounding blocks",
    nearest_clinics="Kalingalinga Clinic: 999, UTH: +260-XXX-XXXX"
)

# Result: 500+ users notified in seconds
```

### Scenario 2: Medical Waste Discovery
```python
# Quick alert
send_medical_waste_alert(
    location="Behind Kanyama School",
    affected_areas="School playground, nearby houses"
)

# Also escalate the report
# Go to priority-reports → escalate to MOH
```

### Scenario 3: Flooding Emergency
```python
# Weather alert
send_flooding_alert(
    location="Chawama low-lying areas",
    affected_areas="Near Chawama stream",
    target_locations=["Chawama", "Kanyama"]
)
```

---

## 📊 TRACKING & ANALYTICS

### View Alert Performance:
1. Go to alert detail page
2. See delivery statistics:
   - SMS sent/delivered
   - WhatsApp sent/delivered
   - In-app notifications created
   - Failed deliveries

### Monitor Escalations:
1. Check priority reports dashboard
2. View escalation status
3. Track authority responses
4. Monitor user notifications

---

## ✅ QUICK CHECKLIST

### Before Sending Alert:
- [ ] Verify information accuracy
- [ ] Choose appropriate severity
- [ ] Include clear safety instructions
- [ ] Add emergency contact numbers
- [ ] Select target audience
- [ ] Review message content

### After Sending Alert:
- [ ] Monitor delivery status
- [ ] Check user responses
- [ ] Update alert if needed
- [ ] Escalate to authorities if required
- [ ] Follow up with additional info

---

## 🎯 BEST PRACTICES

### Message Guidelines:
1. **Be Urgent** - Use clear, direct language
2. **Be Specific** - Exact locations and times
3. **Be Actionable** - Tell people what to do
4. **Be Helpful** - Include emergency contacts
5. **Be Accurate** - Verify all information

### Timing:
- **Critical alerts:** Send immediately
- **High alerts:** Send within 1 hour
- **Medium alerts:** Send within 4 hours
- **Low alerts:** Send during business hours

### Follow-up:
- Update alerts with new information
- Send all-clear when situation resolved
- Provide additional resources
- Monitor community response

---

## 📞 EMERGENCY CONTACTS

### Key Authorities:
- **ZEMA:** Environmental emergencies
- **LCC:** Municipal waste issues
- **MOH:** Health emergencies
- **Emergency Services:** 999

### System Support:
- Check documentation files
- Review notification system
- Contact development team

---

## 🎉 YOU'RE READY!

Your Emergency Alert System can:
- ✅ Send cholera outbreak alerts
- ✅ Issue flooding warnings
- ✅ Alert about medical waste hazards
- ✅ Provide hygiene tips and clinic info
- ✅ Escalate priority reports to ZEMA/LCC
- ✅ Reach users via SMS, WhatsApp, and in-app
- ✅ Target specific locations
- ✅ Track delivery and engagement

**Start protecting your community now!** 🚨💚

---

**Emergency? Send an alert in 30 seconds!** ⚡🚨