# elearning/views_optimized.py - Performance optimized views with caching and pagination
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, F, Prefetch
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from datetime import datetime, timedelta
import io

from .models import (
    Module, Category, Lesson, Quiz, Question, Answer,
    Enrollment, LessonProgress, QuizAttempt, QuizResponse,
    Certificate, ModuleReview, LearningStreak, Badge, UserBadge, Tag
)

# Cache timeout settings
CACHE_TTL = getattr(settings, 'CACHE_TTL', {})
VIEW_CACHE_TTL = CACHE_TTL.get('views', 900)  # 15 minutes
QUERY_CACHE_TTL = CACHE_TTL.get('queries', 1800)  # 30 minutes

def get_user_language(request):
    """Get user's preferred language with caching"""
    if not request.user.is_authenticated:
        return 'en'
    
    cache_key = f'user_language_{request.user.id}'
    language = cache.get(cache_key)
    
    if language is None:
        if hasattr(request.user, 'profile'):
            language = request.user.profile.preferred_language
        else:
            language = 'en'
        cache.set(cache_key, language, 3600)  # Cache for 1 hour
    
    return language

@login_required
def module_detail(request, slug):
    """
    Display detailed information about a specific module - OPTIMIZED
    """
    # Cache key for this module
    cache_key = f'module_detail_{slug}_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data and not settings.DEBUG:
        return render(request, 'elearning/module_detail.html', cached_data)
    
    # Optimized query with select_related and prefetch_related
    module = get_object_or_404(
        Module.objects.select_related('category', 'created_by')
        .prefetch_related(
            'lessons__quiz',
            'tags',
            'prerequisites',
            Prefetch('lessons', queryset=Lesson.objects.order_by('order'))
        ),
        slug=slug,
        is_published=True
    )
    
    # Increment views atomically
    Module.objects.filter(pk=module.pk).update(views_count=F('views_count') + 1)
    
    # Get lessons with optimized query
    lessons = module.lessons.all()
    
    # Check enrollment and progress
    is_enrolled = False
    enrollment = None
    user_progress = {}
    completed_lesson_ids = []
    
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.select_related('module').filter(
            user=request.user, module=module
        ).first()
        
        if enrollment:
            is_enrolled = True
            # Optimized progress query
            lesson_progress = LessonProgress.objects.filter(
                enrollment=enrollment
            ).select_related('lesson').values(
                'lesson_id', 'is_completed', 'time_spent_minutes'
            )
            
            for lp in lesson_progress:
                user_progress[lp['lesson_id']] = {
                    'is_completed': lp['is_completed'],
                    'time_spent': lp['time_spent_minutes'],
                }
                if lp['is_completed']:
                    completed_lesson_ids.append(lp['lesson_id'])
    
    # Get module statistics
    total_lessons = lessons.count()
    preview_lessons = lessons.filter(is_preview=True).count()
    
    # Cached enrollment count
    enrollment_cache_key = f'module_enrollments_{module.id}'
    total_enrollments = cache.get(enrollment_cache_key)
    if total_enrollments is None:
        total_enrollments = Enrollment.objects.filter(module=module).count()
        cache.set(enrollment_cache_key, total_enrollments, QUERY_CACHE_TTL)
    
    # Get recent reviews with limit
    reviews = ModuleReview.objects.filter(
        module=module
    ).select_related('user').order_by('-created_at')[:5]
    
    # Get similar modules (cached)
    similar_cache_key = f'similar_modules_{module.category_id}'
    similar_modules = cache.get(similar_cache_key)
    if similar_modules is None:
        similar_modules = list(Module.objects.filter(
            category=module.category,
            is_published=True
        ).exclude(id=module.id).select_related('category')[:3])
        cache.set(similar_cache_key, similar_modules, QUERY_CACHE_TTL)
    
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
        'avg_rating': module.average_rating or 0,
        'similar_modules': similar_modules,
        'user_language': get_user_language(request),
    }
    
    # Cache the context for 15 minutes
    cache.set(cache_key, context, VIEW_CACHE_TTL)
    
    return render(request, 'elearning/module_detail.html', context)

