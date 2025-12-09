# Landing Page Image Guide

## Where to Add Images

Your landing page now has placeholders for images. Here's where to add them:

### 1. Hero Section Image
**Location:** Hero section (right side on desktop)
**Path:** `static/images/hero-image.jpg`
**Recommended Size:** 800x600px
**Suggested Content:** 
- Zambian landscape with greenery
- Students learning about environment
- Victoria Falls or Zambezi River

### 2. Zambia Environment Image
**Location:** "What is EcoLearn?" section (first image)
**Path:** `static/images/zambia-environment.jpg`
**Recommended Size:** 1200x800px
**Suggested Content:**
- Zambian wildlife
- Natural landscapes
- Environmental conservation efforts

### 3. Community Action Image
**Location:** "Take Action" section (second image)
**Path:** `static/images/community-action.jpg`
**Recommended Size:** 1200x800px
**Suggested Content:**
- Community cleanup events
- People working together
- Recycling or waste management activities

## How to Add Images

1. Create the `static/images/` folder if it doesn't exist:
   ```
   mkdir static/images
   ```

2. Add your images to `static/images/`

3. Uncomment the image tags in the HTML file and remove the placeholder divs

4. Run `python manage.py collectstatic` to collect static files

## Current Features

✅ **Smooth Background Slider** - 3 gradient backgrounds that transition every 5 seconds
✅ **Floating Particles** - Animated elements in hero section
✅ **Scroll Animations** - Elements fade/zoom in as you scroll (AOS library)
✅ **Stats Counter** - Numbers count up when scrolled into view
✅ **Gradient Text Animation** - "Greener Future" text has animated gradient
✅ **Icon Animations** - Icons bounce on hover, leaf icon sways
✅ **Smooth Card Hovers** - Cards lift up with shadow on hover
✅ **Glassmorphism Navbar** - Navbar has blur effect on scroll
✅ **CTA Button Effects** - Call-to-action buttons have ripple glow
✅ **Mobile Responsive** - Works perfectly on all devices

## Performance Optimized

- Removed heavy 3D card transforms that caused glitching
- Removed parallax scrolling that interfered with normal scroll
- Kept smooth, professional animations that don't impact performance
- All text is readable with proper contrast

## Color Scheme

- Primary Green: #22c55e
- Light Green: #d1fae5
- Deep Green: #166534
- Gradients use variations of these colors

Enjoy your beautiful, functional landing page! 🌱
