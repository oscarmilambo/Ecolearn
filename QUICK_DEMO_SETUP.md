# 🚀 QUICK DEMO SETUP (5 Minutes)

## For Your Presentation Today

### Step 1: Get Africa's Talking API Key (2 minutes)

1. **Go to**: https://africastalking.com/
2. **Click**: "Get Started" (top right)
3. **Sign up** with your email
4. **Verify** your email (check inbox)
5. **Login** to dashboard
6. **Go to**: Settings → API Keys
7. **Copy**:
   - Username (usually your email)
   - API Key (long string)

### Step 2: Configure EcoLearn (1 minute)

1. **Open** your `.env` file
2. **Find** these lines:
```env
# Africa's Talking Configuration (Primary SMS Provider)
AFRICAS_TALKING_USERNAME=sandbox
AFRICAS_TALKING_API_KEY=your_africas_talking_api_key_here
```

3. **Replace** with your credentials:
```env
AFRICAS_TALKING_USERNAME=your_actual_username
AFRICAS_TALKING_API_KEY=your_actual_api_key
```

### Step 3: Add Credit (1 minute)

1. **In dashboard**: Go to "Billing" → "Add Credit"
2. **Add**: $1 USD (enough for 100+ SMS in Zambia)
3. **Payment**: Use card or mobile money

### Step 4: Test & Demo (1 minute)

```bash
python setup_demo_presentation.py
```

**Choose option 1** for full presentation demo!

---

## Demo Features Ready

✅ **Live SMS delivery** during presentation  
✅ **3 waste management scenarios**:
   - Community cleanup campaigns
   - Individual user notifications  
   - Emergency environmental alerts

✅ **Real-time statistics** and cost tracking  
✅ **Professional presentation flow** with pauses  
✅ **Audience engagement** opportunities

---

## If You Don't Have Time for Full Setup

**Use Sandbox Mode** (free, no real SMS):

1. Keep these settings in `.env`:
```env
AFRICAS_TALKING_USERNAME=sandbox
AFRICAS_TALKING_API_KEY=your_sandbox_api_key
```

2. **Get sandbox API key** from dashboard → Sandbox
3. **Demo will show** success messages but no real SMS
4. **Perfect for** testing the integration logic

---

## Demo Script Commands

```bash
# Full presentation demo
python demo_sms_presentation.py

# Quick test
python setup_demo_presentation.py

# Enhanced notifications (with Twilio backup)
python enhanced_notifications.py
```

---

## What Your Audience Will See

1. **Live SMS delivery** to real phone numbers
2. **Message tracking** with delivery confirmation
3. **Cost breakdown** per message and provider
4. **Bulk campaign** capabilities for community engagement
5. **Individual notifications** for user achievements
6. **Emergency alert** system for health/safety

---

## Key Talking Points

- **Cost-effective**: ~$0.01 per SMS in Zambia vs $0.075 with Twilio
- **Local coverage**: Better delivery rates in Africa
- **Bulk campaigns**: Engage entire communities instantly
- **Real-time**: Immediate delivery and confirmation
- **Scalable**: Handle thousands of users
- **Integrated**: Works with existing Django notification system

---

## Backup Plan

If Africa's Talking doesn't work during demo:

1. **Use existing Twilio** integration (already working)
2. **Show the code** and explain the benefits
3. **Demonstrate** with test phone numbers
4. **Explain** the cost savings and African focus

---

**You're ready! 🎉**

The demo will showcase how your waste management learning platform can effectively engage Zambian communities through mobile notifications.