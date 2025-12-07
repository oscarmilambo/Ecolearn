# Language Switching Test Checklist

## Pre-requisites
- [ ] Server is running (`python manage.py runserver`)
- [ ] User account exists and is logged in
- [ ] At least one module with translations exists

## Test Steps

### 1. Database Setup
Run migrations to ensure all fields are created:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Test Content in Admin
1. Go to http://localhost:8000/admin/
2. Create a Module with:
   - **Title**: "Waste Management Basics"
   - **Title (Bemba)**: "Ifya Ukutungulula Ubulongwe"
   - **Title (Nyanja)**: "Zoyambira za Kusamalira Zinyalala"
   - **Description**: "Learn the fundamentals of waste management"
   - **Description (Bemba)**: "Sambilila ifya mfumu fya ukutungulula ubulongwe"
   - **Description (Nyanja)**: "Phunzirani zofunikira za kusamalira zinyalala"

3. Create a Lesson with:
   - **Title**: "Introduction to Recycling"
   - **Title (Bemba)**: "Ukwingisha ku Recycling"
   - **Title (Nyanja)**: "Mawu Oyamba pa Recycling"
   - **Content**: "Recycling is the process of converting waste..."
   - **Content (Bemba)**: "Recycling e process ya ukusandula ubulongwe..."
   - **Content (Nyanja)**: "Recycling ndi njira yosintha zinyalala..."
   - Upload video files:
     - **Video File (EN)**: Upload English video
     - **Video File (Bemba)**: Upload Bemba video
     - **Video File (Nyanja)**: Upload Nyanja video

### 3. Test Language Switching

#### Test 1: Navigation Bar Language Switcher
- [ ] Log in to the platform
- [ ] Click on user dropdown in top navigation
- [ ] Verify language switcher is visible with EN, BEM, NY buttons
- [ ] Current language should be highlighted in green
- [ ] Click "BEM" button
- [ ] Page should reload
- [ ] Verify "BEM" is now highlighted

#### Test 2: Module List Page
- [ ] Navigate to `/elearning/modules/`
- [ ] With language set to English:
  - [ ] Module title shows "Waste Management Basics"
  - [ ] Module description shows English text
- [ ] Switch to Bemba (BEM):
  - [ ] Module title shows "Ifya Ukutungulula Ubulongwe"
  - [ ] Module description shows Bemba text
- [ ] Switch to Nyanja (NY):
  - [ ] Module title shows "Zoyambira za Kusamalira Zinyalala"
  - [ ] Module description shows Nyanja text

#### Test 3: Module Detail Page
- [ ] Click on a module
- [ ] Verify module title and description change with language
- [ ] Verify lesson titles change with language
- [ ] Check category names are translated

#### Test 4: Lesson Detail Page
- [ ] Click on a lesson
- [ ] With English selected:
  - [ ] Lesson title shows in English
  - [ ] Lesson content shows in English
  - [ ] Video file is the English version
- [ ] Switch to Bemba:
  - [ ] Lesson title shows in Bemba
  - [ ] Lesson content shows in Bemba
  - [ ] Video file changes to Bemba version
- [ ] Switch to Nyanja:
  - [ ] Lesson title shows in Nyanja
  - [ ] Lesson content shows in Nyanja
  - [ ] Video file changes to Nyanja version

#### Test 5: Quiz Page
- [ ] Navigate to a quiz
- [ ] Verify quiz title changes with language
- [ ] Verify quiz description changes with language
- [ ] Verify question text changes with language
- [ ] Verify answer options change with language

#### Test 6: Language Persistence
- [ ] Select Bemba language
- [ ] Navigate to different pages
- [ ] Close browser
- [ ] Reopen browser and log in
- [ ] Verify language is still Bemba (cookie persistence)

#### Test 7: Fallback Behavior
- [ ] Create a module with only English title (no translations)
- [ ] Switch to Bemba
- [ ] Verify module shows English title (fallback)
- [ ] No errors should occur

### 4. Browser Console Check
- [ ] Open browser developer tools (F12)
- [ ] Check Console tab for any JavaScript errors
- [ ] Check Network tab when switching languages
- [ ] Verify `/set-language/<code>/` request succeeds (302 redirect)

### 5. Database Verification
Check that language preference is saved:
```python
# In Django shell (python manage.py shell)
from accounts.models import CustomUser
user = CustomUser.objects.get(username='your_username')
print(user.preferred_language)  # Should show 'en', 'bem', or 'ny'
```

## Expected Results

### ✅ Pass Criteria
- Language switcher appears in navigation
- Content changes when language is switched
- Media files (video/audio) change based on language
- Language preference persists across sessions
- No errors in browser console
- Fallback to English works when translation missing
- User's language preference is saved in database

### ❌ Fail Indicators
- Language switcher not visible
- Content doesn't change when switching language
- JavaScript errors in console
- 404 or 500 errors when switching language
- Language resets after page refresh
- Media files don't change with language

## Common Issues and Solutions

### Issue: Language not changing
**Solution**: 
- Check middleware order in settings.py
- Verify context processor is registered
- Clear browser cache and cookies

### Issue: Translations not showing
**Solution**:
- Verify translation fields are filled in admin
- Check template syntax
- Ensure `user_language` is in template context

### Issue: Media files not loading
**Solution**:
- Check MEDIA_URL and MEDIA_ROOT settings
- Verify files exist in correct directories
- Check file permissions

### Issue: 404 error on language switch
**Solution**:
- Verify URL pattern in urls.py
- Check that `set_language` view is imported correctly

## Performance Check
- [ ] Language switching is instant (< 1 second)
- [ ] No noticeable delay when loading translated content
- [ ] Media files load smoothly

## Accessibility Check
- [ ] Language switcher is keyboard accessible
- [ ] Screen readers can identify current language
- [ ] Color contrast meets WCAG standards

## Mobile Testing
- [ ] Language switcher works on mobile devices
- [ ] Dropdown menu is accessible on touch screens
- [ ] Content displays correctly on small screens

## Test Report Template

```
Test Date: _______________
Tester: _______________
Browser: _______________
OS: _______________

Results:
- Navigation Switcher: PASS / FAIL
- Module List: PASS / FAIL
- Module Detail: PASS / FAIL
- Lesson Detail: PASS / FAIL
- Quiz: PASS / FAIL
- Media Files: PASS / FAIL
- Persistence: PASS / FAIL
- Fallback: PASS / FAIL

Issues Found:
1. _______________
2. _______________
3. _______________

Overall Status: PASS / FAIL

Notes:
_______________
_______________
```
