from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import (
    Category, Tag, Module, Lesson, Quiz, Question, Answer,
    Enrollment, LessonProgress, QuizAttempt, QuizResponse,
    Certificate, ModuleReview, LearningStreak, Badge, UserBadge
)


# Import-Export Resources
class ModuleResource(resources.ModelResource):
    class Meta:
        model = Module
        fields = ('id', 'title', 'slug', 'category__name', 'difficulty', 'duration_minutes', 'is_premium', 'is_published')
        export_order = fields


class LessonResource(resources.ModelResource):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'slug', 'module__title', 'order', 'content_type', 'duration_minutes', 'is_published')
        export_order = fields


class QuizResource(resources.ModelResource):
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'lesson__title', 'pass_percentage', 'max_attempts', 'time_limit_minutes')
        export_order = fields


class BadgeResource(resources.ModelResource):
    class Meta:
        model = Badge
        fields = ('id', 'name', 'code', 'description', 'points_required', 'is_active')
        export_order = fields


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'order', 'is_active', 'color')
        export_order = fields


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ['name', 'slug', 'module_count_display', 'order', 'is_active', 'color_display', 'translation_status']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'name_bem', 'name_ny']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('English (Default)', {
            'fields': ('name', 'slug', 'description', 'icon', 'icon_class', 'color')
        }),
        ('Bemba Translation', {
            'fields': ('name_bem', 'description_bem'),
            'classes': ('collapse',),
            'description': 'Add Bemba (Chibemba) translations here'
        }),
        ('Nyanja Translation', {
            'fields': ('name_ny', 'description_ny'),
            'classes': ('collapse',),
            'description': 'Add Nyanja (Chinyanja) translations here'
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )
    
    def module_count_display(self, obj):
        return obj.get_module_count()
    module_count_display.short_description = 'Modules'
    
    def color_display(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border-radius: 4px;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    def translation_status(self, obj):
        status = []
        if obj.name_bem:
            status.append('🇿🇲 BEM')
        if obj.name_ny:
            status.append('🇿🇲 NY')
        return ' '.join(status) if status else '⚠️ EN only'
    translation_status.short_description = 'Translations'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'module_count', 'translation_status']
    search_fields = ['name', 'name_bem', 'name_ny']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('English (Default)', {
            'fields': ('name', 'slug')
        }),
        ('Translations', {
            'fields': ('name_bem', 'name_ny'),
            'classes': ('collapse',),
            'description': 'Add Bemba and Nyanja translations'
        }),
    )
    
    def module_count(self, obj):
        return obj.modules.count()
    module_count.short_description = 'Modules'
    
    def translation_status(self, obj):
        status = []
        if obj.name_bem:
            status.append('🇿🇲 BEM')
        if obj.name_ny:
            status.append('🇿🇲 NY')
        return ' '.join(status) if status else '⚠️ EN only'
    translation_status.short_description = 'Translations'


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'content_type', 'order', 'duration_minutes', 'is_preview']


class QuizInline(admin.TabularInline):
    # Quiz is related to Lesson, hence it is an Inline here.
    model = Quiz
    extra = 0
    fields = ['title', 'pass_percentage', 'max_attempts', 'is_required']


