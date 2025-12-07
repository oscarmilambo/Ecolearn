# 📍 Where to Find Everything - Complete Guide

## 🎯 How to See Your New Features

### Step 1: Run Migrations First! (CRITICAL)
```bash
python manage.py makemigrations accounts community
python manage.py migrate
python manage.py runserver
```

---

## 🔗 Direct URLs to Access Features

### Gamification Features (Rewards Dropdown):
1. **My Points Dashboard**
   - URL: http://127.0.0.1:8000/rewards/points/
   - Shows: Points balance, transactions, available rewards
   
2. **Rewards Catalog**
   - URL: http://127.0.0.1:8000/rewards/rewards/
   - Shows: All rewards you can redeem
   
3. **Leaderboard**
   - URL: http://127.0.0.1:8000/rewards/leaderboard/
   - Shows: Top users, your rank, community rankings
   
4. **My Badges**
   - URL: http://127.0.0.1:8000/rewards/badges/
   - Shows: Earned and locked badges

### Community Features:
5. **Events List**
   - URL: http://127.0.0.1:8000/community/events/
   - Shows: Upcoming and past community events
   
6. **Success Stories**
   - URL: http://127.0.0.1:8000/community/stories/
   - Shows: All approved success stories
   - Has: Share buttons on each story
   
7. **Create Success Story**
   - URL: http://127.0.0.1:8000/community/stories/create/
   - Form to submit your own story

### New Features (Just Added):
8. **Notification Preferences** ⭐ NEW
   - URL: http://127.0.0.1:8000/accounts/notifications/preferences/
   - Control: SMS, WhatsApp, Email notifications
   - Settings: Frequency, quiet hours, notification types

### AI Assistant:
9. **AI Chat**
   - URL: http://127.0.0.1:8000/ai-assistant/
   - Chat with AI about platform features

---

## 🧭 Navigation Guide

### From Main Navbar:

#### 1. **Rewards Dropdown** (Top Right)
Click "Rewards" → You'll see:
- My Points
- Redeem Rewards
- Leaderboard
- My Badges

#### 2. **Community Dropdown**
Click "Community" → You'll see:
- Forum
- Events ← Click here for events
- Challenges
- Success Stories ← Click here for stories
- Health Alerts

#### 3. **AI Assistant**
Click "AI Assistant" → Opens chat interface

### From User Profile Dropdown:

Click your avatar (top right) → You'll see:
- Learning Modules
- My Progress
- My Certificates
- Payment History
- **Notifications** ⭐ NEW ← Click here for notification settings
- Profile Settings
- Logout

---

## 📱 What Each Page Shows

### 1. My Points Dashboard (`/rewards/points/`)
```
┌─────────────────────────────────────┐
│ Total Points: 1,250                 │
│ Available: 850  |  Redeemed: 400    │
├─────────────────────────────────────┤
│ Recent Transactions:                │
│ ✅ +100 pts - Completed Module      │
│ ✅ +50 pts - Reported Dumping       │
│ ❌ -200 pts - Redeemed T-Shirt      │
├─────────────────────────────────────┤
│ Available Rewards:                  │
│ 🎁 EcoLearn T-Shirt (200 pts)      │
│ 🎁 Water Bottle (150 pts)          │
└─────────────────────────────────────┘
```

### 2. Rewards Catalog (`/rewards/rewards/`)
```
┌──────────────────────────────────────┐
│ Your Points: 850                     │
├──────────────────────────────────────┤
│ [Image] EcoLearn T-Shirt             │
│ 200 points | 15 left                 │
│ [Redeem Now]                         │
├──────────────────────────────────────┤
│ [Image] Water Bottle                 │
│ 150 points | 30 left                 │
│ [Redeem Now]                         │
└──────────────────────────────────────┘
```

### 3. Leaderboard (`/rewards/leaderboard/`)
```
┌──────────────────────────────────────┐
│ Your Rank: #12  |  Your Points: 850  │
├──────────────────────────────────────┤
│ Top Users:                           │
│ 🥇 #1 John Doe - 2,500 pts          │
│ 🥈 #2 Jane Smith - 2,100 pts        │
│ 🥉 #3 Bob Wilson - 1,800 pts        │
│ ...                                  │
│ #12 You - 850 pts ← Your position   │
└──────────────────────────────────────┘
```

### 4. My Badges (`/rewards/badges/`)
```
┌──────────────────────────────────────┐
│ Badges Earned: 5  |  Available: 10   │
├──────────────────────────────────────┤
│ Earned Badges:                       │
│ 🏅 First Report                      │
│ 🏅 Module Master                     │
│ 🏅 Community Helper                  │
├──────────────────────────────────────┤
│ Locked Badges:                       │
│ 🔒 100 Points (Need 50 more)        │
│ 🔒 Event Organizer (Need 3 events)  │
└──────────────────────────────────────┘
```

