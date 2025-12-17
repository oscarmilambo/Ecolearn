# Africa's Talking SMS Setup Guide for EcoLearn

## Quick Setup for Demo (5 minutes)

### Step 1: Get Africa's Talking Account
1. Go to https://africastalking.com/
2. Click "Get Started" or "Sign Up"
3. Create account with your email
4. Verify your email address

### Step 2: Get API Credentials
1. Login to your Africa's Talking dashboard
2. Go to "Settings" → "API Keys"
3. Copy your **Username** (usually your email or custom name)
4. Copy your **API Key** (long string of characters)

### Step 3: Configure EcoLearn
1. Open your `.env` file
2. Replace the Africa's Talking settings:
```env
# Africa's Talking Configuration
AFRICAS_TALKING_USERNAME=your_username_here
AFRICAS_TALKING_API_KEY=your_api_key_here
```

### Step 4: Install Required Package
```bash
pip install africastalking
```

### Step 5: Test the Integration
```bash
python demo_sms_presentation.py
```

## For Sandbox Testing (Free)

If you want to test without spending money:

1. In your Africa's Talking dashboard, go to "Sandbox"
2. Use sandbox credentials:
   - Username: `sandbox`
   - API Key: (your sandbox API key)
3. Add test phone numbers in sandbox settings
4. Sandbox messages won't be delivered to real phones but will show success

## For Live Demo (Small Cost)

For your presentation with real SMS delivery:

1. Add credit to your Africa's Talking account
   - Go to "Billing" → "Add Credit"
   - Minimum: $1 USD (enough for 100+ SMS in Zambia)
2. Use production credentials (not sandbox)
3. SMS will be delivered to real phone numbers

## SMS Costs in Zambia
- **Airtel Zambia**: ~$0.01 USD per SMS
- **MTN Zambia**: ~$0.01 USD per SMS  
- **Zamtel**: ~$0.01 USD per SMS

**Total demo cost**: ~$0.05 USD for 5 test messages

## Demo Script Features

The `demo_sms_presentation.py` script includes:

✅ **3 Live Demo Scenarios:**
1. Community cleanup campaign (bulk SMS)
2. Recycling education campaign (bulk SMS)  
3. Individual achievement notification (single SMS)

✅ **Real-time Features:**
- Live SMS delivery during presentation
- Message delivery confirmation
- Cost tracking per message
- Error handling and reporting

✅ **Professional Presentation:**
- Clear scenario descriptions
- Pause between demos for audience engagement
- Statistics summary at the end
- Next steps for production deployment

## Running the Demo

### Option 1: Full Presentation Demo
```bash
python demo_sms_presentation.py
# Choose option 1
```

### Option 2: Quick Test
```bash
python demo_sms_presentation.py  
# Choose option 2
```

### Option 3: Custom Integration
```python
from africas_talking_integration import africas_talking_service

# Send single SMS
result = africas_talking_service.send_sms("+260970594105", "Test message")

# Send bulk SMS
phones = ["+260970594105", "+260977123456"]
result = africas_talking_service.send_bulk_sms(phones, "Bulk message")
```

## Integration with Existing Notification System

Your EcoLearn platform already has Twilio notifications. The Africa's Talking integration:

1. **Replaces Twilio** for SMS (more cost-effective in Africa)
2. **Keeps existing notification logic** (same triggers, same user preferences)
3. **Adds bulk campaign features** for waste management education
4. **Maintains all current functionality** (challenge notifications, achievements, etc.)

## Switching from Twilio to Africa's Talking

To use Africa's Talking as your primary SMS provider:

1. Update `community/notifications.py`:
```python
from africas_talking_integration import africas_talking_service

# Replace Twilio SMS calls with:
result = africas_talking_service.send_sms(phone_number, message)
```

2. Keep Twilio as backup for WhatsApp (until Africa's Talking WhatsApp is configured)

## Production Deployment

For production use:

1. **Get production API key** (not sandbox)
2. **Configure sender ID** for branded SMS (e.g., "EcoLearn")
3. **Set up webhook** for delivery reports
4. **Add WhatsApp Business API** (separate Africa's Talking product)
5. **Implement SMS templates** for different campaign types

## Troubleshooting

### Common Issues:

1. **"SMS service not initialized"**
   - Check API key in `.env` file
   - Ensure `africastalking` package is installed

2. **"Invalid phone number"**
   - Use international format: `+260970594105`
   - Remove spaces and special characters

3. **"Insufficient balance"**
   - Add credit to your Africa's Talking account
   - Check billing section in dashboard

4. **"Message not delivered"**
   - Check phone number is active
   - Verify network coverage
   - Check delivery reports in dashboard

## Support

- **Africa's Talking Docs**: https://developers.africastalking.com/
- **Support Email**: support@africastalking.com
- **Community Forum**: https://community.africastalking.com/

---

**Ready for your presentation!** 🚀

The demo will showcase real SMS delivery to demonstrate how your waste management learning platform can engage communities through mobile notifications.