# 🏆 Community Challenges - Quick Reference Card

## ✅ Status: LIVE & RUNNING!

Your server is running at: **http://127.0.0.1:8000/**

---

## 🚀 3-Step Quick Start

### 1️⃣ Create Challenge (Admin)
```
URL: http://127.0.0.1:8000/admin/community/communitychallenge/add/

Fill in:
- Title: "Beach Cleanup Challenge"
- Description: "Help clean our beaches!"
- Challenge Type: Cleanup Challenge
- Start Date: Today
- End Date: 30 days from now
- Target Goal: 100
- Reward Points: 100
- ✓ Is active

Click SAVE
```

### 2️⃣ Join & Submit (User)
```
URL: http://127.0.0.1:8000/community/challenges/

1. Click "🎯 Join Challenge"
2. Upload before photo
3. Enter bags collected
4. Click "✅ Submit Proof"
```

### 3️⃣ Approve (Admin)
```
URL: http://127.0.0.1:8000/admin/community/challengeproof/

1. Select pending proofs
2. Action: "✅ Approve selected proofs"
3. Click Go
4. Points awarded automatically! (30 pts/bag)
```

---

## 📱 Key URLs

| Page | URL |
|------|-----|
| **Challenge List** | `/community/challenges/` |
| **Challenge Detail** | `/community/challenges/<id>/` |
| **Admin Challenges** | `/admin/community/communitychallenge/` |
| **Admin Proofs** | `/admin/community/challengeproof/` |

---

## 💰 Points Formula

```
Points = Bags Collected × 30

Example:
5 bags = 150 points
10 bags = 300 points
```

---

## 🏅 Features Checklist

- ✅ List active challenges
- ✅ One-click join
- ✅ Photo proof submission
- ✅ Admin approval
- ✅ Auto-award 30 pts/bag
- ✅ Top 15 leaderboard
- ✅ User's rank display
- ✅ WhatsApp share
- ✅ Facebook share
- ✅ Mobile-friendly
- ✅ Big buttons
- ✅ Tailwind CSS

---

## 🎯 Admin Actions

### Approve Proofs:
1. Go to Challenge Proofs admin
2. Select proofs (checkbox)
3. Action: "✅ Approve selected proofs (auto-award 30 pts/bag)"
4. Click Go
5. Done! Points awarded automatically

### Reject Proofs:
1. Select proofs
2. Action: "❌ Reject selected proofs"
3. Click Go
4. Add admin notes (optional)

---

## 📸 Photo Requirements

- **Before Photo**: Required ✅
- **After Photo**: Optional
- **Format**: JPG, PNG
- **Purpose**: Verify cleanup work

---

## 🎨 UI Features

### Challenge Cards:
- Banner image or gradient
- Progress bar
- Points badge
- Participant count
- Join button

### Detail Page:
- Full challenge info
- Submission form
- Leaderboard (top 15)
- User's rank
- Share buttons
- Submission history

---

## 🔧 Troubleshooting

### No challenges showing?
- Check "Is active" is ✓
- Verify end date is future
- Refresh page

### Can't upload photos?
- Check MEDIA_URL in settings
- Verify media folder exists
- Check file permissions

### Points not awarded?
- Use bulk approve action
- Don't just change status
- Check gamification app

---

## 📊 What Gets Tracked

- Challenge participation
- Proof submissions
- Approval status
- Points awarded
- Leaderboard rankings
- Social shares
- User contributions

---

## 🎉 Success Indicators

✅ Challenge appears in list
✅ Join button works
✅ Proof form appears after join
✅ Photos upload successfully
✅ Admin sees pending proofs
✅ Bulk approve awards points
✅ Leaderboard updates
✅ Share buttons work

---

## 💡 Pro Tips

1. **Create weekly challenges** for engagement
2. **Use banner images** for visual appeal
3. **Set realistic goals** (50-100 bags)
4. **Approve within 24 hours** to keep momentum
5. **Celebrate top contributors** publicly

---

## 📞 Need Help?

See detailed guides:
- `TEST_CHALLENGES_NOW.md` - Step-by-step testing
- `CHALLENGES_READY.md` - Quick start guide
- `COMMUNITY_CHALLENGES_GUIDE.md` - Full documentation
- `CHALLENGES_COMPLETE_SUMMARY.md` - Technical details

---

## 🎊 You're Ready!

Everything is working. Just:
1. Create your first challenge
2. Test the workflow
3. Start engaging your community!

**Server running at: http://127.0.0.1:8000/** ✅

---

**🌍 Built for EcoLearn/Marabo - Let's make a difference!** 🚀
