# elearning/models.py - Optimized for performance with Cloudinary and caching
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db.models import F
from django.utils.text import slugify
from django.core.cache import cache
# # from cloudinary.models import CloudinaryField  # Temporarily disabled  # Temporarily disabled

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    name_bem = models.CharField(max_length=100, blank=True, null=True)
    name_ny = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    description_bem = models.TextField(blank=True, null=True)
    description_ny = models.TextField(blank=True, null=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    icon_class = models.CharField(
        max_length=50, 
        default='fas fa-leaf',
        help_text='FontAwesome icon class (e.g., fas fa-recycle, fas fa-trash)'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    order = models.IntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    color = models.CharField(max_length=7, default='#000000')

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order']
        indexes = [
            models.Index(fields=['is_active', 'order']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.get_translated_name()

    def get_module_count(self):
        return self.modules.count()

    def get_translated_name(self, language='en'):
        if language == 'bem' and self.name_bem:
            return self.name_bem
        elif language == 'ny' and self.name_ny:
            return self.name_ny
        return self.name

    def get_translated_description(self, language='en'):
        if language == 'bem' and self.description_bem:
            return self.description_bem
        elif language == 'ny' and self.description_ny:
            return self.description_ny
        return self.description


class Tag(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    name_bem = models.CharField(max_length=100, blank=True, null=True)
    name_ny = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.get_translated_name()

    def get_translated_name(self, language='en'):
        if language == 'bem' and self.name_bem:
            return self.name_bem
        elif language == 'ny' and self.name_ny:
            return self.name_ny
        return self.name


class Module(models.Model):
    HIERARCHY_CHOICES = [
        ("reduce", "Reduce"),
        ("reuse", "Reuse"),
        ("recycle", "Recycle"),
        ("recover", "Recover"),
        ("dispose", "Dispose"),
    ]

    WASTE_STREAM_CHOICES = [
        ("solid", "Solid Waste"),
        ("hazardous", "Hazardous Waste"),
        ("e_waste", "E-Waste"),
        ("organic", "Organic Waste"),
        ("cnd", "Construction & Demolition"),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200, db_index=True)
    title_bem = models.CharField(max_length=200, blank=True, null=True)
    title_ny = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    description_bem = models.TextField(blank=True, null=True)
    description_ny = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='modules', db_index=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, db_index=True)
    duration_minutes = models.IntegerField(default=0)
    points_reward = models.IntegerField(default=10)
    thumbnail = models.ImageField(upload_to='module_thumbnails/', blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    order = models.IntegerField(default=0, db_index=True)
    hierarchy_stage = models.CharField(max_length=20, choices=HIERARCHY_CHOICES, blank=True)
    waste_stream = models.CharField(max_length=20, choices=WASTE_STREAM_CHOICES, blank=True)
    external_tour_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    slug = models.SlugField(max_length=200, unique=True, null=True, blank=True, db_index=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='modules')
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    is_premium = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)
    views_count = models.IntegerField(default=0, db_index=True)
    enrollments_count = models.IntegerField(default=0, db_index=True)
    completions_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_modules')
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.URLField(blank=True)

    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['is_published', 'is_active']),
            models.Index(fields=['category', 'is_published']),
            models.Index(fields=['difficulty', 'is_published']),
            models.Index(fields=['is_featured', 'enrollments_count']),
            models.Index(fields=['created_at']),
            models.Index(fields=['title']),
            models.Index(fields=['average_rating', 'enrollments_count']),
        ]

    def __str__(self):
        return self.get_translated_title()

    def increment_views(self):
        Module.objects.filter(pk=self.pk).update(views_count=F('views_count') + 1)

    def get_translated_title(self, language='en'):
        if language == 'bem' and self.title_bem:
            return self.title_bem
        elif language == 'ny' and self.title_ny:
            return self.title_ny
        return self.title

    def get_translated_description(self, language='en'):
        if language == 'bem' and self.description_bem:
            return self.description_bem
        elif language == 'ny' and self.description_ny:
            return self.description_ny
        return self.description

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Module.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Lesson(models.Model):
    CONTENT_TYPES = [
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
    ]

    INTERACTIVE_TYPES = [
        ("none", "None"),
        ("sorting", "Sorting Game"),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons', db_index=True)
    title = models.CharField(max_length=200, db_index=True)
    title_bem = models.CharField(max_length=200, blank=True, null=True)
    title_ny = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=200, null=True, blank=True, db_index=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, db_index=True)
    content = models.TextField(blank=True)
    content_bem = models.TextField(blank=True, null=True)
    content_ny = models.TextField(blank=True, null=True)

    # Media Files with Cloudinary - English (default)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)

    # Media Files with Cloudinary - Bemba
    video_file_bem = models.FileField(upload_to='videos/', blank=True, null=True)
    audio_file_bem = models.FileField(upload_to='audio/', blank=True, null=True)

    # Media Files with Cloudinary - Nyanja
    video_file_ny = models.FileField(upload_to='videos/', blank=True, null=True)
    audio_file_ny = models.FileField(upload_to='audio/', blank=True, null=True)

    external_tour_url = models.URLField(blank=True)
    interactive_type = models.CharField(max_length=20, choices=INTERACTIVE_TYPES, default="none")
    interactive_payload = models.JSONField(null=True, blank=True, help_text="JSON config for interactive content")
    duration_minutes = models.IntegerField(default=0)
    order = models.IntegerField(default=0, db_index=True)
    is_required = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_preview = models.BooleanField(default=False, db_index=True)
    is_published = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['module', 'slug']
        indexes = [
            models.Index(fields=['module', 'order']),
            models.Index(fields=['module', 'is_published']),
            models.Index(fields=['is_preview', 'is_published']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.module} - {self.get_translated_title()}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.get_translated_title('en') or f'lesson-{self.order}')
            slug = base_slug
            counter = 1
            while Lesson.objects.filter(module=self.module, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('elearning:lesson_detail', kwargs={
            'module_slug': self.module.slug,
            'lesson_slug': self.slug
        })

    @property
    def next_lesson(self):
        return Lesson.objects.filter(module=self.module, order__gt=self.order).order_by('order').first()

    @property
    def previous_lesson(self):
        return Lesson.objects.filter(module=self.module, order__lt=self.order).order_by('-order').first()

    @property
    def is_first_lesson(self):
        return self.order == self.module.lessons.first().order if self.module.lessons.exists() else True

    @property
    def is_last_lesson(self):
        return self.order == self.module.lessons.last().order if self.module.lessons.exists() else True

    # Translation Methods
    def get_translated_title(self, language='en'):
        if language == 'bem' and self.title_bem:
            return self.title_bem
        elif language == 'ny' and self.title_ny:
            return self.title_ny
        return self.title

    def get_translated_content(self, language='en'):
        if language == 'bem' and self.content_bem:
            return self.content_bem
        elif language == 'ny' and self.content_ny:
            return self.content_ny
        return self.content

    # Dynamic Media Selection
    def get_video_file(self, language='en'):
        """Return appropriate video file based on language"""
        if language == 'bem' and self.video_file_bem:
            return self.video_file_bem
        elif language == 'ny' and self.video_file_ny:
            return self.video_file_ny
        return self.video_file  # fallback to English

    def get_audio_file(self, language='en'):
        """Return appropriate audio file based on language"""
        if language == 'bem' and self.audio_file_bem:
            return self.audio_file_bem
        elif language == 'ny' and self.audio_file_ny:
            return self.audio_file_ny
        return self.audio_file  # fallback to English

    def get_media_url(self, media_type='video', language='en'):
        """Convenience method to get media URL"""
        if media_type == 'video':
            file = self.get_video_file(language)
        elif media_type == 'audio':
            file = self.get_audio_file(language)
        else:
            return None
        return file.url if file else None


# --- Rest of the models remain unchanged but use get_translated_* in __str__ ---

class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    title_bem = models.CharField(max_length=200, blank=True, null=True)
    title_ny = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)
    description_bem = models.TextField(blank=True, null=True)
    description_ny = models.TextField(blank=True, null=True)
    pass_percentage = models.IntegerField(default=70)
    max_attempts = models.IntegerField(default=3)
    passing_score = models.IntegerField(default=70)
    time_limit_minutes = models.IntegerField(default=0)
    is_required = models.BooleanField(default=True)

    def __str__(self):
        return self.get_translated_title()

    def get_translated_title(self, language='en'):
        if language == 'bem' and self.title_bem:
            return self.title_bem
        elif language == 'ny' and self.title_ny:
            return self.title_ny
        return self.title

    def get_translated_description(self, language='en'):
        if language == 'bem' and self.description_bem:
            return self.description_bem
        elif language == 'ny' and self.description_ny:
            return self.description_ny
        return self.description


class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('text', 'Text Answer'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_text_bem = models.TextField(blank=True, null=True)
    question_text_ny = models.TextField(blank=True, null=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    points = models.IntegerField(default=1)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.get_translated_question_text()[:50]}"

    def get_translated_question_text(self, language='en'):
        if language == 'bem' and self.question_text_bem:
            return self.question_text_bem
        elif language == 'ny' and self.question_text_ny:
            return self.question_text_ny
        return self.question_text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=500)
    answer_text_bem = models.CharField(max_length=500, blank=True, null=True)
    answer_text_ny = models.CharField(max_length=500, blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.get_translated_answer_text()

    def get_translated_answer_text(self, language='en'):
        if language == 'bem' and self.answer_text_bem:
            return self.answer_text_bem
        elif language == 'ny' and self.answer_text_ny:
            return self.answer_text_ny
        return self.answer_text


# --- Remaining models (unchanged except __str__ improvements) ---

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.IntegerField(default=0)
    time_spent_minutes = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'module']

    def __str__(self):
        return f"{self.user.username} - {self.module}"


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    lessons_completed = models.ManyToManyField(Lesson, blank=True)
    completion_percentage = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'module']

    def __str__(self):
        return f"{self.user.username} - {self.module} ({self.completion_percentage}%)"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['enrollment', 'lesson']

    def __str__(self):
        return f"{self.enrollment.user.username} - {self.lesson.get_translated_title()}"


class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    passed = models.BooleanField()
    attempt_number = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz} - Attempt {self.attempt_number}"


