# 📱 WHATSAPP - 5 MINUTE QUICK START

## ⚡ FASTEST WAY TO TEST

### Step 1: Join Sandbox (2 minutes)
1. Open WhatsApp on **+260970594105**
2. Send to: **+1 415 523 8886**
3. Message: `join shadow-mountain` (or your code from Twilio)
4. Wait for confirmation ✅

### Step 2: Get Credentials (1 minute)
1. Go to: https://console.twilio.com/
2. Copy **Account SID** (starts with AC...)
3. Copy **Auth Token** (click to reveal)

### Step 3: Test (2 minutes)
1. Open `test_whatsapp_final.py`
2. Replace lines 8-9 with YOUR credentials:
```python
account_sid = 'AC...'  # Your actual SID
auth_token = '...'     # Your actual token
```
3. Run:
```bash
python test_whatsapp_final.py
```
4. Check WhatsApp! 🎉

---

## ✅ CONFIRMATION

You should see:
```
✅ WhatsApp test sent successfully!
📱 Message SID: SM1234567890abcdef
📞 To: +260970594105
📲 From: +14155238886 (Sandbox)
📊 Status: queued

🎉 Check your WhatsApp now!
```

And receive on WhatsApp:
```
🚮 Marabo Waste Management: WhatsApp activated successfully! 
You can now receive waste alerts.
```

---

## 🚀 NEXT: INTEGRATE

Once test works, update `.env`:
```env
TWILIO_ACCOUNT_SID=AC...your-actual-sid...
TWILIO_AUTH_TOKEN=your-actual-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

Then restart server:
```bash
python manage.py runserver
```

---

## 💡 TROUBLESHOOTING

**Not receiving?**
- Did you join sandbox? (send `join <code>`)
- Wait 30 seconds
- Check Twilio logs: https://console.twilio.com/us1/monitor/logs/sms

**Error "Authenticate"?**
- Check Account SID and Auth Token are correct
- No spaces or quotes

**Error "Invalid phone number"?**
- Must join sandbox first!
- Phone format: `+260970594105` (with +)

---

## 🎯 READY TO USE

After successful test:
- ✅ WhatsApp works
- ✅ Can send from Python
- ✅ Ready to integrate into admin dashboard
- ✅ Users will receive real-time notifications

**Test now: `python test_whatsapp_final.py`** 🚀
