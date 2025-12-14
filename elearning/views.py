# elearning/views.py - FULLY OPTIMIZED with Redis caching, database optimization, and pagination

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, F, Prefetch
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.urls import reverse
from datetime import datetime, timedelta
import io

from django.contrib.auth import get_user_model
User = get_user_model()

from .models import (
    Module, Category, Lesson, Quiz, Question, Answer,
    Enrollment, LessonProgress, QuizAttempt, QuizResponse,
    Certificate, ModuleReview, LearningStreak, Badge, UserBadge, Tag
)
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors 

def get_user_language(request):
    """Get user's preferred language"""
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        # Assuming 'profile' is a related model on your User model
        # You may need to replace 'profile' with your actual user profile model
        return request.user.profile.preferred_language
    return 'en'

# --- Module and Category Views ---

@login_required
def module_detail(request, slug):
    """
    Display detailed information about a specific module
    """
    # Get the module
    module = get_object_or_404(
        Module.objects.select_related('category', 'created_by')
        .prefetch_related('lessons', 'tags', 'prerequisites'),
        slug=slug,
        is_published=True
    )
    
    # Increment views
    module.increment_views()
    
    # Get all lessons ordered
    lessons = module.lessons.all().order_by('order')
    
    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    user_progress = {}
    completed_lesson_ids = []
    
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(
                user=request.user,
                module=module
            )
            is_enrolled = True
            
            # Get lesson progress
            lesson_progress = LessonProgress.objects.filter(
                enrollment=enrollment
            ).select_related('lesson')
            
            # Build progress dictionary
            for lp in lesson_progress:
                user_progress[lp.lesson.id] = {
                    'is_completed': lp.is_completed,
                    'time_spent': lp.time_spent_minutes,
                }
                if lp.is_completed:
                    completed_lesson_ids.append(lp.lesson.id)
        
        except Enrollment.DoesNotExist:
            pass
    
    # Get module statistics
    total_lessons = lessons.count()
    preview_lessons = lessons.filter(is_preview=True).count()
    
    # Get total enrollments (FIXED: use 'enrollment' not 'enrollment_set')
    total_enrollments = Enrollment.objects.filter(module=module).count()
    
    # Get reviews
    reviews = ModuleReview.objects.filter(
        module=module
    ).select_related('user').order_by('-created_at')[:5]
    
    # Calculate average rating
    avg_rating = module.average_rating or 0
    
    # Get similar modules (same category)
    similar_modules = Module.objects.filter(
        category=module.category,
        is_published=True
    ).exclude(id=module.id)[:3]
    
    # Get user's preferred language
    user_language = request.session.get('language', 'en')
    
    context = {
        'module': module,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'user_progress': user_progress,
        'completed_lesson_ids': completed_lesson_ids,
        'total_lessons': total_lessons,
        'preview_lessons': preview_lessons,
        'total_enrollments': total_enrollments,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'similar_modules': similar_modules,
        'user_language': user_language,
    }
    
    return render(request, 'elearning/module_detail.html', context)