@login_required
def module_list(request):
    """
    Display paginated list of modules with filters - OPTIMIZED
    """
    # Get query parameters
    search_query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    difficulty = request.GET.get('difficulty', '')
    tag_slug = request.GET.get('tag', '')
    sort_by = request.GET.get('sort', 'featured')
    page = request.GET.get('page', 1)
    
    # Create cache key based on filters
    cache_key = f'module_list_{search_query}_{category_id}_{difficulty}_{tag_slug}_{sort_by}_{page}_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data and not settings.DEBUG:
        return render(request, 'elearning/module_list.html', cached_data)
    
    # Optimized base queryset
    modules = Module.objects.filter(
        is_published=True,
        is_active=True
    ).select_related('category', 'created_by').prefetch_related('tags')
    
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
    
    # Apply sorting with database indexes
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
    
    # Get categories with module counts (cached)
    categories_cache_key = 'module_categories_with_counts'
    categories = cache.get(categories_cache_key)
    if categories is None:
        categories = Category.objects.filter(is_active=True).annotate(
            module_count=Count('modules', filter=Q(modules__is_published=True))
        ).order_by('order')
        cache.set(categories_cache_key, categories, QUERY_CACHE_TTL)
    
    # Get popular tags (cached)
    tags_cache_key = 'popular_tags'
    tags = cache.get(tags_cache_key)
    if tags is None:
        tags = Tag.objects.annotate(
            module_count=Count('modules', filter=Q(modules__is_published=True))
        ).filter(module_count__gt=0).order_by('-module_count')[:10]
        cache.set(tags_cache_key, tags, QUERY_CACHE_TTL)
    
    # Get user enrollments efficiently
    user_enrollments = []
    user_progress = {}
    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(
            user=request.user
        ).select_related('module').values('module_id', 'progress_percentage')
        
        user_enrollments = [e['module_id'] for e in enrollments]
        user_progress = {e['module_id']: e['progress_percentage'] for e in enrollments}
    
    # Get stats (cached)
    stats_cache_key = 'module_stats'
    stats = cache.get(stats_cache_key)
    if stats is None:
        stats = {
            'total_modules': Module.objects.filter(is_published=True).count(),
            'total_students': Enrollment.objects.values('user').distinct().count(),
            'total_completions': Enrollment.objects.filter(completed_at__isnull=False).count(),
        }
        cache.set(stats_cache_key, stats, QUERY_CACHE_TTL)
    
    # Get featured modules (cached)
    featured_cache_key = 'featured_modules'
    featured_modules = cache.get(featured_cache_key)
    if featured_modules is None:
        featured_modules = list(Module.objects.filter(
            is_published=True,
            is_featured=True
        ).select_related('category')[:3])
        cache.set(featured_cache_key, featured_modules, QUERY_CACHE_TTL)
    
    stats['featured_modules'] = featured_modules
    
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
        'user_language': get_user_language(request),
        'paginator': paginator,
        'page_obj': modules_page,
    }
    
    # Cache for 15 minutes
    cache.set(cache_key, context, VIEW_CACHE_TTL)
    
    return render(request, 'elearning/module_list.html', context)

