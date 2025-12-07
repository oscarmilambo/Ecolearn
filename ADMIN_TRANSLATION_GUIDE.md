# Django Admin Translation Guide for EcoLearn

## Table of Contents
1. [Overview](#overview)
2. [Accessing the Admin Panel](#accessing-the-admin-panel)
3. [Adding Module Translations](#adding-module-translations)
4. [Adding Lesson Translations with Media](#adding-lesson-translations-with-media)
5. [Adding Quiz Translations](#adding-quiz-translations)
6. [Translation Status Indicators](#translation-status-indicators)
7. [Best Practices](#best-practices)

---

## Overview

The EcoLearn admin panel has been enhanced to make adding translations easy and intuitive. All content can be translated into:
- **English (EN)** - Default/Required
- **Bemba (BEM)** - Chibemba
- **Nyanja (NY)** - Chinyanja

### Key Features:
- ✅ Organized sections with emoji icons
- ✅ Collapsible translation fields
- ✅ Visual status indicators
- ✅ Separate media upload for each language
- ✅ Search across all languages
- ✅ Inline editing

---

## Accessing the Admin Panel

1. **Start the development server**:
   ```bash
   python manage.py runserver
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:8000/admin/
   ```

3. **Log in** with your superuser credentials

4. **Navigate to** `ELEARNING` section in the admin panel

---

## Adding Module Translations

### Step 1: Create or Edit a Module

1. Click on **"Modules"** under ELEARNING
2. Click **"Add Module"** or select an existing module
3. You'll see organized sections:

### Step 2: Fill in English Content (Required)

**Section: 📝 English Content (Required)**

This section contains:
- **Title**: Module title in English (required)
- **Slug**: Auto-generated URL-friendly name
- **Description**: Full description in English
- **Category**: Select category
- **Tags**: Select relevant tags
- **Thumbnail**: Upload module image
- **Video URL**: Optional intro video

**Example:**
```
Title: Waste Management Basics
Slug: waste-management-basics
Description: Learn the fundamentals of proper waste management...
```

### Step 3: Add Bemba Translation

**Section: 🇿🇲 Bemba Translation (Chibemba)** - Click to expand

- **Title (Bemba)**: `Ifya Ukutungulula Ubulongwe`
- **Description (Bemba)**: `Sambilila ifya mfumu fya ukutungulula ubulongwe...`

**Tips:**
- This section is collapsible to keep the form clean
- Leave blank if translation not yet available
- You can add it later

### Step 4: Add Nyanja Translation

**Section: 🇿🇲 Nyanja Translation (Chinyanja)** - Click to expand

- **Title (Nyanja)**: `Zoyambira za Kusamalira Zinyalala`
- **Description (Nyanja)**: `Phunzirani zofunikira za kusamalira zinyalala...`

### Step 5: Configure Module Settings

**Section: ⚙️ Module Settings**

- Difficulty level
- Duration in minutes
- Points reward
- Prerequisites
- Waste stream type
- External tour URL

### Step 6: Set Publishing Options

**Section: 🔒 Access & Publishing**

- ☑ Is Premium
- ☑ Is Featured
- ☑ Is Published
- ☑ Is Active

### Step 7: Save

Click **"Save"** or **"Save and continue editing"**

### Step 8: Check Translation Status

Back in the module list, you'll see:
- **Translation Status Column**: Shows `✅ BEM ✅ NY` if both complete
- **Partial**: Shows `⚠️ BEM` if only title translated
- **None**: Shows `❌ No translations` if no translations added

---

## Adding Lesson Translations with Media

Lessons support both text translations AND language-specific media files (video/audio).

### Step 1: Create or Edit a Lesson

1. Click on **"Lessons"** under ELEARNING
2. Click **"Add Lesson"** or select existing
3. You'll see organized sections:

### Step 2: Set Lesson Placement

**Section: 📍 Lesson Placement**

- **Module**: Select parent module
- **Order**: Lesson number (1, 2, 3...)
- ☑ Is Published
- ☑ Is Required
- ☑ Is Preview (free preview for non-enrolled users)

### Step 3: Fill English Content

**Section: 📝 English Content (Required)**

- **Title**: `Introduction to Recycling`
- **Slug**: `introduction-to-recycling`
- **Content Type**: Choose from:
  - Video
  - Audio
  - Text
  - Interactive
- **Duration (minutes)**: `15`
- **Content**: Full lesson text in English (HTML supported)

### Step 4: Upload English Media Files

**Section: 🎬 English Media Files** - Click to expand

If your lesson is video or audio type:
- **Video File**: Upload English video (MP4 recommended)
- **Audio File**: Upload English audio (MP3 recommended)

**File naming suggestion:**
- `lesson-1-intro-recycling-en.mp4`
- `lesson-1-intro-recycling-en.mp3`

### Step 5: Add Bemba Text Translation

**Section: 🇿🇲 Bemba Translation (Chibemba)** - Click to expand

- **Title (Bemba)**: `Ukwingisha ku Recycling`
- **Content (Bemba)**: Full lesson text in Bemba

### Step 6: Upload Bemba Media Files

**Section: 🎬 Bemba Media Files** - Click to expand

- **Video File (Bemba)**: Upload Bemba-language video
- **Audio File (Bemba)**: Upload Bemba-language audio

**File naming suggestion:**
- `lesson-1-intro-recycling-bem.mp4`
- `lesson-1-intro-recycling-bem.mp3`

### Step 7: Add Nyanja Text Translation

**Section: 🇿🇲 Nyanja Translation (Chinyanja)** - Click to expand

- **Title (Nyanja)**: `Mawu Oyamba pa Recycling`
- **Content (Nyanja)**: Full lesson text in Nyanja

### Step 8: Upload Nyanja Media Files

**Section: 🎬 Nyanja Media Files** - Click to expand

- **Video File (Nyanja)**: Upload Nyanja-language video
- **Audio File (Nyanja)**: Upload Nyanja-language audio

**File naming suggestion:**
- `lesson-1-intro-recycling-ny.mp4`
- `lesson-1-intro-recycling-ny.mp3`

### Step 9: Interactive Content (Optional)

**Section: 🎮 Interactive Content** - Click to expand

- Interactive type
- Interactive payload (JSON)
- External tour URL

### Step 10: Save and Check Status

After saving, in the lesson list you'll see TWO status columns:

1. **Text Translations**: `✅ BEM ✅ NY` or `❌ No translations`
2. **Media Files**: 
   - `🎬 EN 🎬 BEM 🎬 NY` (all videos available)
   - `🎵 EN 🎵 BEM` (only EN and BEM audio)
   - `📝 Text only` (no media files)

---

## Adding Quiz Translations

### Step 1: Create or Edit a Quiz

1. Click on **"Quizzes"** under ELEARNING
2. Click **"Add Quiz"** or select existing

### Step 2: Set Quiz Details

**Section: 📍 Quiz Details**

- **Lesson**: Select parent lesson
- ☑ Is Required
- **Pass Percentage**: `70` (minimum to pass)
- **Max Attempts**: `3`
- **Time Limit (minutes)**: `30` (0 for unlimited)

### Step 3: Fill English Content

**Section: 📝 English Content (Required)**

- **Title**: `Recycling Knowledge Check`
- **Description**: `Test your understanding of recycling concepts...`

### Step 4: Add Bemba Translation

**Section: 🇿🇲 Bemba Translation** - Click to expand

- **Title (Bemba)**: `Ukupepa Ubumfwiko bwa Recycling`
- **Description (Bemba)**: `Pimeni ubumfwiko bwenu...`

### Step 5: Add Nyanja Translation

**Section: 🇿🇲 Nyanja Translation** - Click to expand

- **Title (Nyanja)**: `Kuyesa Chidziwitso cha Recycling`
- **Description (Nyanja)**: `Yesani kumvetsa kwanu...`

### Step 6: Save Quiz

Click **"Save and continue editing"** to add questions

### Step 7: Add Questions

Scroll down to **"Questions"** section (inline)

Or click **"Questions"** in the ELEARNING menu

#### For Each Question:

1. **Click "Add Question"**

2. **Fill Question Details**:
   - Quiz: (auto-selected)
   - Question Type: Multiple Choice / True-False / Text
   - Points: `10`
   - Order: `1`, `2`, `3`...

3. **English Question**:
   ```
   Question Text: What percentage of plastic can be recycled?
   ```

4. **Expand Bemba Translation**:
   ```
   Question Text (Bemba): Ni percentage shinga sha plastic shingasandulwa?
   ```

5. **Expand Nyanja Translation**:
   ```
   Question Text (Nyanja): Ndi mulingo wanji wa pulasitiki womwe ungasinthidwe?
   ```

6. **Save Question**

### Step 8: Add Answers (Inline)

For each question, add multiple answers:

#### Answer 1:
- **Answer Text (EN)**: `About 90%`
- **Answer Text (Bemba)**: `Pafupifupi 90%`
- **Answer Text (Nyanja)**: `Pafupifupi 90%`
- ☐ Is Correct
- Order: `1`

#### Answer 2:
- **Answer Text (EN)**: `About 50%`
- **Answer Text (Bemba)**: `Pafupifupi 50%`
- **Answer Text (Nyanja)**: `Pafupifupi 50%`
- ☐ Is Correct
- Order: `2`

#### Answer 3:
- **Answer Text (EN)**: `About 9%`
- **Answer Text (Bemba)**: `Pafupifupi 9%`
- **Answer Text (Nyanja)**: `Pafupifupi 9%`
- ☑ **Is Correct** ← Mark the correct answer
- Order: `3`

#### Answer 4:
- **Answer Text (EN)**: `About 25%`
- **Answer Text (Bemba)**: `Pafupifupi 25%`
- **Answer Text (Nyanja)**: `Pafupifupi 25%`
- ☐ Is Correct
- Order: `4`

### Step 9: Check Translation Status

In the quiz list:
- **Translation Status**: `✅ BEM ✅ NY` (complete)

In the question list:
- **Translation Status**: `✅ BEM ✅ NY` (complete)

In the answer list:
- **Translation Status**: `✅ BEM ✅ NY` (complete)

---

## Translation Status Indicators

### Understanding the Indicators

#### ✅ Complete
- Both title AND description/content translated
- Shows: `✅ BEM ✅ NY`

#### ⚠️ Partial
- Only title OR only description translated
- Shows: `⚠️ BEM ⚠️ NY`

#### ❌ None
- No translations added
- Shows: `❌ No translations`

#### 🇿🇲 Language Indicator
- Shows which languages have translations
- Example: `🇿🇲 BEM 🇿🇲 NY`

#### Media Indicators
- 🎬 = Video file available
- 🎵 = Audio file available
- 📝 = Text only (no media)

### Examples

**Module List View:**
```
Title                    | Category | Translation Status | Created
-------------------------|----------|-------------------|----------
Waste Management Basics  | Basics   | ✅ BEM ✅ NY      | 2025-01-15
Composting Guide         | Advanced | ⚠️ BEM            | 2025-01-14
Recycling 101            | Basics   | ❌ No translations| 2025-01-13
```

**Lesson List View:**
```
Title              | Module | Text Translations | Media Files        | Order
-------------------|--------|-------------------|-------------------|-------
Intro to Recycling | Waste  | ✅ BEM ✅ NY      | 🎬 EN 🎬 BEM 🎬 NY| 1
Types of Waste     | Waste  | ✅ BEM            | 🎵 EN 🎵 BEM      | 2
Sorting Methods    | Waste  | ❌ No translations| 📝 Text only      | 3
```

---

## Best Practices

### 1. Translation Workflow

**Recommended Order:**
1. Create all English content first
2. Review and finalize English version
3. Add Bemba translations
4. Add Nyanja translations
5. Upload language-specific media files
6. Test on frontend

### 2. Content Guidelines

**For Text Translations:**
- Keep the same meaning and tone
- Adapt examples to local context
- Use culturally appropriate references
- Maintain formatting (bold, lists, etc.)

**For Media Files:**
- Use same video/audio quality across languages
- Keep similar duration
- Use clear pronunciation
- Add subtitles if possible

### 3. File Organization

**Naming Convention:**
```
[content-type]-[number]-[title]-[language].[extension]

Examples:
- lesson-1-intro-recycling-en.mp4
- lesson-1-intro-recycling-bem.mp4
- lesson-1-intro-recycling-ny.mp4
- module-thumbnail-waste-basics.jpg
```

### 4. Quality Assurance

**Before Publishing:**
- ☑ All English content complete
- ☑ Translations reviewed by native speakers
- ☑ Media files tested and working
- ☑ Quiz questions make sense in all languages
- ☑ Correct answers marked properly
- ☑ Test on frontend in all languages

### 5. Incremental Translation

**You don't need to translate everything at once:**
1. Start with most popular modules
2. Translate module titles and descriptions first
3. Add lesson translations gradually
4. Upload media files as they become available
5. System automatically falls back to English

### 6. Using Search

**Search works across all languages:**
- Search for "recycling" finds English content
- Search for "ukusandula" finds Bemba content
- Search for "kusamalira" finds Nyanja content

### 7. Bulk Operations

**For multiple items:**
1. Use list view filters
2. Select multiple items with checkboxes
3. Use admin actions (if configured)
4. Or edit one by one for quality

---

## Quick Reference Card

### Module Translation Checklist
- [ ] English title and description
- [ ] Bemba title and description
- [ ] Nyanja title and description
- [ ] Thumbnail image
- [ ] Category and tags
- [ ] Published and active

### Lesson Translation Checklist
- [ ] English title and content
- [ ] English media files (if applicable)
- [ ] Bemba title and content
- [ ] Bemba media files (if applicable)
- [ ] Nyanja title and content
- [ ] Nyanja media files (if applicable)
- [ ] Order and placement correct
- [ ] Published

### Quiz Translation Checklist
- [ ] English title and description
- [ ] Bemba title and description
- [ ] Nyanja title and description
- [ ] All questions translated
- [ ] All answers translated
- [ ] Correct answers marked
- [ ] Pass percentage set
- [ ] Published

---

## Troubleshooting

### Translation Not Showing on Frontend

**Check:**
1. Is the content published?
2. Is the translation field filled in admin?
3. Did you save the changes?
4. Clear browser cache
5. Check user's language setting

### Media File Not Playing

**Check:**
1. File format (MP4 for video, MP3 for audio)
2. File size (not too large)
3. File uploaded successfully
4. MEDIA_URL and MEDIA_ROOT configured
5. File permissions

### Status Indicator Not Updating

**Solution:**
1. Refresh the admin page
2. Check if both title AND description are filled
3. Save the object again

---

## Support

For questions or issues:
1. Check the main documentation
2. Review error messages in admin
3. Test on frontend to verify
4. Check Django logs for errors

---

## Summary

The EcoLearn admin panel makes multilingual content management easy with:
- ✅ Clear visual organization
- ✅ Collapsible sections
- ✅ Status indicators
- ✅ Separate media uploads
- ✅ Search across languages
- ✅ Incremental translation support

**Remember**: English content is required, translations are optional but recommended for better user experience!