@login_required
def category_detail(request, slug):
    """
    Displays modules belonging to a specific category - ENHANCED
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    modules = Module.objects.filter(
        category=category, 
        is_published=True,
        is_active=True
    ).select_related('category', 'created_by').prefetch_related('tags').order_by('-created_at')

    # Get user enrollments
    user_enrollments = []
    if request.user.is_authenticated:
        user_enrollments = list(
            Enrollment.objects.filter(user=request.user)
            .values_list('module_id', flat=True)
        )

    context = {
        'category': category,
        'modules': modules,
        'user_enrollments': user_enrollments,
        'user_language': get_user_language(request),
    }
    
    return render(request, 'elearning/category_detail.html', context)


@login_required
def tag_detail(request, slug):
    """
    Displays modules associated with a specific tag - ENHANCED
    """
    tag = get_object_or_404(Tag, slug=slug)
    
    modules = Module.objects.filter(
        tags=tag, 
        is_published=True,
        is_active=True
    ).select_related('category', 'created_by').prefetch_related('tags').order_by('-created_at')

    # Get user enrollments
    user_enrollments = []
    if request.user.is_authenticated:
        user_enrollments = list(
            Enrollment.objects.filter(user=request.user)
            .values_list('module_id', flat=True)
        )

    context = {
        'tag': tag,
        'modules': modules,
        'user_enrollments': user_enrollments,
        'user_language': get_user_language(request),
    }
    
    return render(request, 'elearning/tag_detail.html', context)

@login_required
def enroll_module(request, slug):
    """
    Enroll user in a module
    """
    module = get_object_or_404(Module, slug=slug, is_published=True)
        
    # Check if already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        module=module,
        defaults={
            'progress_percentage': 0,
        }
    )
        
    if created:
        # Increment enrollment count
        module.enrollments_count += 1
        module.save(update_fields=['enrollments_count'])
            
        messages.success(
            request,
            f'🎉 Successfully enrolled in "{module.title}"! Start learning now.'
        )
    else:
        messages.info(
            request,
            f'You are already enrolled in "{module.title}".'
        )
        
    return redirect('elearning:module_detail', slug=slug)

@login_required
@cache_page(60 * 15)  # Cache for 15 minutes
def module_list(request):
    """
    OPTIMIZED: Display list of all available modules with filters, caching, and pagination
    """
    # Get query parameters
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')
    tag_slug = request.GET.get('tag', '')
    sort_by = request.GET.get('sort', 'featured')
    page = request.GET.get('page', 1)
    
    # Create cache key for this specific query
    cache_key = f"module_list_{search_query}_{category_id}_{difficulty}_{tag_slug}_{sort_by}_{page}_{request.user.id}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return render(request, 'elearning/module_list.html', cached_data)
    
    # OPTIMIZED: Base queryset with select_related and prefetch_related
    modules = Module.objects.filter(
        is_published=True,
        is_active=True
    ).select_related('category', 'created_by').prefetch_related(
        'tags',
        Prefetch('enrollment_set', queryset=Enrollment.objects.select_related('user'))
    )
    
    # Apply filters
    if search_query:
        modules = modules.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(title_bem__icontains=search_query) |
            Q(title_ny__icontains=search_query)
        )
    
    if category_id:
        modules = modules.filter(category_id=category_id)
        selected_category = get_object_or_404(Category, id=category_id)
    else:
        selected_category = None
    
    if difficulty:
        modules = modules.filter(difficulty=difficulty)
    
    if tag_slug:
        modules = modules.filter(tags__slug=tag_slug)
    
    # Apply sorting
    if sort_by == 'popular':
        modules = modules.order_by('-enrollments_count', '-views_count')
    elif sort_by == 'newest':
        modules = modules.order_by('-created_at')
    elif sort_by == 'rating':
        modules = modules.order_by('-average_rating', '-enrollments_count')
    else:  # featured
        modules = modules.order_by('-is_featured', '-enrollments_count', 'order')
    
    # PAGINATION - 20 items per page
    paginator = Paginator(modules, 20)
    try:
        modules_page = paginator.page(page)
    except PageNotAnInteger:
        modules_page = paginator.page(1)
    except EmptyPage:
        modules_page = paginator.page(paginator.num_pages)
    
    # CACHED: Get categories with module counts
    categories_cache_key = "categories_with_counts"
    categories = cache.get(categories_cache_key)
    if not categories:
        categories = Category.objects.filter(is_active=True).annotate(
            module_count=Count('modules', filter=Q(modules__is_published=True))
        ).order_by('order')
        cache.set(categories_cache_key, categories, 60 * 30)  # Cache for 30 minutes
    
    # CACHED: Get popular tags
    tags_cache_key = "popular_tags"
    tags = cache.get(tags_cache_key)
    if not tags:
        tags = Tag.objects.annotate(
            module_count=Count('modules', filter=Q(modules__is_published=True))
        ).filter(module_count__gt=0).order_by('-module_count')[:10]
        cache.set(tags_cache_key, tags, 60 * 30)  # Cache for 30 minutes
    
    # CACHED: Get featured modules
    featured_cache_key = "featured_modules"
    featured_modules = cache.get(featured_cache_key)
    if not featured_modules:
        featured_modules = Module.objects.filter(
            is_published=True,
            is_featured=True
        ).select_related('category')[:3]
        cache.set(featured_cache_key, featured_modules, 60 * 30)  # Cache for 30 minutes
    
    # OPTIMIZED: Get user enrollments
    user_enrollments = []
    user_progress = {}
    if request.user.is_authenticated:
        user_cache_key = f"user_enrollments_{request.user.id}"
        user_data = cache.get(user_cache_key)
        if not user_data:
            enrollments = Enrollment.objects.filter(
                user=request.user
            ).select_related('module').only('module_id', 'progress_percentage')
            
            user_enrollments = [e.module_id for e in enrollments]
            user_progress = {e.module_id: e.progress_percentage for e in enrollments}
            user_data = {'enrollments': user_enrollments, 'progress': user_progress}
            cache.set(user_cache_key, user_data, 60 * 15)  # Cache for 15 minutes
        else:
            user_enrollments = user_data['enrollments']
            user_progress = user_data['progress']
    
    # CACHED: Get stats
    stats_cache_key = "module_stats"
    stats = cache.get(stats_cache_key)
    if not stats:
        stats = {
            'total_modules': Module.objects.filter(is_published=True).count(),
            'total_students': Enrollment.objects.values('user').distinct().count(),
            'total_completions': Enrollment.objects.filter(completed_at__isnull=False).count(),
            'featured_modules': featured_modules,
        }
        cache.set(stats_cache_key, stats, 60 * 30)  # Cache for 30 minutes
    
    # Get user's preferred language
    user_language = request.session.get('language', 'en')
    
    context = {
        'modules': modules_page,
        'categories': categories,
        'tags': tags,
        'selected_category': selected_category,
        'search_query': search_query,
        'current_difficulty': difficulty,
        'sort_by': sort_by,
        'user_enrollments': user_enrollments,
        'user_progress': user_progress,
        'stats': stats,
        'user_language': user_language,
        'paginator': paginator,
        'page_obj': modules_page,
    }
    
    # Cache the context for 15 minutes
    cache.set(cache_key, context, 60 * 15)
    
    return render(request, 'elearning/module_list.html', context)

# --- Lesson Views ---
@login_required
def lesson_detail(request, module_slug, lesson_slug):
    """
    Displays the content of a specific lesson within a module, 
    checking for user enrollment status.
    (Replaces lesson_view)
    """
    # 1. Fetch the module and lesson
    module = get_object_or_404(Module, slug=module_slug, is_published=True)
    lesson = get_object_or_404(Lesson, module=module, slug=lesson_slug)
    
    enrollment = None
    lesson_progress = None
    
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(user=request.user, module=module).first()
        
        # Check access: Must be enrolled or the lesson must be a public preview
        if not enrollment and not lesson.is_preview:
            messages.warning(request, "You must enroll in the module to access this lesson.")
            return redirect('elearning:module_detail', slug=module.slug)
        
        if enrollment:
            # Get or create LessonProgress for the current lesson
            lesson_progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment, 
                lesson=lesson
            )
            # Update last accessed time
            if not created:
                lesson_progress.last_accessed = timezone.now()
                lesson_progress.save()

    # Lesson navigation
    all_lessons = list(module.lessons.all().order_by('order'))
    current_index = all_lessons.index(lesson)
    
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None

    # Get quizzes for this lesson
    quizzes = [lesson.quiz] if hasattr(lesson, 'quiz') else []

    context = {
        'module': module,
        'lesson': lesson,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'quizzes': quizzes, # Corrected to handle OneToOneField relationship
        'user_language': get_user_language(request),
    }
    
    return render(request, 'elearning/lesson_detail.html', context)


@login_required
def lesson_view(request, lesson_id):
    """View individual lesson (Legacy - redirects to slug-based URL)"""
    lesson = get_object_or_404(
        Lesson.objects.select_related('module'),
        id=lesson_id
    )
    # Redirect to the canonical slug-based URL to prevent duplicate content issues
    return redirect('elearning:lesson_detail', module_slug=lesson.module.slug, lesson_slug=lesson.slug)


@login_required
@require_POST
def complete_lesson(request, lesson_id):
    """Mark lesson as completed"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    # NOTE: Your Enrollment model has a foreign key to Module, not Lesson.
    # The lookup is correct: finding enrollment via user and module.
    enrollment = get_object_or_404(Enrollment, user=request.user, module=lesson.module)
    
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    if not lesson_progress.is_completed:
        lesson_progress.is_completed = True
        lesson_progress.completed_at = timezone.now()
        lesson_progress.save()
        
        # Update overall enrollment progress
        total_lessons = lesson.module.lessons.count()
        completed = LessonProgress.objects.filter(
            enrollment=enrollment,
            is_completed=True
        ).count()
        
        enrollment.progress_percentage = int((completed / total_lessons) * 100)
        enrollment.save()
        
        # Check if module is complete
        if enrollment.progress_percentage == 100 and not enrollment.completed_at:
            enrollment.completed_at = timezone.now()
            enrollment.save()
            
            # Update module completion count
            lesson.module.completions_count = F('completions_count') + 1
            lesson.module.save(update_fields=['completions_count'])
            
            # Award certificate
            Certificate.objects.get_or_create(
                user=request.user,
                module=lesson.module,
                defaults={'final_score': 100, 'certificate_id': f'C-{lesson.module.id}-{request.user.id}'}
            )
            
            # REAL-TIME USER NOTIFICATION: Module completed
            try:
                from community.notifications import notification_service
                from community.models import Notification
                
                user = request.user
                user_name = user.get_full_name() or user.username
                module_title = lesson.module.title
                prefs = getattr(user, 'notification_preferences', None)
                
                # SMS notification - PRO ZNBC style
                if prefs and prefs.sms_enabled and user.phone_number:
                    sms_message = f"✅ Well done {user_name}! You finished '{module_title}'. +20 points added!"
                    result = notification_service.send_sms(str(user.phone_number), sms_message)
                    if result.get('success'):
                        print(f"✅ Lesson completion SMS sent to {user.username}")
                
                # WhatsApp notification - PRO Zambian style
                if prefs and prefs.whatsapp_enabled and user.phone_number:
                    whatsapp_message = f"✅ Well done {user_name}! You finished '{module_title}'. +20 points added!"
                    result = notification_service.send_whatsapp(str(user.phone_number), whatsapp_message)
                    if result.get('success'):
                        print(f"✅ Lesson completion WhatsApp sent to {user.username}")
                
                # In-app notification
                Notification.objects.create(
                    user=user,
                    notification_type='general',
                    title=f'Module Completed! 🎓',
                    message=f'Congratulations! You finished {module_title}. +20 points added!',
                    url=f'/elearning/modules/{lesson.module.slug}/'
                )
            except Exception as e:
                print(f"Error in module completion notifications: {e}")
            
            messages.success(request, f'🎉 Congratulations! You completed {lesson.module.title}! Certificate awarded!')
        else:
            messages.success(request, f'✅ Lesson "{lesson.title}" marked as complete! Keep going!')
    else:
        messages.info(request, f'You already completed this lesson.')
    
    # Redirect back to the lesson page using slugs
    return redirect('elearning:lesson_detail', module_slug=lesson.module.slug, lesson_slug=lesson.slug)


