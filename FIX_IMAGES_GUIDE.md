# How to Fix Images on Landing Page

## ✅ What I Fixed

1. **Corrected image filename** - Changed `community_action.jpg` to `comunty_action.jpg` (matching your actual file)
2. **Ran collectstatic** - Collected all static files to staticfiles folder

## 📁 Your Images

Your images are located in: `static/images/`

Currently used on landing page:
- ✅ `zambia_c.jpg` - Children learning about waste segregation
- ✅ `comunty_action.jpg` - Community cleanup action

## 🔧 Steps to See Images

### 1. Restart Your Django Server
Stop your current server (Ctrl+C) and restart:
```bash
python manage.py runserver
```

### 2. Hard Refresh Your Browser
- **Windows/Linux:** Press `Ctrl + F5`
- **Mac:** Press `Cmd + Shift + R`

This clears the browser cache and loads fresh images.

### 3. Check Browser Console
If images still don't show:
- Press `F12` to open Developer Tools
- Go to "Console" tab
- Look for any 404 errors for images
- Check the "Network" tab to see if images are loading

## 🎨 Optional: Add More Images

You have these other images available:
- `bin.jpg`
- `black.jpg`
- `community.jpg`
- `kutoba.jpg`
- `ma bin.jpeg`
- `reduction.jpg`
- `segregation.jpg`

To use them, add to your HTML:
```html
<img src="{% static 'images/YOUR_IMAGE.jpg' %}" alt="Description" class="rounded-2xl shadow-2xl">
```

## ⚠️ Common Issues

### Issue: Images still not showing
**Solution:**
```bash
python manage.py collectstatic --noinput
# Then restart server and hard refresh browser
```

### Issue: 404 errors in console
**Check:**
1. Image filename matches exactly (case-sensitive)
2. Image is in `static/images/` folder
3. `{% load static %}` is at top of template

### Issue: Admin dashboard static files conflict
**Note:** You have static files in both:
- `static/` (main)
- `admin_dashboard/static/` (admin)

This is fine! Django handles this automatically. The warning you saw is normal.

## 🚀 Your Landing Page Now Has

✅ Animated gradient background slider
✅ Floating particles
✅ Scroll animations (AOS)
✅ Stats counter
✅ **Two beautiful images of Zambia**
✅ Smooth hover effects
✅ Mobile responsive

## 📸 Image Recommendations

For best results, your images should be:
- **Format:** JPG or PNG
- **Size:** 1200x800px or larger
- **Quality:** High resolution
- **Content:** Relevant to Zambian environment/community

Enjoy your beautiful landing page! 🌱🇿🇲
