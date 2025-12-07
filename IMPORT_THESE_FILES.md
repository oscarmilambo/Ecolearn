# 📥 Import These CSV Files - Quick Guide

## ✅ 8 CSV Files Created

All files are in your project root, ready to import!

### Files Created:
1. ✅ **modules.csv** - 5 Zambian waste management modules
2. ✅ **lessons.csv** - 10 Lusaka-focused lessons
3. ✅ **quizzes.csv** - 8 assessment quizzes
4. ✅ **questions.csv** - 40 questions with correct answers
5. ✅ **badges.csv** - 10 achievement badges
6. ✅ **rewards.csv** - 8 rewards (airtime, merchandise)
7. ✅ **challenges.csv** - 10 community challenges
8. ✅ **events.csv** - 6 cleanup events in Lusaka

## 🎯 Zambian Content Included

### Locations:
- Lusaka (Chibolya, Kanyama, Soweto Market)
- Kitwe & Ndola (Copperbelt)
- Real recycling centers (Chunga, Green Planet)

### Local Context:
- MTN/Airtel airtime rewards
- Compound-specific cleanups
- Nshima and local food waste
- Lusaka City Council references
- K5000 fines for illegal dumping

## 🚀 How to Import (2 minutes each)

### Server Running?
If not: `python manage.py runserver`

### Import Order (Important!):

#### 1. Modules First
```
→ Go to: http://127.0.0.1:8000/admin/elearning/module/
→ Click "Import"
→ Upload: modules.csv
→ Preview → Confirm
→ Result: 5 modules imported ✅
```

#### 2. Lessons Second
```
→ Go to: http://127.0.0.1:8000/admin/elearning/lesson/
→ Click "Import"
→ Upload: lessons.csv
→ Preview → Confirm
→ Result: 10 lessons imported ✅
```

#### 3. Quizzes Third
```
→ Go to: http://127.0.0.1:8000/admin/elearning/quiz/
→ Click "Import"
→ Upload: quizzes.csv
→ Preview → Confirm
→ Result: 8 quizzes imported ✅
```

#### 4. Questions Fourth
```
→ Go to: http://127.0.0.1:8000/admin/elearning/question/
→ Click "Import"
→ Upload: questions.csv
→ Preview → Confirm
→ Result: 40 questions imported ✅
```

#### 5. Badges
```
→ Go to: http://127.0.0.1:8000/admin/elearning/badge/
→ Click "Import"
→ Upload: badges.csv
→ Preview → Confirm
→ Result: 10 badges imported ✅
```

#### 6. Rewards
```
→ Go to: http://127.0.0.1:8000/admin/gamification/reward/
→ Click "Import"
→ Upload: rewards.csv
→ Preview → Confirm
→ Result: 8 rewards imported ✅
```

#### 7. Challenges
```
→ Go to: http://127.0.0.1:8000/admin/gamification/challenge/
→ Click "Import"
→ Upload: challenges.csv
→ Preview → Confirm
→ Result: 10 challenges imported ✅
```

#### 8. Events
```
→ Go to: http://127.0.0.1:8000/admin/community/communityevent/
→ Click "Import"
→ Upload: events.csv
→ Preview → Confirm
→ Result: 6 events imported ✅
```

## ⚠️ Important Notes

### If Import Fails:

**Missing Foreign Keys?**
- Import modules BEFORE lessons
- Import lessons BEFORE quizzes
- Import quizzes BEFORE questions

**Date Format Issues?**
- Dates are in: YYYY-MM-DD HH:MM:SS format
- Should work automatically

**Field Errors?**
- Check the preview screen
- Fix the CSV file
- Re-upload

## 🎬 For Demo

After importing all files, you'll have:
- ✅ 5 complete modules
- ✅ 10 practical lessons
- ✅ 8 quizzes with 40 questions
- ✅ 10 achievement badges
- ✅ 8 rewards (including airtime)
- ✅ 10 active challenges
- ✅ 6 upcoming events

**Total**: 91 records imported in ~15 minutes!

## 📊 Demo Impact

Show examiners:
1. **Before**: Empty admin pages
2. **Import**: Upload CSV files
3. **After**: 91 records in database
4. **Time**: 15 minutes vs. hours of manual entry

**Say**: "This demonstrates how EcoLearn can rapidly deploy content across Zambia's 116 districts"

## ✅ Verification

After importing, check:
- [ ] Modules page shows 5 modules
- [ ] Lessons page shows 10 lessons
- [ ] Quizzes page shows 8 quizzes
- [ ] Questions page shows 40 questions
- [ ] Badges page shows 10 badges
- [ ] Rewards page shows 8 rewards
- [ ] Challenges page shows 10 challenges
- [ ] Events page shows 6 events

## 🎯 Quick Test

1. Import modules.csv (2 min)
2. Check: http://127.0.0.1:8000/admin/elearning/module/
3. See 5 new modules ✅

## 📝 Sample Content Preview

### Module Example:
- "Waste Management Basics for Lusaka"
- Beginner level, 30 minutes
- 50 points reward

### Lesson Example:
- "Introduction to Waste in Lusaka"
- "Lusaka generates over 1200 tons of waste daily..."

### Challenge Example:
- "December Lusaka Cleanup"
- Community challenge, 200 points
- Target: 100 reports submitted

### Event Example:
- "Chibolya Community Cleanup"
- December 15, 2024
- 100 participants max

### Reward Example:
- "K20 MTN Airtime"
- 200 points cost
- 50 in stock

## 🚀 Ready to Import!

All files are in your project root. Start with modules.csv and work your way down the list.

**Time needed**: 15-20 minutes for all 8 files

**Result**: Fully populated demo database with realistic Zambian content!

---

**Status**: ✅ Files Ready  
**Content**: ✅ Zambian-focused  
**Format**: ✅ CSV (compatible)  
**Demo**: ✅ Ready to impress!

**Start importing now!** 🎉