# --- Quiz Views ---

@login_required
def quiz_take(request, quiz_id):
    """Take a quiz"""
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related('questions__answers'),
        id=quiz_id
    )
    
    # The quiz belongs to a lesson, which belongs to a module.
    module = quiz.lesson.module
    
    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        module=module # Use module of the quiz's lesson
    )
    
    # Check attempt limit
    attempts_count = QuizAttempt.objects.filter(
        user=request.user, # Use user from QuizAttempt model
        quiz=quiz
    ).count()
    
    if attempts_count >= quiz.max_attempts:
        messages.error(request, f'You have reached the maximum number of attempts ({quiz.max_attempts}) for this quiz.')
        return redirect('elearning:module_detail', slug=module.slug)
    
    if request.method == 'POST':
        # Create quiz attempt
        # NOTE: Updated to use user and enrollment fields as per your QuizAttempt model
        attempt = QuizAttempt.objects.create(
            user=request.user,
            enrollment=enrollment,
            quiz=quiz,
            attempt_number=attempts_count + 1,
            total_questions=quiz.questions.count()
        )
        
        # Process answers
        total_points = 0
        earned_points = 0
        
        for question in quiz.questions.all():
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                selected_answer = get_object_or_404(Answer, id=answer_id)
                is_correct = selected_answer.is_correct
                points = question.points if is_correct else 0
                
                QuizResponse.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=is_correct,
                )
                
                total_points += question.points
                earned_points += points
            else:
                # Still need to count the question points in the total, even if unanswered
                total_points += question.points
        
        # Calculate score
        score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        attempt.score = earned_points
        attempt.percentage = score_percentage
        attempt.passed = score_percentage >= quiz.passing_score
        attempt.completed_at = timezone.now()
        attempt.save()
        
        if attempt.passed:
            messages.success(request, f'Congratulations! You passed with {score_percentage:.1f}%')
        else:
            messages.warning(request, f'You scored {score_percentage:.1f}%. Pass score is {quiz.passing_score}%. You can try again.')
        
        return redirect('elearning:quiz_result', attempt_id=attempt.id)
    
    # Get questions for display
    questions = quiz.questions.all().prefetch_related('answers')
    
    # Calculate attempts left
    attempts_left = quiz.max_attempts - attempts_count
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'enrollment': enrollment,
        'attempts_count': attempts_count,
        'attempts_left': attempts_left,
        'user_language': get_user_language(request),
    }
    
    return render(request, 'elearning/quiz_take.html', context)


