# Image Not Showing - Complete Fix Guide

## ✅ What I Just Fixed

1. **Added cache-busting parameter** - `?v=2` to force browser to reload
2. **Fixed URLs configuration** - Removed incorrect static files serving in DEBUG mode

## 🔧 Steps to Fix Right Now

### 1. Stop Your Server
Press `Ctrl+C` in your terminal

### 2. Restart Server
```bash
python manage.py runserver
```

### 3. Clear Browser Cache Completely
Choose ONE method:

**Method A: Hard Refresh (Easiest)**
- Press `Ctrl+Shift+Delete`
- Select "Cached images and files"
- Click "Clear data"
- Then press `Ctrl+F5` on your page

**Method B: Incognito/Private Window**
- Open a new Incognito/Private window
- Go to `http://127.0.0.1:8000/`
- Images should show

**Method C: Clear Browser Cache via DevTools**
- Press `F12`
- Right-click the refresh button
- Select "Empty Cache and Hard Reload"

### 4. Verify Image is Loading
1. Press `F12` (Developer Tools)
2. Go to "Network" tab
3. Refresh page (`Ctrl+F5`)
4. Look for `ghetto.jpg` in the list
5. Click on it - should show:
   - **Status: 200** ✅ (Success)
   - **Size: ~1.7 MB**
   - **Type: image/jpeg**

If you see **404** ❌, continue to next section.

## 🐛 If Image Still Not Showing

### Check 1: Verify File Exists
```bash
dir static\images\ghetto.jpg
```
Should show the file with size ~1.7 MB

### Check 2: Check Django is Serving Static Files
Visit directly in browser:
```
http://127.0.0.1:8000/static/images/ghetto.jpg
```

If this shows the image ✅ but landing page doesn't, it's a template issue.
If this shows 404 ❌, it's a Django configuration issue.

### Check 3: Verify Template Syntax
Open `accounts/templates/accounts/landing_page.html` and check:

1. Top of file has: `{% load static %}`
2. Image tag has: `{% static 'images/ghetto.jpg' %}`

### Check 4: Check Settings
Open `ecolearn/settings.py` and verify:

```python
DEBUG = True  # Should be True for development

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

## 🎯 Quick Test

Run this command to test everything:
```bash
python test_image_url.py
```

Should show:
- ✅ File exists
- ✅ Generated URL: /static/images/ghetto.jpg

## 🔄 Alternative: Use a Different Image

If `ghetto.jpg` still won't show, try another image:

1. Open `accounts/templates/accounts/landing_page.html`
2. Find: `{% static 'images/ghetto.jpg' %}`
3. Change to: `{% static 'images/community.jpg' %}`
4. Save and refresh

## 📱 Test on Different Browser

Sometimes one browser caches aggressively:
- Try Chrome if using Edge
- Try Firefox if using Chrome
- Try Edge if using Firefox

## 🚀 Nuclear Option: Force Complete Refresh

If nothing works:

1. **Delete browser cache folder** (varies by browser)
2. **Restart Django server**
3. **Restart browser completely**
4. **Visit page in Incognito mode**

## ✨ Expected Result

You should see:
- **First image:** Children learning (zambia_c.jpg)
- **Second image:** Community scene (ghetto.jpg)
- Both images: 256px height on mobile, 320px on desktop
- Rounded corners with shadow

## 📞 Still Not Working?

Check browser console (F12 → Console tab) for errors:
- Red errors about static files?
- 404 errors for images?
- MIME type errors?

Copy the error message and we can troubleshoot further!

---

**Current Status:**
- ✅ File exists: `static/images/ghetto.jpg` (1.7 MB)
- ✅ Django configured correctly
- ✅ Template syntax correct
- ✅ Cache-busting added (?v=2)
- ✅ URLs fixed

**Next:** Just restart server and hard refresh browser!