@admin.register(Module)
class ModuleAdmin(ImportExportModelAdmin):
    resource_class = ModuleResource
    list_display = [
        'title', 'category', 'difficulty', 'duration_minutes', 
        'is_premium', 'is_featured', 'is_published', 
        'enrollments_count', 'average_rating', 'translation_status', 'created_at'
    ]
    list_filter = ['difficulty', 'is_premium', 'is_featured', 'is_published', 'category', 'created_at']
    search_fields = ['title', 'title_bem', 'title_ny', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags', 'prerequisites', 'target_roles']
    inlines = [LessonInline]
    readonly_fields = ['views_count', 'enrollments_count', 'completions_count', 'average_rating', 'created_at', 'updated_at']
    
    fieldsets = (
        ('📝 English Content (Required)', {
            'fields': ('title', 'slug', 'description', 'category', 'tags', 'thumbnail', 'video_url'),
            'description': 'Fill in the English content first. This is required.'
        }),
        ('🇿🇲 Bemba Translation (Chibemba)', {
            'fields': ('title_bem', 'description_bem'),
            'classes': ('collapse',),
            'description': 'Add Bemba translations here. Leave blank if not available yet.'
        }),
        ('🇿🇲 Nyanja Translation (Chinyanja)', {
            'fields': ('title_ny', 'description_ny'),
            'classes': ('collapse',),
            'description': 'Add Nyanja translations here. Leave blank if not available yet.'
        }),
        ('⚙️ Module Settings', {
            'fields': ('difficulty', 'duration_minutes', 'points_reward', 'prerequisites', 'hierarchy_stage', 'waste_stream', 'external_tour_url', 'target_roles')
        }),
        ('🔒 Access & Publishing', {
            'fields': ('is_premium', 'is_featured', 'is_published', 'is_active')
        }),
        ('📊 Statistics (Read-only)', {
            'fields': ('views_count', 'enrollments_count', 'completions_count', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('📅 Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def translation_status(self, obj):
        status = []
        if obj.title_bem and obj.description_bem:
            status.append('✅ BEM')
        elif obj.title_bem or obj.description_bem:
            status.append('⚠️ BEM')
        
        if obj.title_ny and obj.description_ny:
            status.append('✅ NY')
        elif obj.title_ny or obj.description_ny:
            status.append('⚠️ NY')
        
        return ' '.join(status) if status else '❌ No translations'
    translation_status.short_description = 'Translations'
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Lesson)
class LessonAdmin(ImportExportModelAdmin):
    resource_class = LessonResource
    list_display = (
        'title', 
        'module', 
        'slug', 
        'order',
        'content_type', 
        'is_published',
        'duration_minutes',
        'is_preview',
        'translation_status',
        'media_status'
    )
    
    list_editable = ['order', 'is_published', 'is_preview']
    list_filter = ['content_type', 'is_preview', 'is_published', 'module__category']
    search_fields = ['title', 'title_bem', 'title_ny', 'module__title', 'content']
    prepopulated_fields = {'slug': ('title',)} 
    inlines = [QuizInline]
    
    fieldsets = (
        ('📍 Lesson Placement', {
            'fields': ('module', 'order', 'is_published', 'is_required', 'is_preview'),
            'description': 'Set where this lesson appears in the module'
        }),
        ('📝 English Content (Required)', {
            'fields': ('title', 'slug', 'content_type', 'duration_minutes', 'content'),
            'description': 'Fill in the English content first'
        }),
        ('🎬 English Media Files', {
            'fields': ('video_file', 'audio_file'),
            'classes': ('collapse',),
            'description': 'Upload video or audio files for English version'
        }),
        ('🇿🇲 Bemba Translation (Chibemba)', {
            'fields': ('title_bem', 'content_bem'),
            'classes': ('collapse',),
            'description': 'Add Bemba text translations'
        }),
        ('🎬 Bemba Media Files', {
            'fields': ('video_file_bem', 'audio_file_bem'),
            'classes': ('collapse',),
            'description': 'Upload Bemba-language video or audio files'
        }),
        ('🇿🇲 Nyanja Translation (Chinyanja)', {
            'fields': ('title_ny', 'content_ny'),
            'classes': ('collapse',),
            'description': 'Add Nyanja text translations'
        }),
        ('🎬 Nyanja Media Files', {
            'fields': ('video_file_ny', 'audio_file_ny'),
            'classes': ('collapse',),
            'description': 'Upload Nyanja-language video or audio files'
        }),
        ('🎮 Interactive Content', {
            'fields': ('interactive_type', 'interactive_payload', 'external_tour_url'),
            'classes': ('collapse',),
        }),
    )

    def translation_status(self, obj):
        status = []
        if obj.title_bem and obj.content_bem:
            status.append('✅ BEM')
        elif obj.title_bem or obj.content_bem:
            status.append('⚠️ BEM')
        
        if obj.title_ny and obj.content_ny:
            status.append('✅ NY')
        elif obj.title_ny or obj.content_ny:
            status.append('⚠️ NY')
        
        return ' '.join(status) if status else '❌ No translations'
    translation_status.short_description = 'Text Translations'
    
    def media_status(self, obj):
        media = []
        if obj.content_type == 'video':
            if obj.video_file:
                media.append('🎬 EN')
            if obj.video_file_bem:
                media.append('🎬 BEM')
            if obj.video_file_ny:
                media.append('🎬 NY')
        elif obj.content_type == 'audio':
            if obj.audio_file:
                media.append('🎵 EN')
            if obj.audio_file_bem:
                media.append('🎵 BEM')
            if obj.audio_file_ny:
                media.append('🎵 NY')
        else:
            return '📝 Text only'
        
        return ' '.join(media) if media else '❌ No media'
    media_status.short_description = 'Media Files'
    
class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ['answer_text', 'answer_text_bem', 'answer_text_ny', 'is_correct', 'order']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text_short', 'quiz', 'question_type', 'points', 'order', 'translation_status']
    list_filter = ['question_type', 'quiz__lesson__module']
    search_fields = ['question_text', 'question_text_bem', 'question_text_ny', 'quiz__title']
    inlines = [AnswerInline]
    
    fieldsets = (
        ('📍 Question Details', {
            'fields': ('quiz', 'question_type', 'points', 'order')
        }),
        ('📝 English Question (Required)', {
            'fields': ('question_text',),
            'description': 'Enter the question in English'
        }),
        ('🇿🇲 Bemba Translation', {
            'fields': ('question_text_bem',),
            'classes': ('collapse',),
            'description': 'Enter the question in Bemba (Chibemba)'
        }),
        ('🇿🇲 Nyanja Translation', {
            'fields': ('question_text_ny',),
            'classes': ('collapse',),
            'description': 'Enter the question in Nyanja (Chinyanja)'
        }),
    )
    
    def question_text_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Question'
    
    def translation_status(self, obj):
        status = []
        if obj.question_text_bem:
            status.append('✅ BEM')
        if obj.question_text_ny:
            status.append('✅ NY')
        return ' '.join(status) if status else '❌ No translations'
    translation_status.short_description = 'Translations'

# --- START OF FULLY CORRECTED ADMIN.PY SECTION ---

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin for individual answer/choice objects."""
    list_display = ['answer_text_short', 'question', 'is_correct', 'order', 'translation_status']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['answer_text', 'answer_text_bem', 'answer_text_ny', 'question__question_text']
    
    fieldsets = (
        ('📝 English Answer (Required)', {
            'fields': ('question', 'answer_text', 'is_correct', 'order')
        }),
        ('🇿🇲 Translations', {
            'fields': ('answer_text_bem', 'answer_text_ny'),
            'classes': ('collapse',),
            'description': 'Add Bemba and Nyanja translations for this answer'
        }),
    )
    
    def answer_text_short(self, obj):
        return obj.answer_text[:50] + '...' if len(obj.answer_text) > 50 else obj.answer_text
    answer_text_short.short_description = 'Answer Text'
    
    def translation_status(self, obj):
        status = []
        if obj.answer_text_bem:
            status.append('✅ BEM')
        if obj.answer_text_ny:
            status.append('✅ NY')
        return ' '.join(status) if status else '❌ No translations'
    translation_status.short_description = 'Translations'

@admin.register(Quiz)
class QuizAdmin(ImportExportModelAdmin):
    resource_class = QuizResource
    list_display = ['title', 'lesson', 'module_display', 'pass_percentage', 'time_limit_minutes', 'max_attempts', 'is_required', 'translation_status']
    list_filter = ['is_required', 'lesson__module__category']
    search_fields = ['title', 'title_bem', 'title_ny', 'lesson__module__title']
    
    fieldsets = (
        ('📍 Quiz Details', {
            'fields': ('lesson', 'is_required', 'pass_percentage', 'max_attempts', 'time_limit_minutes')
        }),
        ('📝 English Content (Required)', {
            'fields': ('title', 'description'),
            'description': 'Enter quiz title and description in English'
        }),
        ('🇿🇲 Bemba Translation', {
            'fields': ('title_bem', 'description_bem'),
            'classes': ('collapse',),
            'description': 'Add Bemba translations'
        }),
        ('🇿🇲 Nyanja Translation', {
            'fields': ('title_ny', 'description_ny'),
            'classes': ('collapse',),
            'description': 'Add Nyanja translations'
        }),
    )

    def module_display(self, obj):
        return obj.lesson.module.title
    module_display.short_description = 'Module'
    
    def translation_status(self, obj):
        status = []
        if obj.title_bem and obj.description_bem:
            status.append('✅ BEM')
        elif obj.title_bem or obj.description_bem:
            status.append('⚠️ BEM')
        
        if obj.title_ny and obj.description_ny:
            status.append('✅ NY')
        elif obj.title_ny or obj.description_ny:
            status.append('⚠️ NY')
        
        return ' '.join(status) if status else '❌ No translations'
    translation_status.short_description = 'Translations'


@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    """Admin for tracking every individual user response to a question."""
    # CORRECTED: Changed 'is_correct' to 'is_correct_display'
    list_display = ['user_display', 'quiz_attempt_display', 'question', 'selected_answer_text', 'is_correct_display']
    
    # CORRECTED: Filter path now uses 'attempt__passed' and 'selected_answer__is_correct'
    list_filter = ['attempt__passed', 'selected_answer__is_correct', 'question__quiz']
    
    # CORRECTED: Search path uses 'attempt__user__username' as per models.py
    search_fields = ['attempt__user__username', 'question__question_text']

    def user_display(self, obj):
        # Uses obj.attempt.user.username as per QuizAttempt model
        return obj.attempt.user.username
    user_display.short_description = 'User'
    
    def quiz_attempt_display(self, obj):
        user = obj.attempt.user.username
        return f"Attempt #{obj.attempt.attempt_number} ({user})"
    quiz_attempt_display.short_description = 'Quiz Attempt'
    
    def selected_answer_text(self, obj):
        # Displays the text for the selected multiple-choice answer
        return obj.selected_answer.answer_text[:50] if obj.selected_answer else (obj.text_response[:50] if obj.text_response else "N/A")
    selected_answer_text.short_description = 'Selected Answer'

    def is_correct_display(self, obj):
        """Determines if the response was correct."""
        # For Multiple Choice/True False: Check if the selected answer is marked as correct
        if obj.selected_answer:
            if obj.selected_answer.is_correct:
                return format_html('<span style="color: green;">Yes</span>')
            return format_html('<span style="color: red;">No</span>')
        
        # For Text Answer: Requires more complex logic, which we can't implement here,
        # but for the admin display, we default to N/A or assume manual review.
        if obj.question.question_type == 'text':
            return format_html('<span style="color: blue;">Manual Review</span>')

        return format_html('<span style="color: orange;">N/A</span>')
    
    is_correct_display.short_description = 'Correct?'
    is_correct_display.boolean = False # Since we are using HTML for color, set to False

# --- END OF FULLY CORRECTED ADMIN.PY SECTION ---

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'progress_percentage', 'enrolled_at', 'completed_at', 'time_spent_display']
    list_filter = ['enrolled_at', 'completed_at', 'module__category']
    search_fields = ['user__username', 'module__title']
    readonly_fields = ['enrolled_at', 'progress_percentage', 'time_spent_minutes']
    date_hierarchy = 'enrolled_at'
    
    def time_spent_display(self, obj):
        hours = obj.time_spent_minutes // 60
        minutes = obj.time_spent_minutes % 60
        return f"{hours}h {minutes}m"
    time_spent_display.short_description = 'Time Spent'


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'lesson', 'is_completed', 'completed_at', 'time_spent_minutes']
    list_filter = ['is_completed', 'completed_at', 'lesson__module__category']
    search_fields = ['enrollment__user__username', 'lesson__title']
    
    def user_display(self, obj):
        return obj.enrollment.user.username
    user_display.short_description = 'User'


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'quiz', 'attempt_number', 'score', 'passed', 'started_at', 'completed_at']
    list_filter = ['passed', 'started_at']
    search_fields = ['enrollment__user__username', 'quiz__title']
    
    def user_display(self, obj):
        return obj.enrollment.user.username if obj.enrollment else obj.user.username
    user_display.short_description = 'User'


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'certificate_id', 'final_score', 'issued_at']
    list_filter = ['issued_at', 'module__category']
    search_fields = ['user__username', 'module__title', 'certificate_id']
    readonly_fields = ['certificate_id', 'issued_at']
    date_hierarchy = 'issued_at'


@admin.register(ModuleReview)
class ModuleReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'rating', 'is_verified_completion', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_verified_completion', 'created_at']
    search_fields = ['user__username', 'module__title', 'review_text']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LearningStreak)
class LearningStreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'total_lessons_completed', 'total_points_earned', 'last_activity_date']
    list_filter = ['last_activity_date']
    search_fields = ['user__username']
    readonly_fields = ['last_activity_date']


@admin.register(Badge)
class BadgeAdmin(ImportExportModelAdmin):
    resource_class = BadgeResource
    list_display = ['name', 'code', 'description', 'icon', 'points_required', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'code': ('name',)}


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    """Admin for tracking badges awarded to users."""
    list_display = ['user', 'badge', 'awarded_at']
    list_filter = ['badge__name', 'awarded_at']
    search_fields = ['user__username', 'badge__name']
    readonly_fields = ['awarded_at']