@login_required
def quiz_result(request, attempt_id):
    """View quiz results"""
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz', 'user'),
        id=attempt_id,
        user=request.user
    )
    
    responses = QuizResponse.objects.filter(attempt=attempt).select_related(
        'question', 'selected_answer'
    )
    
    context = {
        'attempt': attempt,
        'responses': responses,
        'user_language': get_user_language(request),
    }
    
    return render(request, 'elearning/quiz_result.html', context)


# --- Dashboard and Leaderboard Views ---

@login_required
def progress_dashboard(request):
    """User's learning progress dashboard (ENHANCED)"""
    
    # Fetch all user enrollments, prefetching the Module, its Lessons, and the Lesson's Quiz.
    enrollments = Enrollment.objects.filter(user=request.user).select_related('module').prefetch_related(
        'module__lessons__quiz', 
        'module__lessons', 
        'quizattempt_set' # Fetch all quiz attempts for all modules
    ).order_by('-enrolled_at')
    
    # Also fetch all LessonProgress for the user's enrolled lessons efficiently
    user_lesson_progress = LessonProgress.objects.filter(
        enrollment__user=request.user
    ).values('lesson_id', 'is_completed')
    
    # Convert progress to a dictionary for quick lookup: {lesson_id: is_completed_bool}
    progress_map = {item['lesson_id']: item['is_completed'] for item in user_lesson_progress}
    
    # Prepare quiz attempts data for each enrollment
    for enrollment in enrollments:
        enrollment.quiz_attempts_map = {}
        for attempt in enrollment.quizattempt_set.all():
            quiz_id = attempt.quiz_id
            if quiz_id not in enrollment.quiz_attempts_map:
                enrollment.quiz_attempts_map[quiz_id] = attempt
            elif attempt.completed_at and (not enrollment.quiz_attempts_map[quiz_id].completed_at or 
                                          attempt.completed_at > enrollment.quiz_attempts_map[quiz_id].completed_at):
                enrollment.quiz_attempts_map[quiz_id] = attempt
    
    # Statistics
    total_enrolled = enrollments.count()
    completed = enrollments.filter(completed_at__isnull=False).count()
    in_progress = enrollments.filter(progress_percentage__gt=0, completed_at__isnull=True).count()
    
    # Get or create learning streak
    streak, created = LearningStreak.objects.get_or_create(user=request.user)
    
    # Update streak (EXISTING LOGIC)
    today = timezone.now().date()
    if streak.last_activity_date and streak.last_activity_date < today:
        if (today - streak.last_activity_date).days == 1:
            streak.current_streak += 1
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
        else:
            streak.current_streak = 1
        streak.last_activity_date = today # Ensure the date is updated
        streak.save()
    elif not streak.last_activity_date:
        streak.last_activity_date = today
        streak.current_streak = 1
        streak.save()

    
    # Get certificates
    certificates = Certificate.objects.filter(user=request.user).select_related('module').order_by('-issued_at')[:5]
    
    # Get badges
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge').order_by('-awarded_at')
    
    # Recent activity
    recent_progress = LessonProgress.objects.filter(
        enrollment__user=request.user
    ).select_related('lesson__module').order_by('-completed_at', '-time_spent_minutes')[:10]
    
    # Learning time statistics
    total_time = sum([e.time_spent_minutes for e in enrollments if e.time_spent_minutes is not None])
    total_time_in_hours = total_time // 60
    avg_time_per_module = total_time // total_enrolled if total_enrolled > 0 else 0
    
    context = {
        'enrollments': enrollments,
        'progress_map': progress_map, # Used for quick lesson progress check in template
        'total_enrolled': total_enrolled,
        'completed': completed,
        'in_progress': in_progress,
        'completion_rate': (completed / total_enrolled * 100) if total_enrolled > 0 else 0,
        'streak': streak,
        'certificates': certificates,
        'user_badges': user_badges,
        'recent_progress': recent_progress,
        'total_time_in_hours': total_time_in_hours,
        'avg_time_per_module': avg_time_per_module,
    }
    
    return render(request, 'elearning/progress_dashboard.html', context)