@login_required
def lesson_detail(request, module_slug, lesson_slug):
    """
    Display lesson content with optimized queries - OPTIMIZED
    """
    # Optimized queries with select_related
    module = get_object_or_404(
        Module.objects.select_related('category'),
        slug=module_slug, 
        is_published=True
    )
    
    lesson = get_object_or_404(
        Lesson.objects.select_related('module'),
        module=module, 
        slug=lesson_slug
    )
    
    enrollment = None
    lesson_progress = None
    
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(
            user=request.user, 
            module=module
        ).select_related('module').first()
        
        # Check access
        if not enrollment and not lesson.is_preview:
            messages.warning(request, "You must enroll in the module to access this lesson.")
            return redirect('elearning:module_detail', slug=module.slug)
        
        if enrollment:
            lesson_progress, created = LessonProgress.objects.get_or_create(
                enrollment=enrollment, 
                lesson=lesson
            )
            if not created:
                lesson_progress.last_accessed = timezone.now()
                lesson_progress.save(update_fields=['last_accessed'])

    # Optimized lesson navigation
    cache_key = f'lesson_navigation_{module.id}'
    all_lessons = cache.get(cache_key)
    if all_lessons is None:
        all_lessons = list(module.lessons.all().order_by('order').values('id', 'slug', 'title', 'order'))
        cache.set(cache_key, all_lessons, QUERY_CACHE_TTL)
    
    current_lesson = next((l for l in all_lessons if l['slug'] == lesson_slug), None)
    current_index = all_lessons.index(current_lesson) if current_lesson else 0
    
    prev_lesson = all_lessons[current_index - 1] if current_index > 0 else None
    next_lesson = all_lessons[current_index + 1] if current_index < len(all_lessons) - 1 else None

    context = {
        'module': module,
        'lesson': lesson,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'user_language': get_user_language(request),
    }
    
    return render(request, 'elearning/lesson_detail.html', context)

@login_required
def progress_dashboard(request):
    """
    User's learning progress dashboard - OPTIMIZED with pagination
    """
    cache_key = f'progress_dashboard_{request.user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data and not settings.DEBUG:
        return render(request, 'elearning/progress_dashboard.html', cached_data)
    
    # Optimized enrollments query
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('module__category').prefetch_related(
        'module__lessons',
        'quizattempt_set__quiz'
    ).order_by('-enrolled_at')
    
    # Pagination for enrollments
    paginator = Paginator(enrollments, 10)
    page = request.GET.get('page', 1)
    try:
        enrollments_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        enrollments_page = paginator.page(1)
    
    # Optimized lesson progress query
    user_lesson_progress = LessonProgress.objects.filter(
        enrollment__user=request.user
    ).values('lesson_id', 'is_completed')
    
    progress_map = {item['lesson_id']: item['is_completed'] for item in user_lesson_progress}
    
    # Statistics
    total_enrolled = enrollments.count()
    completed = enrollments.filter(completed_at__isnull=False).count()
    in_progress = enrollments.filter(progress_percentage__gt=0, completed_at__isnull=True).count()
    
    # Learning streak
    streak, created = LearningStreak.objects.get_or_create(user=request.user)
    
    # Update streak logic
    today = timezone.now().date()
    if streak.last_activity_date and streak.last_activity_date < today:
        if (today - streak.last_activity_date).days == 1:
            streak.current_streak += 1
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
        else:
            streak.current_streak = 1
        streak.last_activity_date = today
        streak.save()
    elif not streak.last_activity_date:
        streak.last_activity_date = today
        streak.current_streak = 1
        streak.save()
    
    # Recent certificates and badges
    certificates = Certificate.objects.filter(
        user=request.user
    ).select_related('module').order_by('-issued_at')[:5]
    
    user_badges = UserBadge.objects.filter(
        user=request.user
    ).select_related('badge').order_by('-awarded_at')[:10]
    
    # Recent activity
    recent_progress = LessonProgress.objects.filter(
        enrollment__user=request.user
    ).select_related('lesson__module').order_by('-completed_at')[:10]
    
    # Time statistics
    total_time = sum([e.time_spent_minutes for e in enrollments if e.time_spent_minutes])
    total_time_in_hours = total_time // 60
    avg_time_per_module = total_time // total_enrolled if total_enrolled > 0 else 0
    
    context = {
        'enrollments': enrollments_page,
        'progress_map': progress_map,
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
        'paginator': paginator,
        'page_obj': enrollments_page,
    }
    
    # Cache for 10 minutes (shorter for dashboard)
    cache.set(cache_key, context, 600)
    
    return render(request, 'elearning/progress_dashboard.html', context)

