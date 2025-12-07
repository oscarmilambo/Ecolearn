# Translation Flow Verification Guide

## How Translations Work from Admin to User Dashboard

### Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. ADMIN ADDS CONTENT                         │
│  Admin Panel → Module/Lesson/Quiz → Fill translations → Save    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                 2. DATA STORED IN DATABASE                       │
│  title (EN) | title_bem (BEM) | title_ny (NY)                   │
│  description (EN) | description_bem | description_ny            │
│  video_file (EN) | video_file_bem | video_file_ny               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              3. USER SELECTS LANGUAGE                            │
│  Navigation Dropdown → Click BEM/NY → set_language view         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│            4. LANGUAGE PREFERENCE SAVED                          │
│  user.preferred_language = 'bem'                                │
│  Session: LANGUAGE_SESSION_KEY = 'bem'                          │
│  Cookie: ecolearn_language = 'bem'                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│           5. MIDDLEWARE ACTIVATES LANGUAGE                       │
│  UserLanguageMiddleware → translation.activate('bem')           │
│  request.LANGUAGE_CODE = 'bem'                                  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│          6. CONTEXT PROCESSOR ADDS TO TEMPLATES                  │
│  user_language context processor → user_language = 'bem'        │
│  Available in ALL templates automatically                       │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              7. VIEW QUERIES DATABASE                            │
│  modules = Module.objects.filter(is_published=True)             │
│  Returns ALL fields including title_bem, title_ny, etc.         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│           8. TEMPLATE DISPLAYS TRANSLATION                       │
│  {% get_translated_field module 'title' %}                      │
│  Checks user_language → Returns title_bem if BEM selected       │
│  Falls back to title (EN) if translation not available          │
└─────────────────────────────────────────────────────────────────┘
```

## Current Implementation Status

### ✅ Backend Components (All Working)

#### 1. Database Models (`elearning/models.py`)
```python
class Module(models.Model):
    title = models.CharField(max_length=200)
    title_bem = models.CharField(max_length=200, blank=True, null=True)
    title_ny = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    description_bem = models.TextField(blank=True, null=True)
    description_ny = models.TextField(blank=True, null=True)
    # ... other fields
```

#### 2. User Model (`accounts/models.py`)
```python
class CustomUser(AbstractUser):
    preferred_language = models.CharField(
        max_length=3,
        choices=[('en', 'English'), ('bem', 'Bemba'), ('ny', 'Nyanja')],
        default='en'
    )
```

#### 3. Middleware (`elearning/middleware.py`)
```python
class UserLanguageMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            user_language = request.user.preferred_language
            translation.activate(user_language)
            request.LANGUAGE_CODE = user_language
        response = self.get_response(request)
        return response
```

#### 4. Context Processor (`elearning/context_processors.py`)
```python
def user_language(request):
    lang = 'en'
    if request.user.is_authenticated:
        lang = request.user.preferred_language or 'en'
    return {"user_language": lang}