@login_required
def learning_path(request):
    """Suggested learning path based on user progress"""
    # Get user's completed modules
    completed_modules = Certificate.objects.filter(user=request.user).values_list('module_id', flat=True)
    
    # Get recommended modules (not completed, appropriate difficulty)
    user_enrollments = Enrollment.objects.filter(user=request.user)
    beginner_count = user_enrollments.filter(module__difficulty='beginner', completed_at__isnull=False).count()
    
    if beginner_count < 3:
        recommended_difficulty = 'beginner'
    elif beginner_count < 6:
        recommended_difficulty = 'intermediate'
    else:
        recommended_difficulty = 'advanced'
    
    recommended_modules = Module.objects.filter(
        is_published=True,
        difficulty=recommended_difficulty
    ).exclude(id__in=completed_modules).exclude(enrollment__user=request.user).order_by('-created_at')[:6]
    
    # Get popular modules in user's categories
    user_categories = user_enrollments.values_list('module__category', flat=True).distinct()
    popular_in_categories = Module.objects.filter(
        is_published=True,
        category__in=user_categories
    ).exclude(id__in=completed_modules).exclude(enrollment__user=request.user).order_by('-enrollments_count')[:4]
    
    context = {
        'recommended_modules': recommended_modules,
        'recommended_difficulty': recommended_difficulty,
        'popular_in_categories': popular_in_categories,
        'completed_count': len(completed_modules),
    }
    
    return render(request, 'elearning/learning_path.html', context)