class QuizResponse(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True)
    text_response = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Response for {self.question}"


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    final_score = models.IntegerField(default=0)

    class Meta:
        unique_together = ['user', 'module']

    def __str__(self):
        return f"Certificate: {self.user.username} - {self.module}"


class ModuleReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review_text = models.TextField(blank=True)
    is_verified_completion = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'module']

    def __str__(self):
        return f"Review: {self.user.username} - {self.module}"


class LearningStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    total_lessons_completed = models.IntegerField(default=0)
    total_points_earned = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Streak for {self.user.username}"


class Role(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name


Module.add_to_class('target_roles', models.ManyToManyField('Role', related_name='modules', blank=True))


class LearningPath(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    for_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class PathModule(models.Model):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='path_modules')
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)

    class Meta:
        unique_together = ("path", "module")
        ordering = ["order"]

    def __str__(self):
        return f"{self.path.name} -> {self.module}"


class PathEnrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "path")

    def __str__(self):
        return f"{self.user.username} in {self.path.name}"


class Badge(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='badge_icons/', blank=True)
    criteria = models.JSONField(null=True, blank=True, help_text="e.g., {type: 'modules_completed', count: 3}")
    points_required = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")

    def __str__(self):
        return f"{self.user.username} -> {self.badge.name}"