### 5. Events List (`/community/events/`)
```
┌──────────────────────────────────────┐
│ Upcoming Events:                     │
│                                      │
│ [Image] Community Cleanup - Matero   │
│ 📅 Nov 25, 2025 | 👥 45 joined     │
│ [View Details]                       │
│                                      │
│ [Image] Recycling Workshop           │
│ 📅 Dec 1, 2025 | 👥 23 joined      │
│ [View Details]                       │
└──────────────────────────────────────┘
```

### 6. Success Stories (`/community/stories/`)
```
┌──────────────────────────────────────┐
│ Filter: [All] [Cleanup] [Recycling]  │
├──────────────────────────────────────┤
│ [Image] We Cleaned 500kg of Plastic  │
│ By: John Doe | Nov 20, 2025          │
│ Impact: 500kg collected              │
│ [Read Full Story]                    │
│                                      │
│ Share: [WhatsApp] [Facebook] [Twitter]│
└──────────────────────────────────────┘
```

### 7. Notification Preferences (`/accounts/notifications/preferences/`)
```
┌──────────────────────────────────────┐
│ Notification Channels:               │
│ 📱 SMS Notifications      [ON/OFF]  │
│ 💬 WhatsApp Notifications [ON/OFF]  │
│ 📧 Email Notifications    [ON/OFF]  │
├──────────────────────────────────────┤
│ Notification Types:                  │
│ Event Reminders          [ON/OFF]   │
│ Challenge Updates        [ON/OFF]   │
│ Forum Replies            [ON/OFF]   │
│ Reward Updates           [ON/OFF]   │
│ Community News           [ON/OFF]   │
├──────────────────────────────────────┤
│ Frequency:                           │
│ ○ Instant                            │
│ ○ Daily Digest                       │
│ ○ Weekly Summary                     │
├──────────────────────────────────────┤
│ [Send Test] [Save Preferences]       │
└──────────────────────────────────────┘
```

---

## 🎨 Visual Guide - Where to Click

### Main Navigation Bar (Top):
```
┌────────────────────────────────────────────────────────────┐
│ 🍃 EcoLearn  [Learning▼] [Community▼] [Groups] [Report]   │
│              [🤖 AI Assistant] [Rewards▼] [👤 Profile▼]    │
└────────────────────────────────────────────────────────────┘
                                              ↑
                                    Click here for Rewards!
```

### Rewards Dropdown:
```
┌─────────────────────┐
│ 💰 My Points        │ ← Points dashboard
│ 🎁 Redeem Rewards   │ ← Rewards catalog
│ 🏆 Leaderboard      │ ← Rankings
│ 🏅 My Badges        │ ← Badge collection
└─────────────────────┘
```

### Profile Dropdown:
```
┌─────────────────────┐
│ 📚 Learning Modules │
│ 📊 My Progress      │
│ 🎓 My Certificates  │
│ 💳 Payment History  │
│ 🔔 Notifications    │ ← NEW! Click here
│ ⚙️ Profile Settings │
│ 🚪 Logout           │
└─────────────────────┘
```

---

## ✅ Quick Test Checklist

After running migrations, test these:

1. ✅ Click "Rewards" → "My Points" - Should show points dashboard
2. ✅ Click "Rewards" → "Leaderboard" - Should show rankings
3. ✅ Click "Community" → "Events" - Should show events list
4. ✅ Click "Community" → "Success Stories" - Should show stories
5. ✅ Click Profile → "Notifications" - Should show preferences page
6. ✅ Click "AI Assistant" - Should open chat interface

---

## 🐛 If Something Doesn't Work

### Error: "Template does not exist"
**Solution:** The template was created, restart server
```bash
python manage.py runserver
```

### Error: "No such table"
**Solution:** Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Error: "Page not found (404)"
**Solution:** Check if URL is correct, restart server

### Can't see "Notifications" in profile menu
**Solution:** Clear browser cache or hard refresh (Ctrl+F5)

---

## 📊 What Data You'll See

### If Database is Empty:
- Points: 0
- Badges: None earned
- Leaderboard: Empty or just you
- Events: "No events yet"
- Stories: "No stories yet"

### To Add Test Data:
1. Go to Django Admin: http://127.0.0.1:8000/admin/
2. Add some rewards, badges, events
3. Or use the platform to earn points naturally

---

## 🎯 Summary

**Everything is accessible from:**
1. **Rewards dropdown** (top navbar) - Points, Rewards, Leaderboard, Badges
2. **Community dropdown** (top navbar) - Events, Stories
3. **Profile dropdown** (top right) - Notification Preferences
4. **AI Assistant button** (top navbar) - Chat interface

**Just remember to:**
1. ✅ Run migrations first
2. ✅ Restart server
3. ✅ Login to your account
4. ✅ Click around and explore!

---

**Need help?** Check the error messages and refer to the troubleshooting section above.