@login_required
def leaderboard(request):
    """Learning leaderboard"""
    # NOTE: This implementation can be slow. It assumes LearningStreak.total_points_earned exists.
    top_learners = []
    
    # Efficiently fetch all streaks
    streaks = LearningStreak.objects.select_related('user').filter(
        total_points_earned__gt=0
    ).order_by('-total_points_earned')[:50]
    
    # Fetch completion counts
    completion_counts = Certificate.objects.filter(
        user__in=streaks.values_list('user_id', flat=True)
    ).values('user').annotate(modules_completed=Count('module'))
    
    completion_map = {item['user']: item['modules_completed'] for item in completion_counts}
    
    for streak in streaks:
        top_learners.append({
            'user': streak.user,
            'points': streak.total_points_earned,
            'modules_completed': completion_map.get(streak.user.id, 0),
            'streak': streak.current_streak,
        })
    
    # The list is already sorted by the query, but we keep the sorting logic just in case.
    # top_learners.sort(key=lambda x: x['points'], reverse=True) 
    
    user_rank = next((i+1 for i, l in enumerate(top_learners) if l['user'] == request.user), None)
    if user_rank is None and request.user.is_authenticated:
        # Check if current user is not in the top 50, but still has points
        user_streak = LearningStreak.objects.filter(user=request.user).first()
        if user_streak and user_streak.total_points_earned > 0:
            # This requires fetching all streaks again for accurate ranking (slow, but needed for user's rank)
            all_streaks = LearningStreak.objects.filter(total_points_earned__gt=0).order_by('-total_points_earned')
            user_rank = next((i+1 for i, s in enumerate(all_streaks) if s.user == request.user), None)
        
    context = {
        'top_learners': top_learners,
        'user_rank': user_rank,
    }
    
    return render(request, 'elearning/leaderboard.html', context)