@cache_page(VIEW_CACHE_TTL)
@login_required
def leaderboard(request):
    """
    Learning leaderboard with pagination - OPTIMIZED
    """
    # Optimized query for top learners
    top_learners_query = LearningStreak.objects.select_related('user').filter(
        total_points_earned__gt=0
    ).order_by('-total_points_earned')
    
    # Pagination
    paginator = Paginator(top_learners_query, 20)
    page = request.GET.get('page', 1)
    try:
        top_learners_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        top_learners_page = paginator.page(1)
    
    # Get completion counts for displayed users
    user_ids = [learner.user_id for learner in top_learners_page]
    completion_counts = Certificate.objects.filter(
        user_id__in=user_ids
    ).values('user').annotate(modules_completed=Count('module'))
    
    completion_map = {item['user']: item['modules_completed'] for item in completion_counts}
    
    # Prepare leaderboard data
    leaderboard_data = []
    for i, streak in enumerate(top_learners_page, start=top_learners_page.start_index()):
        leaderboard_data.append({
            'rank': i,
            'user': streak.user,
            'points': streak.total_points_earned,
            'modules_completed': completion_map.get(streak.user.id, 0),
            'streak': streak.current_streak,
        })
    
    # Find current user's rank
    user_rank = None
    if request.user.is_authenticated:
        user_streak = LearningStreak.objects.filter(user=request.user).first()
        if user_streak and user_streak.total_points_earned > 0:
            user_rank = LearningStreak.objects.filter(
                total_points_earned__gt=user_streak.total_points_earned
            ).count() + 1
    
    context = {
        'leaderboard_data': leaderboard_data,
        'user_rank': user_rank,
        'paginator': paginator,
        'page_obj': top_learners_page,
    }
    
    return render(request, 'elearning/leaderboard.html', context)

# Keep other views from original file but add caching where appropriate
@login_required
def enroll_module(request, slug):
    """Enroll user in a module - Clear relevant caches"""
    module = get_object_or_404(Module, slug=slug, is_published=True)
        
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        module=module,
        defaults={'progress_percentage': 0}
    )
        
    if created:
        # Update enrollment count atomically
        Module.objects.filter(pk=module.pk).update(enrollments_count=F('enrollments_count') + 1)
        
        # Clear relevant caches
        cache.delete(f'module_enrollments_{module.id}')
        cache.delete(f'progress_dashboard_{request.user.id}')
        cache.delete('module_stats')
            
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
@require_POST
def complete_lesson(request, lesson_id):
    """Mark lesson as completed - Clear relevant caches"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, module=lesson.module)
    
    lesson_progress, created = LessonProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )
    
    if not lesson_progress.is_completed:
        lesson_progress.is_completed = True
        lesson_progress.completed_at = timezone.now()
        lesson_progress.save()
        
        # Update progress
        total_lessons = lesson.module.lessons.count()
        completed = LessonProgress.objects.filter(
            enrollment=enrollment,
            is_completed=True
        ).count()
        
        enrollment.progress_percentage = int((completed / total_lessons) * 100)
        enrollment.save()
        
        # Clear caches
        cache.delete(f'progress_dashboard_{request.user.id}')
        cache.delete(f'lesson_navigation_{lesson.module.id}')
        
        if enrollment.progress_percentage == 100 and not enrollment.completed_at:
            enrollment.completed_at = timezone.now()
            enrollment.save()
            
            # Update completion count
            Module.objects.filter(pk=lesson.module.pk).update(completions_count=F('completions_count') + 1)
            
            # Award certificate
            Certificate.objects.get_or_create(
                user=request.user,
                module=lesson.module,
                defaults={'final_score': 100, 'certificate_id': f'C-{lesson.module.id}-{request.user.id}'}
            )
            
            messages.success(request, f'🎉 Congratulations! You completed {lesson.module.title}! Certificate awarded!')
        else:
            messages.success(request, f'✅ Lesson "{lesson.title}" marked as complete! Keep going!')
    else:
        messages.info(request, f'You already completed this lesson.')
    
    return redirect('elearning:lesson_detail', module_slug=lesson.module.slug, lesson_slug=lesson.slug)