```

#### 5. Language Switching View (`elearning/views.py`)
```python
@login_required
def set_language(request, language_code):
    if language_code in ['en', 'bem', 'ny']:
        request.user.preferred_language = language_code
        request.user.save()
        translation.activate(language_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = language_code
        # Set cookie and redirect
```

#### 6. Template Tags (`elearning/templatetags/elearning_extras.py`)
```python
@register.simple_tag(takes_context=True)
def get_translated_field(context, obj, field_name):
    user_language = context.get('user_language', 'en')
    if user_language == 'bem':
        translated = getattr(obj, f'{field_name}_bem', None)
        if translated:
            return translated
    elif user_language == 'ny':
        translated = getattr(obj, f'{field_name}_ny', None)
        if translated:
            return translated
    return getattr(obj, field_name, '')
```

### ✅ Frontend Components (All Working)

#### 1. Language Switcher (`templates/base.html`)
```html
<div class="border-t border-gray-100 py-2 px-4">
    <p class="text-xs font-medium text-gray-500 mb-2">Language</p>
    <div class="flex space-x-2">
        <a href="{% url 'set_language' 'en' %}" 
           class="{% if user_language == 'en' %}bg-eco-green text-white{% endif %}">EN</a>
        <a href="{% url 'set_language' 'bem' %}" 
           class="{% if user_language == 'bem' %}bg-eco-green text-white{% endif %}">BEM</a>
        <a href="{% url 'set_language' 'ny' %}" 
           class="{% if user_language == 'ny' %}bg-eco-green text-white{% endif %}">NY</a>
    </div>
</div>
```

#### 2. Dashboard Template (`templates/dashboard/user_dashboard.html`)
```django
{% load elearning_extras %}

<h3>{% get_translated_field module 'title' %}</h3>
<p>{% get_translated_field module 'description' %}</p>
```

#### 3. Module List Template (`templates/elearning/module_list.html`)
```django
<h3>
    {% if user_language == 'bem' and module.title_bem %}
        {{ module.title_bem }}
    {% elif user_language == 'ny' and module.title_ny %}
        {{ module.title_ny }}
    {% else %}
        {{ module.title }}
    {% endif %}
</h3>
```

#### 4. Lesson Detail Template (`templates/elearning/lesson_detail.html`)
```django
{% get_translated_media lesson 'video' as video_file %}
{% if video_file %}
    <video controls>
        <source src="{{ video_file.url }}" type="video/mp4">
    </video>
{% endif %}

<div class="content-text">
    {% if user_language == 'bem' and lesson.content_bem %}
        {{ lesson.content_bem|safe }}
    {% elif user_language == 'ny' and lesson.content_ny %}
        {{ lesson.content_ny|safe }}
    {% else %}
        {{ lesson.content|safe }}
    {% endif %}
</div>
```

#### 5. Quiz Template (`templates/elearning/quiz_take.html`)
```django
<h1>
    {% if user_language == 'bem' and quiz.title_bem %}
        {{ quiz.title_bem }}
    {% elif user_language == 'ny' and quiz.title_ny %}
        {{ quiz.title_ny }}
    {% else %}
        {{ quiz.title }}
    {% endif %}
</h1>
```

### ✅ Admin Panel Configuration

All admin classes have been enhanced with:
- Organized fieldsets with emoji icons
- Collapsible translation sections
- Translation status indicators
- Search across all language fields

## Step-by-Step: Admin Adds Content → User Sees Translation

### Scenario: Admin adds a new module with Bemba translation

#### Step 1: Admin Creates Module
1. Admin logs into `/admin/`
2. Goes to `Elearning > Modules > Add Module`
3. Fills in:
   - **Title**: "Waste Sorting Basics"
   - **Description**: "Learn how to sort waste properly..."
   - **Title (Bemba)**: "Ifya Mfumu fya Ukusankanya Ubulongwe"
   - **Description (Bemba)**: "Sambilila ifyakuti mungasankanya buti ubulongwe..."
4. Clicks **Save**

#### Step 2: Database Stores Data
```sql
INSERT INTO elearning_module (
    title, 
    title_bem, 
    title_ny,
    description,
    description_bem,
    description_ny
) VALUES (
    'Waste Sorting Basics',
    'Ifya Mfumu fya Ukusankanya Ubulongwe',
    NULL,
    'Learn how to sort waste properly...',
    'Sambilila ifyakuti mungasankanya buti ubulongwe...',
    NULL
);
```

#### Step 3: User Switches to Bemba
1. User logs in
2. Clicks on user dropdown in navigation
3. Clicks "BEM" button
4. Request sent to `/set-language/bem/`
5. View executes:
   ```python
   request.user.preferred_language = 'bem'
   request.user.save()
   translation.activate('bem')
   ```
6. User redirected back to dashboard

#### Step 4: Dashboard Loads
1. View queries database:
   ```python
   modules = Module.objects.filter(enrollment__user=request.user)
   ```
2. Returns module with ALL fields including `title_bem`

#### Step 5: Template Renders
1. Template tag called:
   ```django
   {% get_translated_field module 'title' %}
   ```
2. Tag logic:
   ```python
   user_language = 'bem'  # from context
   field_name = 'title'
   translated = getattr(module, 'title_bem', None)  # Gets "Ifya Mfumu..."
   if translated:
       return translated  # Returns Bemba title
   ```
3. User sees: **"Ifya Mfumu fya Ukusankanya Ubulongwe"**

#### Step 6: User Switches to English
1. User clicks "EN" button
2. Same process, but:
   ```python
   user_language = 'en'
   return getattr(module, 'title')  # Returns English title
   ```
3. User sees: **"Waste Sorting Basics"**

## Verification Checklist

### ✅ Configuration Files

- [x] `ecolearn/settings.py` - LANGUAGES defined
- [x] `ecolearn/settings.py` - Middleware order correct
- [x] `ecolearn/settings.py` - Context processor registered
- [x] `ecolearn/settings.py` - Language cookie settings
- [x] `ecolearn/urls.py` - set_language URL pattern
- [x] `elearning/middleware.py` - UserLanguageMiddleware exists
- [x] `elearning/context_processors.py` - user_language function exists
- [x] `elearning/views.py` - set_language function exists
- [x] `elearning/templatetags/elearning_extras.py` - Template tags exist

### ✅ Database Models

- [x] Module - has title_bem, title_ny, description_bem, description_ny
- [x] Lesson - has title_bem, title_ny, content_bem, content_ny
- [x] Lesson - has video_file_bem, video_file_ny, audio_file_bem, audio_file_ny
- [x] Quiz - has title_bem, title_ny, description_bem, description_ny
- [x] Question - has question_text_bem, question_text_ny
- [x] Answer - has answer_text_bem, answer_text_ny
- [x] Category - has name_bem, name_ny, description_bem, description_ny
- [x] Tag - has name_bem, name_ny
- [x] CustomUser - has preferred_language field

### ✅ Templates

- [x] base.html - Language switcher in navigation
- [x] user_dashboard.html - Uses get_translated_field
- [x] module_list.html - Displays translated titles/descriptions
- [x] module_detail.html - Uses get_translated_field
- [x] lesson_detail.html - Uses get_translated_media and translated content
- [x] quiz_take.html - Displays translated quiz/questions/answers

### ✅ Admin Panel

- [x] CategoryAdmin - Translation fieldsets and status
- [x] TagAdmin - Translation fieldsets and status
- [x] ModuleAdmin - Translation fieldsets and status
- [x] LessonAdmin - Translation fieldsets, media uploads, status
- [x] QuizAdmin - Translation fieldsets and status
- [x] QuestionAdmin - Translation fieldsets and status
- [x] AnswerAdmin - Translation fieldsets and status

## Testing the Complete Flow

### Test 1: Module Translation

1. **Admin adds module**:
   - Login to admin
   - Add module with English and Bemba translations
   - Save

2. **User enrolls**:
   - Login as user
   - Enroll in the module

3. **User switches language**:
   - Go to dashboard
   - Click user dropdown → BEM
   - Verify module title shows in Bemba
   - Click EN
   - Verify module title shows in English

### Test 2: Lesson with Media

1. **Admin adds lesson**:
   - Create lesson
   - Upload English video
   - Add Bemba translation
   - Upload Bemba video
   - Save

2. **User views lesson**:
   - Navigate to lesson
   - Language set to English → English video plays
   - Switch to Bemba → Bemba video plays
   - Content text changes to Bemba

### Test 3: Quiz Translation

1. **Admin creates quiz**:
   - Add quiz with translations
   - Add questions with Bemba translations
   - Add answers with Bemba translations
   - Save

2. **User takes quiz**:
   - Navigate to quiz
   - Language set to Bemba
   - Quiz title in Bemba
   - Questions in Bemba
   - Answers in Bemba
   - Switch to English → All changes to English

## Troubleshooting

### Issue: Translations not showing

**Check:**
1. Is `user_language` in template context?
   ```django
   {{ user_language }}  <!-- Should show 'bem' or 'ny' -->
   ```

2. Are translation fields filled in admin?
   - Check admin panel
   - Verify title_bem and description_bem have values

3. Is middleware activated?
   ```python
   # In settings.py MIDDLEWARE
   'elearning.middleware.UserLanguageMiddleware',
   ```

4. Is context processor registered?
   ```python
   # In settings.py TEMPLATES
   'elearning.context_processors.user_language',
   ```

### Issue: Language not persisting

**Check:**
1. User's preferred_language field updated?
   ```python
   # In Django shell
   from accounts.models import CustomUser
   user = CustomUser.objects.get(username='testuser')
   print(user.preferred_language)  # Should show 'bem' or 'ny'
   ```

2. Session working?
   ```python
   # In view
   print(request.session.get(translation.LANGUAGE_SESSION_KEY))
   ```

3. Cookie set?
   - Check browser dev tools → Application → Cookies
   - Look for `ecolearn_language` cookie

### Issue: Media files not changing

**Check:**
1. Files uploaded in admin?
   - Verify video_file_bem exists
   - Check file path in database

2. Template using correct tag?
   ```django
   {% get_translated_media lesson 'video' as video_file %}
   ```

3. File accessible?
   - Check MEDIA_URL and MEDIA_ROOT
   - Verify file permissions

## Summary

The translation system is **fully functional** and works as follows:

1. ✅ Admin adds content with translations in Django admin
2. ✅ Data stored in database with language-specific fields
3. ✅ User selects language from navigation dropdown
4. ✅ Language preference saved to user profile, session, and cookie
5. ✅ Middleware activates language on each request
6. ✅ Context processor makes language available in templates
7. ✅ Template tags retrieve correct translation based on user's language
8. ✅ Content displays in selected language
9. ✅ Media files (video/audio) served in appropriate language
10. ✅ Falls back to English if translation not available

**Everything is connected and working!** The admin just needs to add translations, and they will automatically appear for users based on their language selection.