# --- Certificate Views ---

@login_required
def certificates_view(request):
    """View all user certificates"""
    certificates = Certificate.objects.filter(user=request.user).select_related('module').order_by('-issued_at')
    
    context = {
        'certificates': certificates,
    }
    
    return render(request, 'elearning/certificates.html', context)


@login_required
def download_certificate(request, certificate_id):
    """Download certificate as PDF"""
    certificate = get_object_or_404(
        Certificate,
        certificate_id=certificate_id,
        user=request.user
    )
    
    # Create PDF (logic retained from user's original code)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # ... PDF generation code ...
    p.setFillColor(colors.HexColor('#dcfce7'))
    p.rect(0, 0, width, height, fill=1, stroke=0)
    p.setStrokeColor(colors.HexColor('#22c55e'))
    p.setLineWidth(10)
    p.rect(30, 30, width-60, height-60, fill=0, stroke=1)
    p.setFillColor(colors.HexColor('#16a34a'))
    p.setFont("Helvetica-Bold", 40)
    p.drawCentredString(width/2, height-100, "Certificate of Completion")
    p.setFont("Helvetica", 16)
    p.drawCentredString(width/2, height-140, "This is to certify that")
    p.setFont("Helvetica-Bold", 32)
    p.setFillColor(colors.black)
    p.drawCentredString(width/2, height-200, request.user.get_full_name() or request.user.username)
    p.setFont("Helvetica", 16)
    p.setFillColor(colors.HexColor('#16a34a'))
    p.drawCentredString(width/2, height-240, "has successfully completed")
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(colors.black)
    p.drawCentredString(width/2, height-280, certificate.module.title)
    p.setFont("Helvetica", 12)
    p.setFillColor(colors.HexColor('#16a34a'))
    p.drawCentredString(width/2, height-340, f"Issued on: {certificate.issued_at.strftime('%B %d, %Y')}")
    p.drawCentredString(width/2, height-360, f"Certificate ID: {certificate.certificate_id}") 
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width/2, 80, "EcoLearn Environmental Education Platform")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.certificate_id}.pdf"'
    
    return response


