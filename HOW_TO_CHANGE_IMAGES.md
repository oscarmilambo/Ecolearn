# How to Change Images on Landing Page

## ✅ Your Current Images

1. **First Image (Left side):** `zambia_c.jpg` - Children learning
2. **Second Image (Right side):** `ghetto.jpg` - Community action

## 🔄 Steps to Change Any Image

### Step 1: Add Your Image to Static Folder
```
static/images/YOUR_IMAGE_NAME.jpg
```

### Step 2: Update the HTML
Find the image tag in `accounts/templates/accounts/landing_page.html`:

```html
<img src="{% static 'images/OLD_IMAGE.jpg' %}" 
     alt="Description" 
     class="rounded-2xl shadow-2xl w-full h-64 md:h-80 object-cover">
```

Change to:
```html
<img src="{% static 'images/YOUR_IMAGE_NAME.jpg' %}" 
     alt="Your description" 
     class="rounded-2xl shadow-2xl w-full h-64 md:h-80 object-cover">
```

### Step 3: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 4: Restart Server
Stop server (Ctrl+C) and restart:
```bash
python manage.py runserver
```

### Step 5: Hard Refresh Browser
- **Windows:** Ctrl + F5
- **Mac:** Cmd + Shift + R

## 📸 Available Images in Your Static Folder

You have these images ready to use:
- ✅ `ghetto.jpg` (currently used)
- ✅ `zambia_c.jpg` (currently used)
- `bin.jpg`
- `black.jpg`
- `community.jpg`
- `kutoba.jpg`
- `ma bin.jpeg`
- `reduction.jpg`
- `segregation.jpg`

## 🎨 Image Specifications

For best results:
- **Format:** JPG or PNG
- **Size:** 1200x800px or larger
- **Aspect Ratio:** 3:2 or 4:3
- **File Size:** Under 500KB for fast loading

## ⚡ Quick Change Example

Want to use `community.jpg` instead of `ghetto.jpg`?

1. Open `accounts/templates/accounts/landing_page.html`
2. Find: `{% static 'images/ghetto.jpg' %}`
3. Change to: `{% static 'images/community.jpg' %}`
4. Run: `python manage.py collectstatic --noinput`
5. Restart server and refresh browser

## 🐛 Troubleshooting

### Image not showing?
1. Check filename matches exactly (case-sensitive)
2. Run collectstatic again
3. Clear browser cache (Ctrl+F5)
4. Check browser console (F12) for 404 errors

### Image too large/small?
Adjust the height classes:
- `h-64` = 256px
- `h-80` = 320px
- `h-96` = 384px

Current setting: `h-64 md:h-80` (256px mobile, 320px desktop)

That's it! Your images should now show perfectly. 🎉
