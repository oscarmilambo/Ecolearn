# 🧪 TEST NOTIFICATIONS NOW!

## ✅ 3 WAYS TO TEST

### Method 1: Django Management Command (EASIEST)
```bash
python manage.py test_notifications
```

**What it does:**
- Finds user with phone number automatically
- Sends all 4 PRO notification types
- Shows success/failure for each
- Color-coded output

**Test specific phone:**
```bash
python manage.py test_notifications --phone +260971234567
```

---

### Method 2: Simple Python Script
```bash
python test_notifications_simple.py
```

**What it does:**
- Same as Method 1
- Standalone script (no Django command needed)
- Works if management commands have issues

---

### Method 3: Manual Test in Django Shell
```bash
python manage.py shell
```

Then run:
```python
from community.notifications import notification_service
from accounts.models import CustomUser

# Get test user
user = CustomUser.objects.filter(phone_number__isnull=False).first()
print(f"Testing with: {user.username} - {user.phone_number}")

# Test SMS
result = notification_service.send_sms(
    str(user.phone_number), 
    "🎉 Test from EcoLearn!"
)
print(f"SMS: {result}")

# Test WhatsApp
result = notification_service.send_whatsapp(
    str(user.phone_number), 
    "🎉 Test from EcoLearn!"
)
print(f"WhatsApp: {result}")
```

---

## 📱 WHAT YOU'LL RECEIVE

After running any test method, check your phone for **8 messages**:

### SMS Messages (4):
1. "🎉 John Banda, welcome to Clean Kalingalinga Challenge! Top 3 win airtime. Submit proof now!"
2. "✅ APPROVED! You earned 50 points (5 bags). You are now #3 in Clean Kalingalinga Challenge! Keep cleaning Zambia!"
3. "🚨 NEW ILLEGAL DUMP in Kalingalinga Market! 3 photos attached. Act now!"
4. "✅ Well done John Banda! You finished 'Waste Management Basics'. +20 points added!"

### WhatsApp Messages (4):
Same as SMS (identical format for consistency)

---

## ✅ EXPECTED OUTPUT

```
============================================================
PRO NOTIFICATION TEST
============================================================

✅ Test User: john_banda
📱 Phone: +260971234567

============================================================
TEST 1: JOIN CHALLENGE
============================================================

📱 Message: 🎉 John Banda, welcome to Clean Kalingalinga Challenge! Top 3 win airtime. Submit proof now!
✅ SMS sent! SID: SM1234567890abcdef
✅ WhatsApp sent! SID: SM0987654321fedcba

============================================================
TEST 2: PROOF APPROVED
============================================================

📱 Message: ✅ APPROVED! You earned 50 points (5 bags). You are now #3 in Clean Kalingalinga Challenge! Keep cleaning Zambia!
✅ SMS sent! SID: SM1234567890abcdef
✅ WhatsApp sent! SID: SM0987654321fedcba

============================================================
TEST 3: NEW ILLEGAL DUMP
============================================================

📱 Message: 🚨 NEW ILLEGAL DUMP in Kalingalinga Market! 3 photos attached. Act now!
✅ SMS sent! SID: SM1234567890abcdef
✅ WhatsApp sent! SID: SM0987654321fedcba

============================================================
TEST 4: LESSON COMPLETED
============================================================

📱 Message: ✅ Well done John Banda! You finished 'Waste Management Basics'. +20 points added!
✅ SMS sent! SID: SM1234567890abcdef
✅ WhatsApp sent! SID: SM0987654321fedcba

============================================================
✅ ALL TESTS COMPLETED!
============================================================

Check your phone for 8 messages (4 SMS + 4 WhatsApp)
```

---

## 🔧 TROUBLESHOOTING

### ❌ "No user with phone number found"

**Solution:**
```bash
# Add phone number to a user
python manage.py shell
>>> from accounts.models import CustomUser
>>> user = CustomUser.objects.first()
>>> user.phone_number = '+260971234567'
>>> user.save()
>>> exit()
```

Then run test again.

---

### ❌ "SMS failed: Unable to create record"

**Possible causes:**
1. **Invalid Twilio credentials**
   ```bash
   python check_credentials.py
   ```

2. **Wrong phone number format**
   - Must include country code: `+260971234567`
   - Not: `0971234567` or `971234567`

3. **Insufficient Twilio balance**
   - Login to: https://console.twilio.com
   - Check account balance
   - Add credit if needed

4. **Invalid Twilio phone number**
   - Check `.env` file
   - Verify `TWILIO_PHONE_NUMBER` is correct

---

### ❌ "WhatsApp failed: ..."

**Possible causes:**
1. **WhatsApp sandbox not configured**
   - Twilio WhatsApp requires sandbox setup
   - Or use approved WhatsApp Business number

2. **Wrong WhatsApp number format**
   - Check `.env` file
   - Should be: `TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886`

3. **Test with SMS first**
   - If SMS works but WhatsApp doesn't
   - Issue is WhatsApp-specific (sandbox/approval)

---

### ❌ Messages sent but not received

**Check:**
1. **Phone number is correct**
   - Verify in user profile
   - Must match your actual phone

2. **Twilio delivery status**
   - Login to: https://console.twilio.com
   - Go to: Messaging → Logs
   - Check delivery status

3. **Network/carrier issues**
   - Try different phone number
   - Check spam/blocked messages

4. **Wait a few minutes**
   - Sometimes delivery is delayed
   - Check Twilio logs for status

---

## 🎯 QUICK FIXES

### Fix 1: Update Phone Number
```bash
python manage.py shell
>>> from accounts.models import CustomUser
>>> user = CustomUser.objects.get(username='your_username')
>>> user.phone_number = '+260971234567'
>>> user.save()
```

### Fix 2: Check Twilio Credentials
```bash
python check_credentials.py
```

### Fix 3: Test Single Message
```bash
python manage.py shell
>>> from community.notifications import notification_service
>>> result = notification_service.send_sms('+260971234567', 'Test')
>>> print(result)
```

### Fix 4: Verify .env File
```bash
# Check these variables exist:
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
```

---

## 🚀 READY TO TEST?

Run this now:
```bash
python manage.py test_notifications
```

**Expected:** 8 messages on your phone in 30 seconds! 📱✨

---

## 📚 MORE HELP

- **Full Guide:** `PRO_NOTIFICATIONS_COMPLETE.md`
- **Messages:** `NOTIFICATION_MESSAGES_REFERENCE.md`
- **Testing:** `START_TESTING_NOTIFICATIONS.md`

---

## ✅ SUCCESS CHECKLIST

After testing, verify:
- [ ] Received 8 messages total
- [ ] 4 SMS messages arrived
- [ ] 4 WhatsApp messages arrived
- [ ] All messages are professional and clear
- [ ] Messages arrived within 1 minute
- [ ] No error messages in console
- [ ] Twilio console shows "Delivered"

---

## 🎉 DONE!

If all 8 messages arrived, your PRO notification system is working perfectly! 

Now test the real user flows:
1. Join a challenge → Get welcome message
2. Submit proof → Admin approves → Get approval message
3. Report illegal dump → Admins get alert
4. Complete module → Get completion message

All automatic! 🚀📱✨