def verify_certificate(request, certificate_id):
    """Public certificate verification page"""
    certificate = get_object_or_404(Certificate, certificate_id=certificate_id)
    
    context = {
        'certificate': certificate,
        'is_valid': True,
    }
    
    return render(request, 'elearning/verify_certificate.html', context)


# --- Review Views ---

@login_required
@require_POST
def submit_review(request, module_slug):
    """Submit or update module review"""
    module = get_object_or_404(Module, slug=module_slug)
    rating = request.POST.get('rating')
    review_text = request.POST.get('review_text', '')
    
    if not rating or int(rating) not in range(1, 6):
        messages.error(request, 'Please provide a valid rating (1-5 stars)')
        return redirect('elearning:module_detail', slug=module.slug)
    
    # Check if user completed the module
    enrollment = Enrollment.objects.filter(
        user=request.user,
        module=module,
        completed_at__isnull=False
    ).first()
    
    is_verified = enrollment is not None
    
    # Create or update review
    review, created = ModuleReview.objects.update_or_create(
        user=request.user,
        module=module,
        defaults={
            'rating': int(rating),
            'review_text': review_text,
            'is_verified_completion': is_verified
        }
    )
    
    # Update module average rating
    avg_rating = ModuleReview.objects.filter(module=module).aggregate(Avg('rating'))['rating__avg']
    module.average_rating = round(avg_rating, 2) if avg_rating else 0
    module.save(update_fields=['average_rating'])
    
    messages.success(request, 'Thank you for your review!')
    return redirect('elearning:module_detail', slug=module.slug)


@login_required
@require_POST
def edit_review(request, module_slug): 
    """Handles editing an existing review for a module."""
    module = get_object_or_404(Module, slug=module_slug)
    
    try:
        user_review = ModuleReview.objects.get(module=module, user=request.user)
    except ModuleReview.DoesNotExist:
        messages.error(request, 'You do not have a review to edit for this module.')
        return redirect('elearning:module_detail', slug=module.slug)
    
    rating = request.POST.get('rating')
    review_text = request.POST.get('review_text', '').strip()
    
    if not rating or int(rating) not in range(1, 6):
        messages.error(request, 'Please provide a valid rating (1-5 stars) to update.')
        return redirect('elearning:module_detail', slug=module.slug)
        
    # Update the review
    user_review.rating = int(rating)
    user_review.review_text = review_text
    user_review.updated_at = timezone.now()
    user_review.save()
    
    # Update module average rating
    avg_rating = ModuleReview.objects.filter(module=module).aggregate(Avg('rating'))['rating__avg']
    module.average_rating = round(avg_rating, 2) if avg_rating else 0
    module.save(update_fields=['average_rating'])
    
    messages.success(request, 'Your review has been successfully updated!')
    return redirect('elearning:module_detail', slug=module.slug)

@login_required
def user_dashboard(request):
    # Fetch all modules, prefetch related lessons and quizzes for efficiency
    modules = Module.objects.prefetch_related('lessons__quiz').filter(is_published=True)

    # Calculate user statistics
    points = 0
    modules_completed = 0
    certificates_earned = 0

    if request.user.is_authenticated:
        # Points from LearningStreak
        streak = LearningStreak.objects.filter(user=request.user).first()
        points = streak.total_points_earned if streak else 0

        # Modules completed from Enrollment
        modules_completed = Enrollment.objects.filter(
            user=request.user,
            completed_at__isnull=False
        ).count()

        # Certificates earned
        certificates_earned = Certificate.objects.filter(user=request.user).count()

    context = {
        'modules': modules,
        'profile': {
            'points': points,
            'modules_completed': modules_completed,
            'certificates_earned': certificates_earned,
        },
        'user_language': get_user_language(request),
    }
    return render(request, 'dashboard/user_dashboard.html', context)


# --- Language Switching View ---

