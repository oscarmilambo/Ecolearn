# admin_dashboard/views.py (FIXED - userprofile instead of profile)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from openpyxl import Workbook
from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


from accounts.models import CustomUser, UserProfile
from elearning.models import Module, Enrollment
from reporting.models import DumpingReport
from payments.models import Payment
from community.models import CommunityEvent  # Remove if not exists
from django.db.models import Sum


@staff_member_required
def dashboard(request):
    # Get pending proofs count for navigation badge
    from community.models import ChallengeProof
    request.pending_proofs_count = ChallengeProof.objects.filter(status='pending').count()
    
    total_users = CustomUser.objects.count()
    users_last_3_months = CustomUser.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=90)
    ).count()

    # SAFE retention rate
    six_months_ago = timezone.now() - timedelta(days=180)
    old_users = CustomUser.objects.filter(date_joined__lte=six_months_ago).count()
    active_old = CustomUser.objects.filter(
        date_joined__lte=six_months_ago,
        last_login__gte=timezone.now() - timedelta(days=30)
    ).count()
    retention_rate = round((active_old / old_users * 100), 1) if old_users else 0

    # SAFE completion rate
    total_enrollments = Enrollment.objects.count()
    completed = Enrollment.objects.exclude(completed_at=None).count()
    module_completion_rate = round((completed / total_enrollments * 100), 1) if total_enrollments else 0

    # SAFE reports
    total_reports = DumpingReport.objects.count()
    six_months_reports = DumpingReport.objects.filter(
        reported_at__gte=timezone.now() - timedelta(days=180)
    ).count()

    # SAFE revenue
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    # SAFE charts (only valid dates)
    monthly_users = list(
        CustomUser.objects
        .filter(date_joined__isnull=False)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')[:6]
    )

    language_dist = list(
        CustomUser.objects
        .exclude(preferred_language__isnull=True)
        .values('preferred_language')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # SAFE map data (only valid coordinates)
    report_locs = list(
        DumpingReport.objects
        .filter(latitude__isnull=False, longitude__isnull=False)
        .values('latitude', 'longitude', 'description', 'waste_type')[:50]
    )

    context = {
        'total_users': total_users,
        'users_last_3_months': users_last_3_months,
        'retention_rate': retention_rate,
        'module_completion_rate': module_completion_rate,
        'total_reports': total_reports,
        'reports_last_6_months': six_months_reports,
        'engagement_rate': 48,  # Hardcoded fallback
        'total_revenue': total_revenue,
        'roi': 156,
        'monthly_users': monthly_users or [],
        'language_dist': language_dist,
        'report_locs': report_locs,
    }

    return render(request, 'admin_dashboard/dashboard.html', context)


@staff_member_required
def user_management(request):
    from django.db.models import Q, Count, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # Get filter parameters
    location_filter = request.GET.get('location', '')
    language_filter = request.GET.get('language', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset with related data
    users = CustomUser.objects.select_related('userprofile').prefetch_related(
        'enrollment_set', 'point_transactions', 'notification_preferences'
    )
    
    # Apply filters
    if location_filter:
        users = users.filter(location__icontains=location_filter)
    if language_filter:
        users = users.filter(preferred_language=language_filter)
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter == 'active':
        users = users.filter(is_active=True, last_login__gte=timezone.now() - timedelta(days=30))
    elif status_filter == 'inactive':
        users = users.filter(Q(is_active=False) | Q(last_login__lt=timezone.now() - timedelta(days=30)))
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    users = users.order_by('-date_joined')
    
    # User statistics
    total_users = CustomUser.objects.count()
    target_users = 500  # Target for first 3 months
    three_months_ago = timezone.now() - timedelta(days=90)
    users_last_3_months = CustomUser.objects.filter(date_joined__gte=three_months_ago).count()
    progress_to_target = round((total_users / target_users * 100), 1) if target_users else 0
    
    # Demographics by location (Kalingalinga, Kanyama, Chawama)
    location_stats = CustomUser.objects.values('location').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Language distribution
    language_stats = CustomUser.objects.values('preferred_language').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Role distribution
    role_stats = CustomUser.objects.values('role').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Activity stats
    active_users = CustomUser.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Registration trends (last 6 months)
    registration_trends = []
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30 * (i + 1))
        month_end = timezone.now() - timedelta(days=30 * i)
        count = CustomUser.objects.filter(
            date_joined__gte=month_start,
            date_joined__lt=month_end
        ).count()
        registration_trends.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    registration_trends.reverse()
    
    context = {
        'users': users,
        'total_users': total_users,
        'target_users': target_users,
        'users_last_3_months': users_last_3_months,
        'progress_to_target': progress_to_target,
        'active_users': active_users,
        'location_stats': location_stats,
        'language_stats': language_stats,
        'role_stats': role_stats,
        'registration_trends': registration_trends,
        # Filter values for form persistence
        'location_filter': location_filter,
        'language_filter': language_filter,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        # Filter choices
        'language_choices': CustomUser.LANGUAGE_CHOICES,
        'role_choices': CustomUser.USER_ROLES,
    }
    
    return render(request, 'admin_dashboard/users.html', context)


@staff_member_required
def module_management(request):
    """Content Management System - Module Management"""
    from django.db.models import Q, Count, Avg
    from elearning.models import Module, Category, Tag
    
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    difficulty_filter = request.GET.get('difficulty', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    modules = Module.objects.select_related('category', 'created_by').prefetch_related('tags').annotate(
        enrolled=Count('enrollment'),
        completed=Count('enrollment', filter=Q(enrollment__completed_at__isnull=False))
    )
    
    # Apply filters
    if category_filter:
        modules = modules.filter(category_id=category_filter)
    if difficulty_filter:
        modules = modules.filter(difficulty=difficulty_filter)
    if status_filter == 'published':
        modules = modules.filter(is_published=True)
    elif status_filter == 'unpublished':
        modules = modules.filter(is_published=False)
    elif status_filter == 'featured':
        modules = modules.filter(is_featured=True)
    if search_query:
        modules = modules.filter(
            Q(title__icontains=search_query) |
            Q(title_bem__icontains=search_query) |
            Q(title_ny__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    modules = modules.order_by('-created_at')
    
    # Statistics
    total_modules = Module.objects.count()
    published_modules = Module.objects.filter(is_published=True).count()
    draft_modules = Module.objects.filter(is_published=False).count()
    featured_modules = Module.objects.filter(is_featured=True).count()
    
    # Category breakdown
    category_stats = Category.objects.annotate(
        module_count=Count('modules'),
        published_count=Count('modules', filter=Q(modules__is_published=True))
    ).order_by('-module_count')
    
    # Get all categories and tags for filters
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'modules': modules,
        'total_modules': total_modules,
        'published_modules': published_modules,
        'draft_modules': draft_modules,
        'featured_modules': featured_modules,
        'category_stats': category_stats,
        'categories': categories,
        'category_filter': category_filter,
        'difficulty_filter': difficulty_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        'difficulty_choices': Module.DIFFICULTY_CHOICES,
    }
    
    return render(request, 'admin_dashboard/modules.html', context)


# admin_dashboard/views.py → report_management (COPY-PASTE THIS EXACT FUNCTION)

@staff_member_required
def report_detail(request, report_id):
    """Detailed view of a specific dumping report"""
    from reporting.models import DumpingReport, ReportUpdate, Authority
    from community.notifications import send_notification
    
    report = get_object_or_404(DumpingReport, id=report_id)
    updates = report.updates.all().order_by('-created_at')
    authorities = Authority.objects.filter(is_active=True)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            old_status = report.status
            new_status = request.POST.get('status')
            report.status = new_status
            
            # Set timestamps based on status
            if new_status == 'verified' and not report.verified_at:
                report.verified_at = timezone.now()
            elif new_status == 'resolved' and not report.resolved_at:
                report.resolved_at = timezone.now()
            
            report.save()
            
            # Send notification to reporter if not anonymous
            if report.reporter and not report.is_anonymous:
                status_messages = {
                    'pending': 'Your report has been received and is pending review.',
                    'verified': 'Your report has been verified and is being investigated.',
                    'in_progress': 'Your report is being actively investigated.',
                    'resolved': 'Your report has been resolved! Thank you for helping keep our community clean.',
                    'rejected': 'Your report has been reviewed. Please contact us for more information.'
                }
                
                notification_message = status_messages.get(new_status, f'Your report status has been updated to {report.get_status_display()}')
                
                # Send notification
                send_notification(
                    user=report.reporter,
                    title=f'Report Update: {report.reference_number}',
                    message=notification_message,
                    notification_type='report_update',
                    link=f'/reporting/reports/{report.id}/'
                )
                
                # Send SMS if user has phone number
                if report.reporter.phone_number:
                    try:
                        from twilio.rest import Client
                        from django.conf import settings
                        
                        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        client.messages.create(
                            body=f"[EcoLearn] Report {report.reference_number}: {notification_message}",
                            from_=settings.TWILIO_PHONE_NUMBER,
                            to=str(report.reporter.phone_number)
                        )
                    except Exception as e:
                        print(f"SMS notification failed: {str(e)}")
            
            # Create update record
            ReportUpdate.objects.create(
                report=report,
                update_text=f'Status changed from {old_status} to {new_status}',
                updated_by=request.user,
                is_public=True
            )
            
            messages.success(request, f'Report status updated to {report.get_status_display()} and user notified!')
        
        elif action == 'add_update':
            update_text = request.POST.get('update_text')
            is_public = request.POST.get('is_public') == 'on'
            
            ReportUpdate.objects.create(
                report=report,
                update_text=update_text,
                updated_by=request.user,
                is_public=is_public
            )
            
            # Notify reporter if update is public
            if is_public and report.reporter and not report.is_anonymous:
                send_notification(
                    user=report.reporter,
                    title=f'New Update: {report.reference_number}',
                    message=update_text[:100],
                    notification_type='report_update',
                    link=f'/reporting/reports/{report.id}/'
                )
            
            messages.success(request, 'Update added successfully!')
        
        elif action == 'forward_to_authority':
            authority_id = request.POST.get('authority')
            authority = Authority.objects.get(id=authority_id)
            
            report.forwarded_to_authority = True
            report.authority_name = authority.name
            report.authority_contact = authority.contact_email
            report.save()
            
            # Create update record
            ReportUpdate.objects.create(
                report=report,
                update_text=f'Report forwarded to {authority.name}',
                updated_by=request.user,
                is_public=True
            )
            
            # Notify reporter
            if report.reporter and not report.is_anonymous:
                send_notification(
                    user=report.reporter,
                    title=f'Report Forwarded: {report.reference_number}',
                    message=f'Your report has been forwarded to {authority.name} for action.',
                    notification_type='report_update',
                    link=f'/reporting/reports/{report.id}/'
                )
            
            messages.success(request, f'Report forwarded to {authority.name} and user notified!')
        
        elif action == 'add_notes':
            report.admin_notes = request.POST.get('admin_notes')
            report.save()
            messages.success(request, 'Admin notes updated!')
        
        return redirect('admin_dashboard:report_detail', report_id=report.id)
    
    context = {
        'report': report,
        'updates': updates,
        'authorities': authorities,
        'status_choices': DumpingReport.STATUS_CHOICES,
    }
    
    return render(request, 'admin_dashboard/report_detail.html', context)


@staff_member_required
def report_management(request):
    from reporting.models import DumpingReport
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q

    # Get filter parameters
    status_filter = request.GET.get('status', '')
    severity_filter = request.GET.get('severity', '')
    forwarded_filter = request.GET.get('forwarded', '')
    search_query = request.GET.get('search', '')

    # Base queryset
    reports = DumpingReport.objects.select_related('reporter').order_by('-reported_at')

    # Apply filters
    if status_filter:
        reports = reports.filter(status=status_filter)
    if severity_filter:
        reports = reports.filter(severity=severity_filter)
    if forwarded_filter == 'yes':
        reports = reports.filter(forwarded_to_authority=True)
    elif forwarded_filter == 'no':
        reports = reports.filter(forwarded_to_authority=False)
    if search_query:
        reports = reports.filter(
            Q(reference_number__icontains=search_query) |
            Q(location_description__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Get actual NUMBERS, not querysets!
    total_reports = DumpingReport.objects.count()
    six_months_ago = timezone.now() - timedelta(days=180)
    reports_last_6_months = DumpingReport.objects.filter(reported_at__gte=six_months_ago).count()

    # Status counts for template
    pending_count = DumpingReport.objects.filter(status='pending').count()
    verified_count = DumpingReport.objects.filter(status='verified').count()
    in_progress_count = DumpingReport.objects.filter(status='in_progress').count()
    resolved_count = DumpingReport.objects.filter(status='resolved').count()
    
    high_priority_pending = DumpingReport.objects.filter(status='pending', severity='high').count()
    critical_pending = DumpingReport.objects.filter(status='pending', severity='critical').count()
    overdue_reports = DumpingReport.objects.filter(
        status='in_progress',
        reported_at__lte=timezone.now() - timedelta(days=7)
    ).count()

    # Calculate metrics
    resolution_rate = round((resolved_count / total_reports * 100), 1) if total_reports > 0 else 0
    forwarded_count = DumpingReport.objects.filter(forwarded_to_authority=True).count()
    forwarded_rate = round((forwarded_count / total_reports * 100), 1) if total_reports > 0 else 0

    # Get pending reports as queryset for the table
    pending_reports = DumpingReport.objects.filter(status='pending').select_related('reporter').order_by('-reported_at')[:10]

    # Map data
    report_locs = list(
        DumpingReport.objects
        .filter(latitude__isnull=False, longitude__isnull=False)
        .values('id', 'latitude', 'longitude', 'waste_type', 'description', 'severity', 'status', 'reference_number')[:200]
    )

    # Status counts dictionary for template
    status_counts = {
        'pending': pending_count,
        'verified': verified_count,
        'in_progress': in_progress_count,
        'resolved': resolved_count,
    }

    context = {
        'reports': reports,
        'pending_reports': pending_reports,
        'status_counts': status_counts,
        'total_reports': total_reports,
        'reports_last_6_months': reports_last_6_months,
        'high_priority_pending': high_priority_pending,
        'critical_pending': critical_pending,
        'in_progress_reports': in_progress_count,
        'overdue_reports': overdue_reports,
        'resolved_reports': resolved_count,
        'resolution_rate': resolution_rate,
        'forwarded_count': forwarded_count,
        'forwarded_rate': forwarded_rate,
        'report_locs': report_locs,
        # Filter values
        'status_filter': status_filter,
        'severity_filter': severity_filter,
        'forwarded_filter': forwarded_filter,
        'search_query': search_query,
        # Filter choices
        'status_choices': DumpingReport.STATUS_CHOICES,
        'severity_choices': DumpingReport.SEVERITY_CHOICES,
    }
    return render(request, 'admin_dashboard/reports.html', context)


@staff_member_required
def authority_management(request):
    """Manage authorities for report forwarding"""
    from reporting.models import Authority
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            Authority.objects.create(
                name=request.POST.get('name'),
                contact_email=request.POST.get('contact_email'),
                contact_phone=request.POST.get('contact_phone', ''),
                api_endpoint=request.POST.get('api_endpoint', ''),
                api_key=request.POST.get('api_key', ''),
                coverage_areas=request.POST.get('coverage_areas', ''),
                is_active=True
            )
            messages.success(request, 'Authority added successfully!')
        
        elif action == 'toggle':
            authority_id = request.POST.get('authority_id')
            authority = Authority.objects.get(id=authority_id)
            authority.is_active = not authority.is_active
            authority.save()
            status = "activated" if authority.is_active else "deactivated"
            messages.success(request, f'Authority {status}!')
        
        elif action == 'delete':
            authority_id = request.POST.get('authority_id')
            authority = Authority.objects.get(id=authority_id)
            authority.delete()
            messages.success(request, 'Authority deleted!')
        
        return redirect('admin_dashboard:authority_management')
    
    authorities = Authority.objects.all().order_by('-is_active', 'name')
    
    context = {
        'authorities': authorities,
    }
    
    return render(request, 'admin_dashboard/authority_management.html', context)


@staff_member_required
def forum_moderation(request):
    """Community Forum Moderation"""
    from community.models import ForumTopic, ForumReply, SuccessStory, ForumCategory
    from django.db.models import Q, Count, Sum
    
    # Get filter parameters
    content_type = request.GET.get('type', 'all')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Get forum topics with engagement metrics
    topics = ForumTopic.objects.select_related('author', 'category').annotate(
        reply_count=Count('replies')
    ).order_by('-created_at')
    
    # Apply category filter
    if category_filter:
        topics = topics.filter(category_id=category_filter)
    
    # Get forum replies
    replies = ForumReply.objects.select_related('author', 'topic').order_by('-created_at')
    
    # Get success stories (pending approval)
    pending_stories = SuccessStory.objects.filter(is_approved=False).select_related('author').order_by('-created_at')
    approved_stories = SuccessStory.objects.filter(is_approved=True).select_related('author').order_by('-created_at')[:10]
    
    # Apply search
    if search_query:
        topics = topics.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
        replies = replies.filter(
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Statistics
    total_topics = ForumTopic.objects.count()
    total_replies = ForumReply.objects.count()
    total_stories = SuccessStory.objects.count()
    pending_stories_count = pending_stories.count()
    pinned_topics_count = ForumTopic.objects.filter(is_pinned=True).count()
    locked_topics_count = ForumTopic.objects.filter(is_locked=True).count()
    
    # Category breakdown with engagement metrics
    categories = ForumCategory.objects.annotate(
        topic_count=Count('topics'),
        total_replies=Count('topics__replies')
    ).order_by('-topic_count')
    
    # Engagement metrics
    total_likes = SuccessStory.objects.aggregate(
        total=Sum('likes__id')
    )['total'] or 0
    
    # Most engaged topics (by replies)
    most_engaged_topics = ForumTopic.objects.annotate(
        reply_count=Count('replies')
    ).order_by('-reply_count')[:5]
    
    # Get all categories for filter
    all_categories = ForumCategory.objects.filter(is_active=True).order_by('name')
    
    context = {
        'topics': topics[:50],
        'replies': replies[:50],
        'pending_stories': pending_stories,
        'approved_stories': approved_stories,
        'total_topics': total_topics,
        'total_replies': total_replies,
        'total_stories': total_stories,
        'pending_stories_count': pending_stories_count,
        'pinned_topics_count': pinned_topics_count,
        'locked_topics_count': locked_topics_count,
        'categories': categories,
        'all_categories': all_categories,
        'most_engaged_topics': most_engaged_topics,
        'total_likes': total_likes,
        'content_type': content_type,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_dashboard/forum_moderation.html', context)


@staff_member_required
def moderate_content(request, content_type, content_id):
    """Moderate specific content (delete, pin, lock, approve)"""
    from community.models import ForumTopic, ForumReply, SuccessStory
    from community.notifications import send_notification
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if content_type == 'topic':
            content = get_object_or_404(ForumTopic, id=content_id)
            
            if action == 'delete':
                content.delete()
                messages.success(request, 'Topic deleted successfully!')
            elif action == 'pin':
                content.is_pinned = not content.is_pinned
                content.save()
                status = "pinned" if content.is_pinned else "unpinned"
                messages.success(request, f'Topic {status}!')
            elif action == 'lock':
                content.is_locked = not content.is_locked
                content.save()
                status = "locked" if content.is_locked else "unlocked"
                messages.success(request, f'Topic {status}!')
        
        elif content_type == 'reply':
            content = get_object_or_404(ForumReply, id=content_id)
            
            if action == 'delete':
                content.delete()
                messages.success(request, 'Reply deleted successfully!')
            elif action == 'mark_solution':
                content.is_solution = not content.is_solution
                content.save()
                status = "marked as solution" if content.is_solution else "unmarked as solution"
                messages.success(request, f'Reply {status}!')
        
        elif content_type == 'story':
            content = get_object_or_404(SuccessStory, id=content_id)
            
            if action == 'approve':
                content.is_approved = True
                content.save()
                
                # Notify author
                send_notification(
                    user=content.author,
                    title='Success Story Approved!',
                    message=f'Your success story "{content.title}" has been approved and is now visible to the community!',
                    notification_type='story_approved',
                    link=f'/community/stories/{content.id}/'
                )
                
                messages.success(request, 'Story approved and author notified!')
            elif action == 'disapprove':
                content.is_approved = False
                content.save()
                messages.success(request, 'Story disapproved!')
            elif action == 'delete':
                content.delete()
                messages.success(request, 'Story deleted successfully!')
            elif action == 'feature':
                content.is_featured = not content.is_featured
                content.save()
                status = "featured" if content.is_featured else "unfeatured"
                messages.success(request, f'Story {status}!')
        
        return redirect('admin_dashboard:forum_moderation')
    
    return redirect('admin_dashboard:forum_moderation')


@staff_member_required
def challenge_management(request):
    """Community Challenges Management with Proofs"""
    from community.models import CommunityChallenge, ChallengeParticipant, ChallengeProof
    from django.db.models import Count, Sum
    from django.utils import timezone
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')
    
    # Base queryset
    challenges = CommunityChallenge.objects.annotate(
        participant_count=Count('participants'),
        total_contribution=Sum('participants__contribution')
    ).order_by('-start_date')
    
    # Apply filters
    if status_filter == 'upcoming':
        challenges = challenges.filter(start_date__gt=timezone.now())
    elif status_filter == 'active':
        challenges = challenges.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now(), is_active=True)
    elif status_filter == 'completed':
        challenges = challenges.filter(end_date__lt=timezone.now())
    elif status_filter == 'cancelled':
        challenges = challenges.filter(is_active=False)
    
    if type_filter:
        challenges = challenges.filter(challenge_type=type_filter)
    
    # Statistics
    total_challenges = CommunityChallenge.objects.count()
    active_challenges = CommunityChallenge.objects.filter(
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        is_active=True
    ).count()
    upcoming_challenges = CommunityChallenge.objects.filter(start_date__gt=timezone.now()).count()
    completed_challenges = CommunityChallenge.objects.filter(end_date__lt=timezone.now()).count()
    
    # Total participants across all challenges
    total_participants = ChallengeParticipant.objects.values('user').distinct().count()
    
    # Proof statistics
    pending_proofs = ChallengeProof.objects.filter(status='pending').select_related(
        'participant__user', 'participant__challenge'
    ).order_by('-submitted_at')[:10]  # Show latest 10
    
    pending_count = ChallengeProof.objects.filter(status='pending').count()
    approved_count = ChallengeProof.objects.filter(status='approved').count()
    total_bags = ChallengeProof.objects.filter(status='approved').aggregate(
        total=Sum('bags_collected')
    )['total'] or 0
    total_points = total_bags * 30
    
    context = {
        'challenges': challenges,
        'total_challenges': total_challenges,
        'active_challenges': active_challenges,
        'upcoming_challenges': upcoming_challenges,
        'completed_challenges': completed_challenges,
        'total_participants': total_participants,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'challenge_types': CommunityChallenge.CHALLENGE_TYPES,
        'now': timezone.now(),
        # Proof data
        'pending_proofs': pending_proofs,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'total_bags': total_bags,
        'total_points': total_points,
    }
    
    return render(request, 'admin_dashboard/challenge_management.html', context)


@staff_member_required
def challenge_create(request):
    """Create new community challenge"""
    from community.models import CommunityChallenge, Notification
    from community.notifications import notification_service
    
    if request.method == 'POST':
        challenge = CommunityChallenge.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            challenge_type=request.POST.get('challenge_type'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            target_goal=int(request.POST.get('target_goal', 100)),
            reward_points=int(request.POST.get('reward_points', 100)),
            is_active=True
        )
        
        if request.FILES.get('image'):
            challenge.image = request.FILES['image']
            challenge.save()
        
        # Send notifications to all active users
        try:
            from accounts.models import CustomUser
            active_users = CustomUser.objects.filter(is_active=True)
            
            # Prepare notification data
            notification_data = {
                'challenge_name': challenge.title,
                'description': challenge.description[:100],
                'reward_points': challenge.reward_points,
                'end_date': challenge.end_date.strftime('%B %d, %Y'),
                'url': f'/community/challenges/{challenge.id}/'
            }
            
            # Send via SMS/WhatsApp/Email based on user preferences
            notification_count = 0
            for user in active_users:
                try:
                    # Create in-app notification
                    Notification.objects.create(
                        user=user,
                        notification_type='challenge_update',
                        title=f'🏆 New Challenge: {challenge.title}',
                        message=f'{challenge.description[:150]}... Reward: {challenge.reward_points} points!',
                        url=f'/community/challenges/{challenge.id}/'
                    )
                    
                    # Send external notifications if user has preferences
                    if hasattr(user, 'notification_preferences'):
                        prefs = user.notification_preferences
                        channels = []
                        if prefs.sms_enabled:
                            channels.append('sms')
                        if prefs.whatsapp_enabled:
                            channels.append('whatsapp')
                        if prefs.email_enabled:
                            channels.append('email')
                        
                        if channels:
                            # Prepare message
                            message_data = {
                                'sms': f"🏆 New Challenge: {challenge.title}\nReward: {challenge.reward_points} pts\nJoin: {request.build_absolute_uri(f'/community/challenges/{challenge.id}/')}",
                                'whatsapp': f"🏆 *New Challenge Launched!*\n\n*{challenge.title}*\n\n{challenge.description[:200]}\n\n*Reward:* {challenge.reward_points} points\n*Ends:* {challenge.end_date.strftime('%B %d, %Y')}\n\nJoin now: {request.build_absolute_uri(f'/community/challenges/{challenge.id}/')}\n\nLet's make a difference together! 🌱",
                                'subject': f'New Challenge: {challenge.title}',
                                'text': f"A new challenge has been launched: {challenge.title}\n\n{challenge.description}\n\nReward: {challenge.reward_points} points\nEnds: {challenge.end_date.strftime('%B %d, %Y')}\n\nJoin now: {request.build_absolute_uri(f'/community/challenges/{challenge.id}/')}"
                            }
                            
                            # Send via each enabled channel
                            if 'sms' in channels and user.phone_number:
                                notification_service.send_sms(str(user.phone_number), message_data['sms'][:160])
                            
                            if 'whatsapp' in channels and user.phone_number:
                                notification_service.send_whatsapp(str(user.phone_number), message_data['whatsapp'])
                            
                            if 'email' in channels and user.email:
                                notification_service.send_email(user.email, message_data['subject'], message_data['text'])
                    
                    notification_count += 1
                except Exception as e:
                    logger.error(f"Error sending notification to user {user.id}: {str(e)}")
            
            messages.success(request, f'Challenge "{challenge.title}" created and {notification_count} users notified!')
        except Exception as e:
            logger.error(f"Error sending challenge notifications: {str(e)}")
            messages.success(request, f'Challenge "{challenge.title}" created successfully!')
        
        return redirect('admin_dashboard:challenge_detail', challenge_id=challenge.id)
    
    context = {
        'challenge_types': CommunityChallenge.CHALLENGE_TYPES,
    }
    
    return render(request, 'admin_dashboard/challenge_create.html', context)


@staff_member_required
def challenge_detail(request, challenge_id):
    """View and manage specific challenge"""
    from community.models import CommunityChallenge, ChallengeParticipant
    from django.db.models import Sum
    
    challenge = get_object_or_404(CommunityChallenge, id=challenge_id)
    participants = ChallengeParticipant.objects.filter(challenge=challenge).select_related('user').order_by('-contribution')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update':
            challenge.title = request.POST.get('title')
            challenge.description = request.POST.get('description')
            challenge.target_goal = int(request.POST.get('target_goal'))
            challenge.reward_points = int(request.POST.get('reward_points'))
            
            if request.FILES.get('image'):
                challenge.image = request.FILES['image']
            
            challenge.save()
            messages.success(request, 'Challenge updated successfully!')
        
        elif action == 'toggle_status':
            challenge.is_active = not challenge.is_active
            challenge.save()
            status = "activated" if challenge.is_active else "cancelled"
            messages.success(request, f'Challenge {status}!')
        
        elif action == 'award_points':
            # Award points to all participants
            from gamification.models import PointTransaction
            
            for participant in participants:
                PointTransaction.objects.create(
                    user=participant.user,
                    points=challenge.reward_points,
                    description=f'Completed challenge: {challenge.title}',
                    transaction_type='challenge_reward'
                )
            
            messages.success(request, f'Points awarded to {participants.count()} participants!')
        
        return redirect('admin_dashboard:challenge_detail', challenge_id=challenge.id)
    
    # Calculate statistics
    total_contribution = participants.aggregate(total=Sum('contribution'))['total'] or 0
    progress_percentage = min(100, int((total_contribution / challenge.target_goal * 100))) if challenge.target_goal else 0
    
    context = {
        'challenge': challenge,
        'participants': participants,
        'total_contribution': total_contribution,
        'progress_percentage': progress_percentage,
        'now': timezone.now(),
    }
    
    return render(request, 'admin_dashboard/challenge_detail.html', context)


@staff_member_required
def challenge_delete(request, challenge_id):
    """Delete challenge"""
    challenge = get_object_or_404(CommunityChallenge, id=challenge_id)
    challenge_title = challenge.title
    challenge.delete()
    messages.success(request, f'Challenge "{challenge_title}" deleted successfully!')
    return redirect('admin_dashboard:challenge_management')


@staff_member_required
def challenge_proofs(request):
    """View and manage challenge proof submissions"""
    from community.models import ChallengeProof
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'pending')
    challenge_filter = request.GET.get('challenge', '')
    
    # Base query
    proofs = ChallengeProof.objects.select_related(
        'participant__user', 
        'participant__challenge',
        'reviewed_by'
    ).order_by('-submitted_at')
    
    # Apply filters
    if status_filter and status_filter != 'all':
        proofs = proofs.filter(status=status_filter)
    
    if challenge_filter:
        proofs = proofs.filter(participant__challenge_id=challenge_filter)
    
    # Get challenges for filter dropdown
    from community.models import CommunityChallenge
    challenges = CommunityChallenge.objects.filter(is_active=True).order_by('-start_date')
    
    # Statistics
    total_proofs = ChallengeProof.objects.count()
    pending_count = ChallengeProof.objects.filter(status='pending').count()
    approved_count = ChallengeProof.objects.filter(status='approved').count()
    rejected_count = ChallengeProof.objects.filter(status='rejected').count()
    total_bags = ChallengeProof.objects.filter(status='approved').aggregate(
        total=Sum('bags_collected')
    )['total'] or 0
    total_points = total_bags * 30
    
    context = {
        'proofs': proofs,
        'challenges': challenges,
        'status_filter': status_filter,
        'challenge_filter': challenge_filter,
        'total_proofs': total_proofs,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'total_bags': total_bags,
        'total_points': total_points,
    }
    
    return render(request, 'admin_dashboard/challenge_proofs.html', context)


@staff_member_required
def proof_approve(request, proof_id):
    """Approve a challenge proof"""
    from community.models import ChallengeProof, Notification, ChallengeParticipant
    from community.notifications import notification_service
    
    proof = get_object_or_404(ChallengeProof, id=proof_id)
    
    if proof.status == 'pending':
        proof.approve(request.user)
        messages.success(
            request, 
            f'✅ Proof approved! {proof.bags_collected} bags = {proof.points_awarded} points awarded to {proof.participant.user.username}'
        )
        
        # REAL-TIME NOTIFICATION: Send WhatsApp/SMS instantly when proof is approved
        try:
            user = proof.participant.user
            prefs = getattr(user, 'notification_preferences', None)
            
            # Get user's rank in the challenge
            rank = ChallengeParticipant.objects.filter(
                challenge=proof.participant.challenge,
                contribution__gt=proof.participant.contribution
            ).count() + 1
            
            user_name = user.get_full_name() or user.username
            challenge_name = proof.participant.challenge.title
            
            # SMS notification - PRO ZNBC style
            if prefs and prefs.sms_enabled and prefs.challenge_updates and user.phone_number:
                sms_message = f"✅ APPROVED! You earned {proof.points_awarded} points ({proof.bags_collected} bags). You are now #{rank} in {challenge_name}! Keep cleaning Zambia!"
                result = notification_service.send_sms(str(user.phone_number), sms_message)
                if result.get('success'):
                    print(f"✅ SMS sent to {user.username}")
            
            # WhatsApp notification - PRO Zambian style
            if prefs and prefs.whatsapp_enabled and prefs.challenge_updates and user.phone_number:
                whatsapp_message = f"✅ APPROVED! You earned {proof.points_awarded} points ({proof.bags_collected} bags). You are now #{rank} in {challenge_name}! Keep cleaning Zambia!"
                result = notification_service.send_whatsapp(str(user.phone_number), whatsapp_message)
                if result.get('success'):
                    print(f"✅ WhatsApp sent to {user.username}")
            
            # In-app notification
            Notification.objects.create(
                user=user,
                notification_type='challenge_update',
                title='Proof Approved! 🎉',
                message=f'Your clean-up proof is approved! +{proof.points_awarded} points earned ({proof.bags_collected} bags). Current rank: #{rank}!',
                url=proof.participant.challenge.get_absolute_url()
            )
        except Exception as e:
            print(f"Notification error: {e}")
    else:
        messages.warning(request, 'This proof has already been reviewed.')
    
    return redirect('admin_dashboard:challenge_proofs')


@staff_member_required
def proof_reject(request, proof_id):
    """Reject a challenge proof"""
    from community.models import ChallengeProof
    
    proof = get_object_or_404(ChallengeProof, id=proof_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Does not meet requirements')
        proof.reject(request.user, reason)
        messages.success(request, f'❌ Proof rejected for {proof.participant.user.username}')
        return redirect('admin_dashboard:challenge_proofs')
    
    return redirect('admin_dashboard:challenge_proofs')


@staff_member_required
def proof_bulk_approve(request):
    """Bulk approve multiple proofs"""
    from community.models import ChallengeProof, Notification, ChallengeParticipant
    from community.notifications import notification_service
    
    if request.method == 'POST':
        proof_ids = request.POST.getlist('proof_ids')
        
        if not proof_ids:
            messages.warning(request, 'No proofs selected.')
            return redirect('admin_dashboard:challenge_proofs')
        
        approved_count = 0
        total_points = 0
        
        for proof_id in proof_ids:
            try:
                proof = ChallengeProof.objects.get(id=proof_id, status='pending')
                proof.approve(request.user)
                approved_count += 1
                total_points += proof.points_awarded
                
                # REAL-TIME NOTIFICATION: Send to each user
                try:
                    user = proof.participant.user
                    prefs = getattr(user, 'notification_preferences', None)
                    
                    # Get user's rank
                    rank = ChallengeParticipant.objects.filter(
                        challenge=proof.participant.challenge,
                        contribution__gt=proof.participant.contribution
                    ).count() + 1
                    
                    user_name = user.get_full_name() or user.username
                    challenge_name = proof.participant.challenge.title
                    
                    # SMS notification - PRO ZNBC style
                    if prefs and prefs.sms_enabled and prefs.challenge_updates and user.phone_number:
                        sms_message = f"✅ APPROVED! You earned {proof.points_awarded} points ({proof.bags_collected} bags). You are now #{rank} in {challenge_name}! Keep cleaning Zambia!"
                        notification_service.send_sms(str(user.phone_number), sms_message)
                    
                    # WhatsApp notification - PRO Zambian style
                    if prefs and prefs.whatsapp_enabled and prefs.challenge_updates and user.phone_number:
                        whatsapp_message = f"✅ APPROVED! You earned {proof.points_awarded} points ({proof.bags_collected} bags). You are now #{rank} in {challenge_name}! Keep cleaning Zambia!"
                        notification_service.send_whatsapp(str(user.phone_number), whatsapp_message)
                    
                    # In-app notification
                    Notification.objects.create(
                        user=user,
                        notification_type='challenge_update',
                        title='Proof Approved! 🎉',
                        message=f'Your clean-up proof is approved! +{proof.points_awarded} points earned ({proof.bags_collected} bags). Current rank: #{rank}!',
                        url=proof.participant.challenge.get_absolute_url()
                    )
                except Exception as e:
                    print(f"Notification error for user {user.username}: {e}")
                    
            except ChallengeProof.DoesNotExist:
                pass
        
        messages.success(
            request, 
            f'✅ {approved_count} proof(s) approved! Total {total_points} points awarded!'
        )
    
    return redirect('admin_dashboard:challenge_proofs')


@staff_member_required
def system_settings(request):
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        if message and len(message) <= 160:
            try:
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                users = CustomUser.objects.filter(phone_number__isnull=False)
                sent = 0
                for user in users:
                    client.messages.create(
                        body=f"[EcoLearn] {message}",
                        from_=settings.TWILIO_PHONE_NUMBER,
                        to=str(user.phone_number)
                    )
                    sent += 1
                messages.success(request, f'SMS sent to {sent} users!')
            except Exception as e:
                messages.error(request, f'Failed: {str(e)[:50]}...')
        else:
            messages.error(request, 'Message empty or too long!')
        return redirect('admin_dashboard:settings')

    return render(request, 'admin_dashboard/settings.html', {
        'total_users': CustomUser.objects.count()
    })


@staff_member_required
def export_users(request):
    from django.utils import timezone
    
    wb = Workbook()
    ws = wb.active
    ws.title = "EcoLearn Users"
    
    # Enhanced headers
    headers = [
        'ID', 'Username', 'Full Name', 'Email', 'Phone', 'Location', 
        'Language', 'Role', 'Literacy Level', 'Registration Date', 
        'Last Login', 'Status', 'Modules Completed', 'Total Points'
    ]
    ws.append(headers)

    # Get users with related data
    users = CustomUser.objects.select_related('userprofile').prefetch_related(
        'enrollment_set', 'point_transactions'
    ).all()

    for user in users:
        # Calculate user stats
        modules_completed = user.enrollment_set.filter(completed_at__isnull=False).count()
        total_points = sum(pt.points for pt in user.point_transactions.all())
        
        # Determine status
        if not user.is_active:
            status = 'Inactive'
        elif user.last_login and user.last_login >= timezone.now() - timezone.timedelta(days=30):
            status = 'Active'
        else:
            status = 'Dormant'
        
        # Get literacy level from profile if exists
        literacy_level = 'Unknown'
        if hasattr(user, 'userprofile') and user.userprofile:
            literacy_level = getattr(user.userprofile, 'literacy_level', 'Unknown')
        
        ws.append([
            user.id,
            user.username,
            user.get_full_name() or 'N/A',
            user.email or 'N/A',
            str(user.phone_number) if user.phone_number else 'N/A',
            user.location or 'N/A',
            user.get_preferred_language_display(),
            user.get_role_display(),
            literacy_level,
            user.date_joined.strftime('%Y-%m-%d %H:%M') if user.date_joined else 'Unknown',
            user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never',
            status,
            modules_completed,
            total_points
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=ecolearn_users_{timezone.now().strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


@staff_member_required
def user_detail(request, user_id):
    """Detailed view of a specific user"""
    from django.utils import timezone
    from datetime import timedelta
    
    user = get_object_or_404(CustomUser, id=user_id)
    
    # User activity stats
    enrollments = user.enrollment_set.select_related('module').all()
    completed_modules = enrollments.filter(completed_at__isnull=False)
    point_transactions = user.point_transactions.all().order_by('-created_at')[:10]
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_activity = {
        'logins': 1 if user.last_login and user.last_login >= thirty_days_ago else 0,
        'modules_completed': completed_modules.filter(completed_at__gte=thirty_days_ago).count(),
        'points_earned': sum(
            pt.points for pt in point_transactions 
            if pt.created_at >= thirty_days_ago and pt.points > 0
        )
    }
    
    context = {
        'user': user,
        'enrollments': enrollments,
        'completed_modules': completed_modules,
        'point_transactions': point_transactions,
        'recent_activity': recent_activity,
        'total_points': sum(pt.points for pt in user.point_transactions.all()),
    }
    
    return render(request, 'admin_dashboard/user_detail.html', context)


@staff_member_required
def toggle_user_status(request, user_id):
    """Activate/deactivate user account"""
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status = "activated" if user.is_active else "deactivated"
    messages.success(request, f'User {user.username} has been {status}.')
    
    return redirect('admin_dashboard:user_detail', user_id=user.id)


@staff_member_required
def module_create(request):
    """Create new learning module"""
    from elearning.models import Module, Category, Tag
    from django.forms import ModelForm
    
    if request.method == 'POST':
        # Handle module creation
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        difficulty = request.POST.get('difficulty')
        duration_minutes = request.POST.get('duration_minutes', 0)
        points_reward = request.POST.get('points_reward', 10)
        is_published = request.POST.get('is_published') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        
        # Create module
        module = Module.objects.create(
            title=title,
            description=description,
            category_id=category_id,
            difficulty=difficulty,
            duration_minutes=duration_minutes,
            points_reward=points_reward,
            is_published=is_published,
            is_featured=is_featured,
            created_by=request.user
        )
        
        # Handle multilingual content
        if request.POST.get('title_bem'):
            module.title_bem = request.POST.get('title_bem')
        if request.POST.get('description_bem'):
            module.description_bem = request.POST.get('description_bem')
        if request.POST.get('title_ny'):
            module.title_ny = request.POST.get('title_ny')
        if request.POST.get('description_ny'):
            module.description_ny = request.POST.get('description_ny')
        
        # Handle thumbnail upload
        if request.FILES.get('thumbnail'):
            module.thumbnail = request.FILES['thumbnail']
        
        # Handle PDF guide upload
        if request.FILES.get('pdf_guide'):
            module.pdf_guide = request.FILES['pdf_guide']
        
        module.save()
        
        messages.success(request, f'Module "{module.title}" created successfully!')
        return redirect('admin_dashboard:module_edit', module_id=module.id)
    
    categories = Category.objects.filter(is_active=True).order_by('name')
    
    context = {
        'categories': categories,
        'difficulty_choices': Module.DIFFICULTY_CHOICES,
    }
    
    return render(request, 'admin_dashboard/module_create.html', context)


@staff_member_required
def module_edit(request, module_id):
    """Edit existing module"""
    from elearning.models import Module, Category, Lesson
    
    module = get_object_or_404(Module, id=module_id)
    
    if request.method == 'POST':
        # Update module fields
        module.title = request.POST.get('title')
        module.description = request.POST.get('description')
        module.category_id = request.POST.get('category')
        module.difficulty = request.POST.get('difficulty')
        module.duration_minutes = request.POST.get('duration_minutes', 0)
        module.points_reward = request.POST.get('points_reward', 10)
        module.is_published = request.POST.get('is_published') == 'on'
        module.is_featured = request.POST.get('is_featured') == 'on'
        module.is_premium = request.POST.get('is_premium') == 'on'
        
        # Multilingual content
        module.title_bem = request.POST.get('title_bem', '')
        module.description_bem = request.POST.get('description_bem', '')
        module.title_ny = request.POST.get('title_ny', '')
        module.description_ny = request.POST.get('description_ny', '')
        
        # Handle thumbnail upload
        if request.FILES.get('thumbnail'):
            module.thumbnail = request.FILES['thumbnail']
        
        # Handle PDF guide upload
        if request.FILES.get('pdf_guide'):
            module.pdf_guide = request.FILES['pdf_guide']
        
        # Handle video URL
        module.video_url = request.POST.get('video_url', '')
        
        module.save()
        
        messages.success(request, f'Module "{module.title}" updated successfully!')
        return redirect('admin_dashboard:module_edit', module_id=module.id)
    
    categories = Category.objects.filter(is_active=True).order_by('name')
    lessons = module.lessons.all().order_by('order')
    
    # Get module statistics
    enrollments = module.enrollment_set.count()
    completions = module.enrollment_set.filter(completed_at__isnull=False).count()
    avg_rating = module.average_rating or 0
    
    context = {
        'module': module,
        'categories': categories,
        'lessons': lessons,
        'difficulty_choices': Module.DIFFICULTY_CHOICES,
        'enrollments': enrollments,
        'completions': completions,
        'avg_rating': avg_rating,
    }
    
    return render(request, 'admin_dashboard/module_edit.html', context)


@staff_member_required
def module_delete(request, module_id):
    """Delete module"""
    module = get_object_or_404(Module, id=module_id)
    module_title = module.title
    module.delete()
    messages.success(request, f'Module "{module_title}" deleted successfully!')
    return redirect('admin_dashboard:modules')


@staff_member_required
def module_toggle_publish(request, module_id):
    """Toggle module publish status"""
    module = get_object_or_404(Module, id=module_id)
    module.is_published = not module.is_published
    module.save()
    
    status = "published" if module.is_published else "unpublished"
    messages.success(request, f'Module "{module.title}" {status}!')
    
    return redirect('admin_dashboard:modules')


@staff_member_required
def lesson_create(request, module_id):
    """Create new lesson for a module"""
    from elearning.models import Module, Lesson
    from django.http import HttpResponse
    
    module = get_object_or_404(Module, id=module_id)
    
    if request.method == 'POST':
        try:
            # Create lesson
            lesson = Lesson.objects.create(
                module=module,
                title=request.POST.get('title'),
                content_type=request.POST.get('content_type'),
                content=request.POST.get('content', ''),
                duration_minutes=int(request.POST.get('duration_minutes', 0) or 0),
                order=int(request.POST.get('order', 0) or 0),
                is_published=request.POST.get('is_published') == 'on',
                is_preview=request.POST.get('is_preview') == 'on',
            )
            
            # Multilingual content
            lesson.title_bem = request.POST.get('title_bem', '')
            lesson.content_bem = request.POST.get('content_bem', '')
            lesson.title_ny = request.POST.get('title_ny', '')
            lesson.content_ny = request.POST.get('content_ny', '')
            
            # Handle media uploads
            if request.FILES.get('video_file'):
                lesson.video_file = request.FILES['video_file']
            if request.FILES.get('audio_file'):
                lesson.audio_file = request.FILES['audio_file']
            if request.FILES.get('video_file_bem'):
                lesson.video_file_bem = request.FILES['video_file_bem']
            if request.FILES.get('audio_file_bem'):
                lesson.audio_file_bem = request.FILES['audio_file_bem']
            if request.FILES.get('video_file_ny'):
                lesson.video_file_ny = request.FILES['video_file_ny']
            if request.FILES.get('audio_file_ny'):
                lesson.audio_file_ny = request.FILES['audio_file_ny']
            
            lesson.save()
            
            messages.success(request, f'Lesson "{lesson.title}" created successfully!')
            return redirect('admin_dashboard:module_edit', module_id=module.id)
        except Exception as e:
            messages.error(request, f'Error creating lesson: {str(e)}')
            # Re-render the form with the error
    
    # Debug: Check if template exists
    from django.template.loader import get_template
    try:
        template = get_template('admin_dashboard/lesson_create.html')
        print(f"✅ Template found: {template.origin.name}")
    except Exception as e:
        print(f"❌ Template error: {str(e)}")
        return HttpResponse(f"Template Error: {str(e)}", status=500)
    
    context = {
        'module': module,
        'content_types': Lesson.CONTENT_TYPES,
    }
    
    return render(request, 'admin_dashboard/lesson_create.html', context)


@staff_member_required
def lesson_edit(request, lesson_id):
    """Edit existing lesson"""
    from elearning.models import Lesson
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if request.method == 'POST':
        try:
            # Update lesson
            lesson.title = request.POST.get('title')
            lesson.content_type = request.POST.get('content_type')
            lesson.content = request.POST.get('content', '')
            lesson.duration_minutes = int(request.POST.get('duration_minutes', 0) or 0)
            lesson.order = int(request.POST.get('order', 0) or 0)
            lesson.is_published = request.POST.get('is_published') == 'on'
            lesson.is_preview = request.POST.get('is_preview') == 'on'
            
            # Multilingual content
            lesson.title_bem = request.POST.get('title_bem', '')
            lesson.content_bem = request.POST.get('content_bem', '')
            lesson.title_ny = request.POST.get('title_ny', '')
            lesson.content_ny = request.POST.get('content_ny', '')
            
            # Handle media uploads
            if request.FILES.get('video_file'):
                lesson.video_file = request.FILES['video_file']
            if request.FILES.get('audio_file'):
                lesson.audio_file = request.FILES['audio_file']
            if request.FILES.get('video_file_bem'):
                lesson.video_file_bem = request.FILES['video_file_bem']
            if request.FILES.get('audio_file_bem'):
                lesson.audio_file_bem = request.FILES['audio_file_bem']
            if request.FILES.get('video_file_ny'):
                lesson.video_file_ny = request.FILES['video_file_ny']
            if request.FILES.get('audio_file_ny'):
                lesson.audio_file_ny = request.FILES['audio_file_ny']
            
            lesson.save()
            
            messages.success(request, f'Lesson "{lesson.title}" updated successfully!')
            return redirect('admin_dashboard:module_edit', module_id=lesson.module.id)
        except Exception as e:
            messages.error(request, f'Error updating lesson: {str(e)}')
    
    context = {
        'lesson': lesson,
        'content_types': Lesson.CONTENT_TYPES,
    }
    
    return render(request, 'admin_dashboard/lesson_edit.html', context)


@staff_member_required
def lesson_delete(request, lesson_id):
    """Delete lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    module_id = lesson.module.id
    lesson_title = lesson.title
    lesson.delete()
    messages.success(request, f'Lesson "{lesson_title}" deleted successfully!')
    return redirect('admin_dashboard:module_edit', module_id=module_id)


@staff_member_required
def module_bulk_publish(request):
    """Bulk publish/unpublish modules"""
    if request.method == 'POST':
        module_ids = request.POST.getlist('module_ids')
        action = request.POST.get('action')
        
        if module_ids and action:
            modules = Module.objects.filter(id__in=module_ids)
            
            if action == 'publish':
                modules.update(is_published=True)
                messages.success(request, f'{modules.count()} modules published successfully!')
            elif action == 'unpublish':
                modules.update(is_published=False)
                messages.success(request, f'{modules.count()} modules unpublished successfully!')
            elif action == 'feature':
                modules.update(is_featured=True)
                messages.success(request, f'{modules.count()} modules marked as featured!')
            elif action == 'unfeature':
                modules.update(is_featured=False)
                messages.success(request, f'{modules.count()} modules unmarked as featured!')
            elif action == 'delete':
                count = modules.count()
                modules.delete()
                messages.success(request, f'{count} modules deleted successfully!')
        else:
            messages.error(request, 'Please select modules and an action.')
    
    return redirect('admin_dashboard:modules')


@staff_member_required
def content_analytics(request):
    """Content analytics and engagement metrics"""
    from elearning.models import Module, Lesson, Category, Enrollment
    from django.db.models import Sum, Avg, Count, Q, F
    
    # Module engagement metrics
    top_modules = Module.objects.filter(is_published=True).order_by('-views_count')[:10]
    most_enrolled = Module.objects.filter(is_published=True).order_by('-enrollments_count')[:10]
    highest_rated = Module.objects.filter(is_published=True, average_rating__gt=0).order_by('-average_rating')[:10]
    
    # Calculate completion rates for top modules
    for module in top_modules:
        total_enrollments = module.enrollment_set.count()
        completed = module.enrollment_set.filter(completed_at__isnull=False).count()
        module.completion_rate = round((completed / total_enrollments * 100), 1) if total_enrollments else 0
    
    # Category performance
    category_performance = Category.objects.annotate(
        total_views=Sum('modules__views_count'),
        total_enrollments=Sum('modules__enrollments_count'),
        avg_rating=Avg('modules__average_rating')
    ).order_by('-total_enrollments')
    
    # Content statistics
    total_content = {
        'modules': Module.objects.count(),
        'published_modules': Module.objects.filter(is_published=True).count(),
        'lessons': Lesson.objects.count(),
        'published_lessons': Lesson.objects.filter(is_published=True).count(),
        'video_lessons': Lesson.objects.filter(content_type='video').count(),
        'audio_lessons': Lesson.objects.filter(content_type='audio').count(),
        'text_lessons': Lesson.objects.filter(content_type='text').count(),
    }
    
    # Multilingual content coverage
    modules_with_bemba = Module.objects.exclude(title_bem='').exclude(title_bem__isnull=True).count()
    modules_with_nyanja = Module.objects.exclude(title_ny='').exclude(title_ny__isnull=True).count()
    total_modules = Module.objects.count()
    
    translation_coverage = {
        'bemba_percentage': round((modules_with_bemba / total_modules * 100), 1) if total_modules else 0,
        'nyanja_percentage': round((modules_with_nyanja / total_modules * 100), 1) if total_modules else 0,
        'bemba_count': modules_with_bemba,
        'nyanja_count': modules_with_nyanja,
    }
    
    # Location-based analytics (Kalingalinga, Kanyama, Chawama)
    location_analytics = []
    target_locations = ['Kalingalinga', 'Kanyama', 'Chawama']
    
    for location in target_locations:
        # Get users from this location
        users_in_location = CustomUser.objects.filter(location__icontains=location)
        
        # Get enrollments from these users
        enrollments = Enrollment.objects.filter(user__in=users_in_location)
        
        # Get most popular modules in this location
        popular_modules = Module.objects.filter(
            enrollment__user__in=users_in_location
        ).annotate(
            location_enrollments=Count('enrollment', filter=Q(enrollment__user__in=users_in_location))
        ).order_by('-location_enrollments')[:3]
        
        location_analytics.append({
            'name': location,
            'total_users': users_in_location.count(),
            'total_enrollments': enrollments.count(),
            'popular_modules': popular_modules,
        })
    
    # Language preference analytics
    language_usage = []
    for lang_code, lang_name in [('en', 'English'), ('bem', 'Bemba'), ('ny', 'Nyanja')]:
        users_count = CustomUser.objects.filter(preferred_language=lang_code).count()
        language_usage.append({
            'code': lang_code,
            'name': lang_name,
            'users': users_count,
        })
    
    context = {
        'top_modules': top_modules,
        'most_enrolled': most_enrolled,
        'highest_rated': highest_rated,
        'category_performance': category_performance,
        'total_content': total_content,
        'translation_coverage': translation_coverage,
        'location_analytics': location_analytics,
        'language_usage': language_usage,
    }
    
    return render(request, 'admin_dashboard/content_analytics.html', context)


@staff_member_required
def user_demographics(request):
    """Detailed demographics view"""
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Location breakdown (focus on Kalingalinga, Kanyama, Chawama)
    target_locations = ['Kalingalinga', 'Kanyama', 'Chawama']
    location_data = []
    
    for location in target_locations:
        count = CustomUser.objects.filter(location__icontains=location).count()
        location_data.append({
            'name': location,
            'count': count,
            'percentage': round((count / CustomUser.objects.count() * 100), 1) if CustomUser.objects.count() else 0
        })
    
    # Other locations
    other_count = CustomUser.objects.exclude(
        location__icontains='Kalingalinga'
    ).exclude(
        location__icontains='Kanyama'
    ).exclude(
        location__icontains='Chawama'
    ).count()
    
    location_data.append({
        'name': 'Other Locations',
        'count': other_count,
        'percentage': round((other_count / CustomUser.objects.count() * 100), 1) if CustomUser.objects.count() else 0
    })
    
    # Language distribution
    language_data = CustomUser.objects.values('preferred_language').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Registration trends by month
    monthly_registrations = []
    for i in range(12):
        month_start = timezone.now().replace(day=1) - timedelta(days=30 * i)
        month_end = month_start + timedelta(days=31)
        count = CustomUser.objects.filter(
            date_joined__gte=month_start,
            date_joined__lt=month_end
        ).count()
        monthly_registrations.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    monthly_registrations.reverse()
    
    context = {
        'location_data': location_data,
        'language_data': language_data,
        'monthly_registrations': monthly_registrations,
        'total_users': CustomUser.objects.count(),
        'target_users': 500,
    }
    
    return render(request, 'admin_dashboard/user_demographics.html', context)

@staff_member_required
def export_reports(request):
    import csv
    from django.http import HttpResponse
    from reporting.models import DumpingReport

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ecolearn_illegal_dumping_reports.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Ref No', 'Reporter', 'Phone', 'Location', 'Waste Type',
        'Severity', 'Status', 'Reported Date', 'Photos'
    ])

    reports = DumpingReport.objects.select_related('reporter__userprofile').all()
    for report in reports:
        phone = report.reporter.userprofile.phone_number if hasattr(report.reporter, 'userprofile') and report.reporter.userprofile.phone_number else 'N/A'
        photos = []
        if report.photo1: photos.append(report.photo1.url)
        if report.photo2: photos.append(report.photo2.url)
        if report.photo3: photos.append(report.photo3.url)
        photos_str = " | ".join(photos) if photos else "No photos"

        writer.writerow([
            f'ZMR{report.id:04d}',
            report.reporter.get_full_name() if not report.is_anonymous else 'Anonymous',
            phone,
            report.location_description or 'No description',
            report.get_waste_type_display(),
            report.get_severity_display(),
            report.get_status_display(),
            report.reported_at.strftime('%Y-%m-%d %H:%M'),
            photos_str
        ])

    return response

@staff_member_required
def mark_resolved(request, report_id):
    from reporting.models import DumpingReport
    report = get_object_or_404(DumpingReport, id=report_id)
    report.status = 'resolved'
    report.save()
    messages.success(request, f'Report ZMR{report.id:04d} marked as RESOLVED!')
    return redirect('admin_dashboard:reports')

@staff_member_required
def notify_lcc(request, report_id):
    messages.info(request, f'Notification sent to Lusaka City Council for report ZMR{report_id:04d}')
    return redirect('admin_dashboard:reports')

@login_required
def admin_dashboard(request):
    """
    Admin view to manage pending and in-progress reports.
    """
    if not request.user.is_staff:
        messages.error(request, 'Access denied. You must be staff to view the dashboard.')
        return redirect('reporting:reports_map')
    
    # Core Admin Task: View Pending Reports
    pending_reports = DumpingReport.objects.filter(status='pending').order_by('-reported_on')
    
    # Secondary Task: View Reports Needing Attention (e.g., in progress)
    in_progress_reports = DumpingReport.objects.filter(status='in_progress').order_by('-reported_on')

    # Status counts for dashboard metrics
    status_counts = DumpingReport.objects.values('status').annotate(count=Count('status'))
    
    context = {
        'pending_reports': pending_reports,
        'in_progress_reports': in_progress_reports,
        'status_counts': {item['status']: item['count'] for item in status_counts},
        # You will use the admin_dashboard.html template here
    }
    return render(request, 'admin_dashboard/admin_dashboard.html', context)

@staff_member_required
def assign_team(request, report_id):
    from reporting.models import DumpingReport
    from django.contrib import messages
    report = get_object_or_404(DumpingReport, id=report_id)
    report.status = 'in_progress'
    report.save()
    messages.success(request, f'Report ZMR{report.id:04d} assigned to cleanup team!')
    return redirect('admin_dashboard:reports')


# NOTIFICATION SYSTEM MANAGEMENT

@staff_member_required
def notification_management(request):
    """Notification System Dashboard"""
    from community.models import NotificationLog
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get statistics
    total_sent = NotificationLog.objects.count()
    today = timezone.now().date()
    sent_today = NotificationLog.objects.filter(sent_at__date=today).count()
    
    # Status breakdown
    status_stats = NotificationLog.objects.values('status').annotate(count=Count('id'))
    
    # Channel breakdown
    channel_stats = NotificationLog.objects.values('channel').annotate(count=Count('id'))
    
    # Recent notifications
    recent_notifications = NotificationLog.objects.select_related('user').order_by('-sent_at')[:20]
    
    # Calculate engagement rate
    delivered = NotificationLog.objects.filter(status='delivered').count()
    engagement_rate = round((delivered / total_sent * 100), 1) if total_sent > 0 else 0
    
    # Last 7 days trend
    seven_days_ago = timezone.now() - timedelta(days=7)
    daily_stats = []
    for i in range(7):
        day = timezone.now() - timedelta(days=i)
        count = NotificationLog.objects.filter(
            sent_at__date=day.date()
        ).count()
        daily_stats.append({
            'date': day.strftime('%b %d'),
            'count': count
        })
    daily_stats.reverse()
    
    context = {
        'total_sent': total_sent,
        'sent_today': sent_today,
        'engagement_rate': engagement_rate,
        'status_stats': status_stats,
        'channel_stats': channel_stats,
        'recent_notifications': recent_notifications,
        'daily_stats': daily_stats,
    }
    
    return render(request, 'admin_dashboard/notification_management.html', context)


@staff_member_required
def notification_create(request):
    """Create and send notification campaign"""
    from community.notifications import notification_service
    from community.models import NotificationLog
    from django.db.models import Q
    
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        message = request.POST.get('message')
        channels = request.POST.getlist('channels')  # ['sms', 'whatsapp', 'email']
        priority = request.POST.get('priority', 'normal')
        
        # Target audience filters
        target_all = request.POST.get('target_all') == 'on'
        target_locations = request.POST.getlist('locations')
        target_languages = request.POST.getlist('languages')
        target_roles = request.POST.getlist('roles')
        
        # Build user queryset
        users = CustomUser.objects.filter(is_active=True)
        
        if not target_all:
            if target_locations:
                location_q = Q()
                for loc in target_locations:
                    location_q |= Q(location__icontains=loc)
                users = users.filter(location_q)
            
            if target_languages:
                users = users.filter(preferred_language__in=target_languages)
            
            if target_roles:
                users = users.filter(role__in=target_roles)
        
        # Send notifications
        sent_count = 0
        failed_count = 0
        
        for user in users:
            for channel in channels:
                try:
                    # Create notification log
                    log = NotificationLog.objects.create(
                        user=user,
                        channel=channel,
                        notification_type='campaign',
                        message=message,
                        status='pending'
                    )
                    
                    # Send based on channel
                    if channel == 'sms' and user.phone_number:
                        result = notification_service.send_sms(
                            str(user.phone_number),
                            f"[EcoLearn] {message[:140]}"
                        )
                        if result.get('success'):
                            log.status = 'sent'
                            log.message_sid = result.get('message_sid', '')
                            sent_count += 1
                        else:
                            log.status = 'failed'
                            log.error_message = result.get('error', '')
                            failed_count += 1
                    
                    elif channel == 'whatsapp' and user.phone_number:
                        result = notification_service.send_whatsapp(
                            str(user.phone_number),
                            f"*{title}*\n\n{message}"
                        )
                        if result.get('success'):
                            log.status = 'sent'
                            log.message_sid = result.get('message_sid', '')
                            sent_count += 1
                        else:
                            log.status = 'failed'
                            log.error_message = result.get('error', '')
                            failed_count += 1
                    
                    elif channel == 'email' and user.email:
                        result = notification_service.send_email(
                            user.email,
                            title,
                            message
                        )
                        if result.get('success'):
                            log.status = 'sent'
                            sent_count += 1
                        else:
                            log.status = 'failed'
                            log.error_message = result.get('error', '')
                            failed_count += 1
                    
                    log.save()
                
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Notification send error: {str(e)}")
        
        messages.success(
            request,
            f'Campaign sent! {sent_count} notifications sent, {failed_count} failed.'
        )
        return redirect('admin_dashboard:notification_history')
    
    # GET request - show form
    locations = CustomUser.objects.values_list('location', flat=True).distinct()
    locations = [loc for loc in locations if loc]
    
    context = {
        'locations': locations,
        'language_choices': CustomUser.LANGUAGE_CHOICES,
        'role_choices': CustomUser.USER_ROLES,
    }
    
    return render(request, 'admin_dashboard/notification_create.html', context)


@staff_member_required
def notification_send(request):
    """Quick send notification (AJAX endpoint)"""
    from community.notifications import notification_service
    from community.models import NotificationLog
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            channel = data.get('channel')
            message = data.get('message')
            
            user = CustomUser.objects.get(id=user_id)
            
            # Create log
            log = NotificationLog.objects.create(
                user=user,
                channel=channel,
                notification_type='manual',
                message=message,
                status='pending'
            )
            
            # Send
            if channel == 'sms':
                result = notification_service.send_sms(str(user.phone_number), message)
            elif channel == 'whatsapp':
                result = notification_service.send_whatsapp(str(user.phone_number), message)
            elif channel == 'email':
                result = notification_service.send_email(user.email, 'EcoLearn Notification', message)
            
            if result.get('success'):
                log.status = 'sent'
                log.message_sid = result.get('message_sid', '')
            else:
                log.status = 'failed'
                log.error_message = result.get('error', '')
            
            log.save()
            
            return JsonResponse({'success': True, 'message': 'Notification sent!'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@staff_member_required
def notification_history(request):
    """View notification history with filters"""
    from community.models import NotificationLog
    from django.db.models import Q
    
    # Get filter parameters
    channel_filter = request.GET.get('channel', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    notifications = NotificationLog.objects.select_related('user').order_by('-sent_at')
    
    # Apply filters
    if channel_filter:
        notifications = notifications.filter(channel=channel_filter)
    
    if status_filter:
        notifications = notifications.filter(status=status_filter)
    
    if date_filter:
        from datetime import datetime
        date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
        notifications = notifications.filter(sent_at__date=date_obj)
    
    if search_query:
        notifications = notifications.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(notifications, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    total_notifications = notifications.count()
    sent_count = notifications.filter(status='sent').count()
    delivered_count = notifications.filter(status='delivered').count()
    failed_count = notifications.filter(status='failed').count()
    
    context = {
        'page_obj': page_obj,
        'total_notifications': total_notifications,
        'sent_count': sent_count,
        'delivered_count': delivered_count,
        'failed_count': failed_count,
        'channel_filter': channel_filter,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'search_query': search_query,
        'channel_choices': NotificationLog.CHANNEL_CHOICES,
        'status_choices': NotificationLog.STATUS_CHOICES,
    }
    
    return render(request, 'admin_dashboard/notification_history.html', context)


@staff_member_required
def notification_analytics(request):
    """Notification analytics and engagement metrics"""
    from community.models import NotificationLog
    from django.db.models import Count, Q, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # Date range
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # Total statistics
    total_sent = NotificationLog.objects.filter(sent_at__gte=start_date).count()
    total_delivered = NotificationLog.objects.filter(
        sent_at__gte=start_date,
        status='delivered'
    ).count()
    total_failed = NotificationLog.objects.filter(
        sent_at__gte=start_date,
        status='failed'
    ).count()
    
    # Engagement rate
    engagement_rate = round((total_delivered / total_sent * 100), 1) if total_sent > 0 else 0
    
    # Channel performance
    channel_performance = []
    for channel_code, channel_name in NotificationLog.CHANNEL_CHOICES:
        channel_total = NotificationLog.objects.filter(
            sent_at__gte=start_date,
            channel=channel_code
        ).count()
        channel_delivered = NotificationLog.objects.filter(
            sent_at__gte=start_date,
            channel=channel_code,
            status='delivered'
        ).count()
        channel_rate = round((channel_delivered / channel_total * 100), 1) if channel_total > 0 else 0
        
        channel_performance.append({
            'channel': channel_name,
            'total': channel_total,
            'delivered': channel_delivered,
            'rate': channel_rate
        })
    
    # Daily trend
    daily_trend = []
    for i in range(days):
        day = timezone.now() - timedelta(days=i)
        day_sent = NotificationLog.objects.filter(
            sent_at__date=day.date()
        ).count()
        day_delivered = NotificationLog.objects.filter(
            sent_at__date=day.date(),
            status='delivered'
        ).count()
        daily_trend.append({
            'date': day.strftime('%b %d'),
            'sent': day_sent,
            'delivered': day_delivered
        })
    daily_trend.reverse()
    
    # Notification type breakdown
    type_breakdown = NotificationLog.objects.filter(
        sent_at__gte=start_date
    ).values('notification_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Peak hours analysis
    hour_stats = []
    for hour in range(24):
        count = NotificationLog.objects.filter(
            sent_at__gte=start_date,
            sent_at__hour=hour
        ).count()
        hour_stats.append({
            'hour': f"{hour:02d}:00",
            'count': count
        })
    
    # Top users by notifications received
    top_users = NotificationLog.objects.filter(
        sent_at__gte=start_date
    ).values(
        'user__username', 'user__id'
    ).annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    context = {
        'days': days,
        'total_sent': total_sent,
        'total_delivered': total_delivered,
        'total_failed': total_failed,
        'engagement_rate': engagement_rate,
        'channel_performance': channel_performance,
        'daily_trend': daily_trend,
        'type_breakdown': type_breakdown,
        'hour_stats': hour_stats,
        'top_users': top_users,
    }
    
    return render(request, 'admin_dashboard/notification_analytics.html', context)


# ====================== EMERGENCY ALERT SYSTEM ======================

@staff_member_required
def emergency_alerts(request):
    """Emergency Health Alerts Dashboard"""
    from community.models import HealthAlert
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Get filter parameters
    alert_type_filter = request.GET.get('type', '')
    severity_filter = request.GET.get('severity', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    alerts = HealthAlert.objects.select_related('created_by').order_by('-created_at')
    
    # Apply filters
    if alert_type_filter:
        alerts = alerts.filter(alert_type=alert_type_filter)
    if severity_filter:
        alerts = alerts.filter(severity=severity_filter)
    if status_filter == 'active':
        alerts = alerts.filter(is_active=True)
    elif status_filter == 'expired':
        alerts = alerts.filter(is_active=False)
    
    # Statistics
    total_alerts = HealthAlert.objects.count()
    active_alerts = HealthAlert.objects.filter(is_active=True).count()
    critical_alerts = HealthAlert.objects.filter(severity='critical', is_active=True).count()
    
    # Recent alerts (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_alerts = HealthAlert.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Alert type breakdown
    alert_types = HealthAlert.objects.values('alert_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Severity breakdown
    severity_stats = HealthAlert.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'alerts': alerts,
        'total_alerts': total_alerts,
        'active_alerts': active_alerts,
        'critical_alerts': critical_alerts,
        'recent_alerts': recent_alerts,
        'alert_types': alert_types,
        'severity_stats': severity_stats,
        'alert_type_filter': alert_type_filter,
        'severity_filter': severity_filter,
        'status_filter': status_filter,
        'alert_type_choices': HealthAlert.ALERT_TYPES,
        'severity_choices': HealthAlert.SEVERITY_LEVELS,
    }
    
    return render(request, 'admin_dashboard/emergency_alerts.html', context)


@staff_member_required
def alert_create(request):
    """Create new emergency health alert"""
    from community.models import HealthAlert
    
    if request.method == 'POST':
        # Create alert
        alert = HealthAlert.objects.create(
            alert_type=request.POST.get('alert_type'),
            severity=request.POST.get('severity'),
            title=request.POST.get('title'),
            message=request.POST.get('message'),
            location=request.POST.get('location'),
            affected_areas=request.POST.get('affected_areas', ''),
            hygiene_tips=request.POST.get('hygiene_tips', ''),
            nearest_clinics=request.POST.get('nearest_clinics', ''),
            created_by=request.user,
            is_active=True
        )
        
        # Set expiry date if provided
        if request.POST.get('expires_at'):
            from datetime import datetime
            alert.expires_at = datetime.strptime(
                request.POST.get('expires_at'), 
                '%Y-%m-%dT%H:%M'
            )
            alert.save()
        
        # Automatically send alert if requested
        if request.POST.get('send_immediately') == 'on':
            return redirect('admin_dashboard:alert_send', alert_id=alert.id)
        
        messages.success(request, f'Emergency alert "{alert.title}" created successfully!')
        return redirect('admin_dashboard:alert_detail', alert_id=alert.id)
    
    context = {
        'alert_types': HealthAlert.ALERT_TYPES,
        'severity_levels': HealthAlert.SEVERITY_LEVELS,
    }
    
    return render(request, 'admin_dashboard/alert_create.html', context)


@staff_member_required
def alert_detail(request, alert_id):
    """View and manage specific alert"""
    from community.models import HealthAlert
    
    alert = get_object_or_404(HealthAlert, id=alert_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update':
            alert.title = request.POST.get('title')
            alert.message = request.POST.get('message')
            alert.location = request.POST.get('location')
            alert.affected_areas = request.POST.get('affected_areas', '')
            alert.hygiene_tips = request.POST.get('hygiene_tips', '')
            alert.nearest_clinics = request.POST.get('nearest_clinics', '')
            alert.severity = request.POST.get('severity')
            
            if request.POST.get('expires_at'):
                from datetime import datetime
                alert.expires_at = datetime.strptime(
                    request.POST.get('expires_at'), 
                    '%Y-%m-%dT%H:%M'
                )
            
            alert.save()
            messages.success(request, 'Alert updated successfully!')
        
        elif action == 'toggle_status':
            alert.is_active = not alert.is_active
            alert.save()
            status = "activated" if alert.is_active else "deactivated"
            messages.success(request, f'Alert {status}!')
        
        return redirect('admin_dashboard:alert_detail', alert_id=alert.id)
    
    context = {
        'alert': alert,
        'severity_choices': HealthAlert.SEVERITY_LEVELS,
    }
    
    return render(request, 'admin_dashboard/alert_detail.html', context)


@staff_member_required
def alert_send(request, alert_id):
    """Send emergency alert to users"""
    from community.models import HealthAlert
    from community.notifications import notification_service
    from accounts.models import CustomUser
    
    alert = get_object_or_404(HealthAlert, id=alert_id)
    
    if request.method == 'POST':
        # Get target parameters
        target_all = request.POST.get('target_all') == 'on'
        target_locations = request.POST.getlist('locations')
        channels = request.POST.getlist('channels', ['sms', 'whatsapp'])
        
        # Build user queryset
        users = CustomUser.objects.filter(is_active=True)
        
        if not target_all and target_locations:
            location_q = Q()
            for loc in target_locations:
                location_q |= Q(location__icontains=loc)
            users = users.filter(location_q)
        
        # Prepare emergency message
        severity_emoji = {
            'low': '⚠️',
            'medium': '🚨',
            'high': '🔴',
            'critical': '🚨🔴'
        }
        
        emoji = severity_emoji.get(alert.severity, '⚠️')
        
        # SMS message (short)
        sms_message = f"{emoji} HEALTH ALERT: {alert.title}. {alert.message[:100]}... Safety tips: {alert.hygiene_tips[:50]}..."
        
        # WhatsApp message (detailed)
        whatsapp_message = f"""
{emoji} *HEALTH ALERT - {alert.get_severity_display().upper()}*

*{alert.title}*

*Location:* {alert.location}
*Affected Areas:* {alert.affected_areas}

*Alert:*
{alert.message}

*Safety Tips:*
{alert.hygiene_tips}

*Nearest Clinics:*
{alert.nearest_clinics}

Stay safe! - EcoLearn Emergency System
        """.strip()
        
        # Send to users
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                if 'sms' in channels and user.phone_number:
                    result = notification_service.send_sms(
                        str(user.phone_number),
                        sms_message[:160]  # SMS limit
                    )
                    if result.get('success'):
                        sent_count += 1
                    else:
                        failed_count += 1
                
                if 'whatsapp' in channels and user.phone_number:
                    result = notification_service.send_whatsapp(
                        str(user.phone_number),
                        whatsapp_message
                    )
                    if result.get('success'):
                        sent_count += 1
                    else:
                        failed_count += 1
                
                # Always create in-app notification for emergencies
                from community.models import Notification
                Notification.objects.create(
                    user=user,
                    notification_type='emergency',
                    title=f"{emoji} {alert.title}",
                    message=alert.message,
                    url=f'/health-alerts/{alert.id}/'
                )
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Emergency alert send error: {str(e)}")
        
        messages.success(
            request,
            f'Emergency alert sent! {sent_count} notifications sent, {failed_count} failed.'
        )
        return redirect('admin_dashboard:emergency_alerts')
    
    # GET request - show send form
    locations = CustomUser.objects.values_list('location', flat=True).distinct()
    locations = [loc for loc in locations if loc]
    
    context = {
        'alert': alert,
        'locations': locations,
    }
    
    return render(request, 'admin_dashboard/alert_send.html', context)


@staff_member_required
def alert_deactivate(request, alert_id):
    """Deactivate emergency alert"""
    alert = get_object_or_404(HealthAlert, id=alert_id)
    alert.is_active = False
    alert.save()
    
    messages.success(request, f'Alert "{alert.title}" deactivated.')
    return redirect('admin_dashboard:emergency_alerts')


@staff_member_required
def priority_reports(request):
    """View priority reports that need escalation"""
    from reporting.models import DumpingReport
    from django.db.models import Q
    
    # Get high-priority reports
    priority_reports = DumpingReport.objects.filter(
        Q(severity__in=['high', 'critical']) |
        Q(waste_type__icontains='medical') |
        Q(waste_type__icontains='hazardous') |
        Q(description__icontains='medical') |
        Q(description__icontains='hospital') |
        Q(description__icontains='clinic')
    ).select_related('reporter').order_by('-reported_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        priority_reports = priority_reports.filter(status=status_filter)
    
    # Statistics
    total_priority = priority_reports.count()
    pending_escalation = priority_reports.filter(
        status__in=['pending', 'verified'],
        forwarded_to_authority=False
    ).count()
    
    medical_waste = priority_reports.filter(
        Q(waste_type__icontains='medical') |
        Q(description__icontains='medical')
    ).count()
    
    context = {
        'priority_reports': priority_reports,
        'total_priority': total_priority,
        'pending_escalation': pending_escalation,
        'medical_waste': medical_waste,
        'status_filter': status_filter,
        'status_choices': DumpingReport.STATUS_CHOICES,
    }
    
    return render(request, 'admin_dashboard/priority_reports.html', context)


@staff_member_required
def escalate_report(request, report_id):
    """Escalate priority report to ZEMA/LCC"""
    from reporting.models import DumpingReport, Authority
    from community.notifications import send_notification
    
    report = get_object_or_404(DumpingReport, id=report_id)
    
    if request.method == 'POST':
        authority_id = request.POST.get('authority')
        urgency = request.POST.get('urgency', 'high')
        notes = request.POST.get('escalation_notes', '')
        
        # Get authority
        authority = Authority.objects.get(id=authority_id)
        
        # Update report
        report.forwarded_to_authority = True
        report.authority_name = authority.name
        report.authority_contact = authority.contact_email
        report.status = 'in_progress'
        report.admin_notes = f"ESCALATED ({urgency.upper()}): {notes}\n\n{report.admin_notes or ''}"
        report.save()
        
        # Send urgent notification to authority (if email configured)
        if authority.contact_email:
            try:
                from django.core.mail import send_mail
                
                subject = f"🚨 URGENT: Priority Report Escalation - {report.reference_number}"
                
                message = f"""
URGENT PRIORITY REPORT ESCALATION

Report ID: {report.reference_number}
Severity: {report.get_severity_display()}
Waste Type: {report.waste_type}
Location: {report.location_description}

Description:
{report.description}

Escalation Notes:
{notes}

GPS Coordinates: {report.latitude}, {report.longitude}
Reported: {report.reported_at.strftime('%Y-%m-%d %H:%M')}
Reporter: {report.reporter.get_full_name() if report.reporter else 'Anonymous'}

Photos: {report.photos.count()} attached

Please take immediate action.

EcoLearn Emergency System
                """.strip()
                
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[authority.contact_email],
                    fail_silently=False
                )
                
            except Exception as e:
                logger.error(f"Failed to send escalation email: {str(e)}")
        
        # Notify reporter
        if report.reporter and not report.is_anonymous:
            send_notification(
                user=report.reporter,
                title=f'Report Escalated: {report.reference_number}',
                message=f'Your priority report has been escalated to {authority.name} for urgent action.',
                notification_type='report_update',
                link=f'/reporting/reports/{report.id}/'
            )
        
        # Create health alert if medical waste
        if 'medical' in report.waste_type.lower() or 'medical' in report.description.lower():
            from community.models import HealthAlert
            
            HealthAlert.objects.create(
                alert_type='hazardous_waste',
                severity='high',
                title=f'Medical Waste Alert - {report.location_description}',
                message=f'Medical waste reported at {report.location_description}. Avoid contact and keep children away.',
                location=report.location_description,
                affected_areas=report.location_description,
                hygiene_tips='Do not touch medical waste. Wash hands thoroughly if contact occurs. Seek medical attention if injured.',
                nearest_clinics='Contact nearest clinic immediately if exposure occurs.',
                created_by=request.user,
                is_active=True
            )
        
        messages.success(
            request,
            f'Report {report.reference_number} escalated to {authority.name}!'
        )
        return redirect('admin_dashboard:priority_reports')
    
    # GET request - show escalation form
    authorities = Authority.objects.filter(is_active=True)
    
    context = {
        'report': report,
        'authorities': authorities,
    }
    
    return render(request, 'admin_dashboard/escalate_report.html', context)


# ============================================================================
# GROUPS MANAGEMENT SECTION
# ============================================================================

@staff_member_required
def groups_management(request):
    """Groups Management Dashboard"""
    from collaboration.models import CleanupGroup, GroupMembership, GroupEvent, GroupImpactReport
    from django.db.models import Q, Count, Sum, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    district_filter = request.GET.get('district', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset with annotations (using different names to avoid conflicts)
    groups = CleanupGroup.objects.select_related('coordinator').annotate(
        members_total=Count('members'),
        events_total=Count('events'),
        completed_events=Count('events', filter=Q(events__status='completed')),
        total_waste_collected=Sum('events__waste_collected'),
        total_participants=Sum('events__participants_count')
    )
    
    # Apply filters
    if status_filter == 'active':
        groups = groups.filter(is_active=True)
    elif status_filter == 'inactive':
        groups = groups.filter(is_active=False)
    if district_filter:
        groups = groups.filter(district__icontains=district_filter)
    if search_query:
        groups = groups.filter(
            Q(name__icontains=search_query) |
            Q(community__icontains=search_query) |
            Q(coordinator__username__icontains=search_query) |
            Q(coordinator__first_name__icontains=search_query) |
            Q(coordinator__last_name__icontains=search_query)
        )
    
    groups = groups.order_by('-created_at')
    
    # Statistics
    total_groups = CleanupGroup.objects.count()
    active_groups = CleanupGroup.objects.filter(is_active=True).count()
    inactive_groups = CleanupGroup.objects.filter(is_active=False).count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_groups_month = CleanupGroup.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_events = GroupEvent.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Top performing groups
    top_groups = CleanupGroup.objects.annotate(
        completed_events_count=Count('events', filter=Q(events__status='completed'))
    ).order_by('-completed_events_count')[:5]
    
    # District breakdown
    district_stats = CleanupGroup.objects.values('district').annotate(
        count=Count('id'),
        active_count=Count('id', filter=Q(is_active=True))
    ).order_by('-count')[:10]
    
    # Social media adoption
    groups_with_social = CleanupGroup.objects.filter(
        Q(facebook_url__isnull=False, facebook_url__gt='') |
        Q(whatsapp_url__isnull=False, whatsapp_url__gt='') |
        Q(twitter_url__isnull=False, twitter_url__gt='')
    ).count()
    social_adoption_rate = round((groups_with_social / total_groups * 100), 1) if total_groups > 0 else 0
    
    # Total impact metrics
    total_events = GroupEvent.objects.filter(status='completed').count()
    total_waste_collected = GroupEvent.objects.filter(status='completed').aggregate(
        total=Sum('waste_collected')
    )['total'] or 0
    total_participants = GroupEvent.objects.filter(status='completed').aggregate(
        total=Sum('participants_count')
    )['total'] or 0
    
    context = {
        'groups': groups,
        'total_groups': total_groups,
        'active_groups': active_groups,
        'inactive_groups': inactive_groups,
        'new_groups_month': new_groups_month,
        'recent_events': recent_events,
        'top_groups': top_groups,
        'district_stats': district_stats,
        'groups_with_social': groups_with_social,
        'social_adoption_rate': social_adoption_rate,
        'total_events': total_events,
        'total_waste_collected': total_waste_collected,
        'total_participants': total_participants,
        # Filter values
        'status_filter': status_filter,
        'district_filter': district_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_dashboard/groups_management.html', context)


@staff_member_required
def group_detail_admin(request, group_id):
    """Detailed admin view of a specific group"""
    from collaboration.models import CleanupGroup, GroupMembership, GroupEvent, GroupImpactReport
    from community.notifications import send_notification
    
    group = get_object_or_404(CleanupGroup, id=group_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'toggle_status':
            group.is_active = not group.is_active
            group.save()
            
            status = "activated" if group.is_active else "deactivated"
            messages.success(request, f'Group {status} successfully!')
            
            # Notify coordinator
            send_notification(
                user=group.coordinator,
                title=f'Group Status Update',
                message=f'Your group "{group.name}" has been {status} by an administrator.',
                notification_type='group_update'
            )
        
        elif action == 'update_info':
            group.name = request.POST.get('name', group.name)
            group.description = request.POST.get('description', group.description)
            group.community = request.POST.get('community', group.community)
            group.district = request.POST.get('district', group.district)
            group.save()
            
            messages.success(request, 'Group information updated successfully!')
        
        return redirect('admin_dashboard:group_detail_admin', group_id=group.id)
    
    # Get group statistics
    members = GroupMembership.objects.filter(group=group, is_active=True).select_related('user')
    events = GroupEvent.objects.filter(group=group).order_by('-scheduled_date')
    reports = GroupImpactReport.objects.filter(group=group).order_by('-generated_at')
    
    # Calculate metrics
    completed_events = events.filter(status='completed')
    total_waste_collected = completed_events.aggregate(Sum('waste_collected'))['waste_collected__sum'] or 0
    total_participants = completed_events.aggregate(Sum('participants_count'))['participants_count__sum'] or 0
    
    # Recent activity
    recent_events = events[:5]
    recent_members = members.order_by('-joined_at')[:5]
    
    context = {
        'group': group,
        'members': members,
        'events': events,
        'reports': reports,
        'recent_events': recent_events,
        'recent_members': recent_members,
        'total_waste_collected': total_waste_collected,
        'total_participants': total_participants,
        'completed_events_count': completed_events.count(),
    }
    
    return render(request, 'admin_dashboard/group_detail_admin.html', context)


@staff_member_required
def groups_analytics(request):
    """Groups analytics and insights"""
    from collaboration.models import CleanupGroup, GroupEvent, GroupMembership
    from django.db.models import Count, Sum, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # Time-based analytics
    six_months_ago = timezone.now() - timedelta(days=180)
    
    # Group growth over time
    monthly_growth = []
    for i in range(6):
        month_start = timezone.now() - timedelta(days=30 * (i + 1))
        month_end = timezone.now() - timedelta(days=30 * i)
        count = CleanupGroup.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        monthly_growth.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    monthly_growth.reverse()
    
    # Impact metrics by district
    district_impact = CleanupGroup.objects.values('district').annotate(
        group_count=Count('id'),
        total_events=Count('events'),
        total_waste=Sum('events__waste_collected'),
        total_participants=Sum('events__participants_count')
    ).order_by('-total_waste')
    
    # Calculate average waste per group for each district
    district_impact_list = []
    for district in district_impact:
        avg_waste_per_group = 0
        if district['group_count'] > 0 and district['total_waste']:
            avg_waste_per_group = district['total_waste'] / district['group_count']
        
        district_impact_list.append({
            'district': district['district'],
            'group_count': district['group_count'],
            'total_events': district['total_events'] or 0,
            'total_waste': district['total_waste'] or 0,
            'total_participants': district['total_participants'] or 0,
            'avg_waste_per_group': round(avg_waste_per_group, 1)
        })
    
    # Social media adoption trends
    social_stats = {
        'facebook': CleanupGroup.objects.filter(facebook_url__isnull=False, facebook_url__gt='').count(),
        'whatsapp': CleanupGroup.objects.filter(whatsapp_url__isnull=False, whatsapp_url__gt='').count(),
        'twitter': CleanupGroup.objects.filter(twitter_url__isnull=False, twitter_url__gt='').count(),
    }
    
    # Group size distribution
    size_distribution = {
        'small': CleanupGroup.objects.annotate(members_count=Count('members')).filter(members_count__lt=10).count(),
        'medium': CleanupGroup.objects.annotate(members_count=Count('members')).filter(members_count__gte=10, members_count__lt=25).count(),
        'large': CleanupGroup.objects.annotate(members_count=Count('members')).filter(members_count__gte=25).count(),
    }
    
    # Most active coordinators
    active_coordinators = CleanupGroup.objects.values(
        'coordinator__username', 'coordinator__first_name', 'coordinator__last_name'
    ).annotate(
        groups_count=Count('id'),
        total_events=Count('events'),
        total_impact=Sum('events__waste_collected')
    ).order_by('-total_impact')[:10]
    
    context = {
        'monthly_growth': monthly_growth,
        'district_impact': district_impact_list,
        'social_stats': social_stats,
        'size_distribution': size_distribution,
        'active_coordinators': active_coordinators,
    }
    
    return render(request, 'admin_dashboard/groups_analytics.html', context)


@staff_member_required
def export_groups_data(request):
    """Export groups data to Excel"""
    from collaboration.models import CleanupGroup
    from django.http import HttpResponse
    from openpyxl import Workbook
    from django.utils import timezone
    from django.db.models import Count, Sum
    
    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Groups Data"
    
    # Headers
    headers = [
        'Group Name', 'Coordinator', 'Community', 'District', 'Members', 
        'Events', 'Waste Collected (kg)', 'Status', 'Created Date',
        'Facebook', 'WhatsApp', 'Twitter'
    ]
    ws.append(headers)
    
    # Data
    groups = CleanupGroup.objects.select_related('coordinator').annotate(
        members_count=Count('members'),
        event_count=Count('events'),
        waste_collected=Sum('events__waste_collected')
    )
    
    for group in groups:
        ws.append([
            group.name,
            group.coordinator.get_full_name() or group.coordinator.username,
            group.community,
            group.district,
            group.members_count,
            group.event_count,
            float(group.waste_collected or 0),
            'Active' if group.is_active else 'Inactive',
            group.created_at.strftime('%Y-%m-%d'),
            'Yes' if group.facebook_url else 'No',
            'Yes' if group.whatsapp_url else 'No',
            'Yes' if group.twitter_url else 'No',
        ])
    
    # Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=groups_data_{timezone.now().strftime("%Y%m%d")}.xlsx'
    
    wb.save(response)
    return response


# ============================================================================
# GROUPS MANAGEMENT SECTION
# ======================================================================

# ============================================================================
# ADMIN GROUPS PRIVILEGES - CREATE, EDIT, DELETE, MANAGE
# ============================================================================

@staff_member_required
def create_group_admin(request):
    """Admin view to create new cleanup groups"""
    from collaboration.models import CleanupGroup
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            description = request.POST.get('description')
            community = request.POST.get('community')
            district = request.POST.get('district')
            coordinator_id = request.POST.get('coordinator')
            
            # Social media links
            facebook_url = request.POST.get('facebook_url', '')
            whatsapp_url = request.POST.get('whatsapp_url', '')
            twitter_url = request.POST.get('twitter_url', '')
            
            # Validation
            if not all([name, description, community, district, coordinator_id]):
                messages.error(request, 'All required fields must be filled.')
                return redirect('admin_dashboard:create_group_admin')
            
            # Get coordinator
            coordinator = get_object_or_404(User, id=coordinator_id)
            
            # Create group
            group = CleanupGroup.objects.create(
                name=name,
                description=description,
                community=community,
                district=district,
                coordinator=coordinator,
                facebook_url=facebook_url,
                whatsapp_url=whatsapp_url,
                twitter_url=twitter_url,
                is_active=True
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                group.image = request.FILES['image']
                group.save()
            
            messages.success(request, f'Group "{name}" created successfully!')
            return redirect('admin_dashboard:group_detail_admin', group_id=group.id)
            
        except Exception as e:
            messages.error(request, f'Error creating group: {str(e)}')
            return redirect('admin_dashboard:create_group_admin')
    
    # GET request - show form
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
    
    context = {
        'users': users,
        'page_title': 'Create New Group',
    }
    return render(request, 'admin_dashboard/create_group_admin.html', context)


@staff_member_required
def edit_group_admin(request, group_id):
    """Admin view to edit cleanup groups"""
    from collaboration.models import CleanupGroup
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    group = get_object_or_404(CleanupGroup, id=group_id)
    
    if request.method == 'POST':
        try:
            # Update group data
            group.name = request.POST.get('name', group.name)
            group.description = request.POST.get('description', group.description)
            group.community = request.POST.get('community', group.community)
            group.district = request.POST.get('district', group.district)
            
            # Update coordinator if provided
            coordinator_id = request.POST.get('coordinator')
            if coordinator_id:
                coordinator = get_object_or_404(User, id=coordinator_id)
                group.coordinator = coordinator
            
            # Update social media links
            group.facebook_url = request.POST.get('facebook_url', '')
            group.whatsapp_url = request.POST.get('whatsapp_url', '')
            group.twitter_url = request.POST.get('twitter_url', '')
            
            # Handle image upload
            if 'image' in request.FILES:
                group.image = request.FILES['image']
            
            # Handle status change
            if 'is_active' in request.POST:
                group.is_active = request.POST.get('is_active') == 'on'
            
            group.save()
            
            messages.success(request, f'Group "{group.name}" updated successfully!')
            return redirect('admin_dashboard:group_detail_admin', group_id=group.id)
            
        except Exception as e:
            messages.error(request, f'Error updating group: {str(e)}')
    
    # GET request - show form
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
    
    context = {
        'group': group,
        'users': users,
        'page_title': f'Edit Group: {group.name}',
    }
    return render(request, 'admin_dashboard/edit_group_admin.html', context)


@staff_member_required
@require_POST
def delete_group_admin(request, group_id):
    """Admin view to delete cleanup groups"""
    from collaboration.models import CleanupGroup
    
    group = get_object_or_404(CleanupGroup, id=group_id)
    group_name = group.name
    
    try:
        # Check if group has events or members
        events_count = group.events.count()
        members_count = group.members.count()
        
        if events_count > 0 or members_count > 0:
            # Soft delete - deactivate instead of hard delete
            group.is_active = False
            group.save()
            messages.warning(request, f'Group "{group_name}" has been deactivated instead of deleted due to existing events or members.')
        else:
            # Hard delete if no dependencies
            group.delete()
            messages.success(request, f'Group "{group_name}" deleted successfully!')
        
        return redirect('admin_dashboard:groups_management')
        
    except Exception as e:
        messages.error(request, f'Error deleting group: {str(e)}')
        return redirect('admin_dashboard:group_detail_admin', group_id=group_id)


@staff_member_required
@require_POST
def toggle_group_status_admin(request, group_id):
    """Admin view to activate/deactivate groups"""
    from collaboration.models import CleanupGroup
    
    group = get_object_or_404(CleanupGroup, id=group_id)
    
    try:
        group.is_active = not group.is_active
        group.save()
        
        status = "activated" if group.is_active else "deactivated"
        messages.success(request, f'Group "{group.name}" {status} successfully!')
        
        return JsonResponse({
            'success': True,
            'status': group.is_active,
            'message': f'Group {status} successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating group status: {str(e)}'
        })


@staff_member_required
def manage_group_members_admin(request, group_id):
    """Admin view to manage group members"""
    from collaboration.models import CleanupGroup, GroupMembership
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    group = get_object_or_404(CleanupGroup, id=group_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_member':
            user_id = request.POST.get('user_id')
            role = request.POST.get('role', 'member')
            
            try:
                user = get_object_or_404(User, id=user_id)
                membership, created = GroupMembership.objects.get_or_create(
                    group=group,
                    user=user,
                    defaults={'role': role, 'is_active': True}
                )
                
                if created:
                    messages.success(request, f'{user.get_full_name() or user.username} added to group as {role}!')
                else:
                    messages.info(request, f'{user.get_full_name() or user.username} is already a member of this group.')
                    
            except Exception as e:
                messages.error(request, f'Error adding member: {str(e)}')
        
        elif action == 'remove_member':
            membership_id = request.POST.get('membership_id')
            
            try:
                membership = get_object_or_404(GroupMembership, id=membership_id, group=group)
                user_name = membership.user.get_full_name() or membership.user.username
                membership.delete()
                messages.success(request, f'{user_name} removed from group!')
                
            except Exception as e:
                messages.error(request, f'Error removing member: {str(e)}')
        
        elif action == 'update_role':
            membership_id = request.POST.get('membership_id')
            new_role = request.POST.get('new_role')
            
            try:
                membership = get_object_or_404(GroupMembership, id=membership_id, group=group)
                membership.role = new_role
                membership.save()
                
                user_name = membership.user.get_full_name() or membership.user.username
                messages.success(request, f'{user_name} role updated to {new_role}!')
                
            except Exception as e:
                messages.error(request, f'Error updating role: {str(e)}')
        
        return redirect('admin_dashboard:manage_group_members_admin', group_id=group_id)
    
    # GET request
    members = GroupMembership.objects.filter(group=group, is_active=True).select_related('user')
    available_users = User.objects.filter(is_active=True).exclude(
        id__in=members.values_list('user_id', flat=True)
    ).order_by('first_name', 'last_name', 'username')
    
    context = {
        'group': group,
        'members': members,
        'available_users': available_users,
        'role_choices': GroupMembership.ROLE_CHOICES,
        'page_title': f'Manage Members: {group.name}',
    }
    return render(request, 'admin_dashboard/manage_group_members_admin.html', context)


@staff_member_required
def bulk_group_actions_admin(request):
    """Admin view for bulk actions on groups"""
    from collaboration.models import CleanupGroup
    
    if request.method == 'POST':
        action = request.POST.get('action')
        group_ids = request.POST.getlist('group_ids')
        
        if not group_ids:
            messages.error(request, 'No groups selected.')
            return redirect('admin_dashboard:groups_management')
        
        groups = CleanupGroup.objects.filter(id__in=group_ids)
        
        try:
            if action == 'activate':
                groups.update(is_active=True)
                messages.success(request, f'{groups.count()} groups activated successfully!')
                
            elif action == 'deactivate':
                groups.update(is_active=False)
                messages.success(request, f'{groups.count()} groups deactivated successfully!')
                
            elif action == 'delete':
                # Check for dependencies before bulk delete
                groups_with_deps = []
                groups_to_delete = []
                
                for group in groups:
                    if group.events.count() > 0 or group.members.count() > 0:
                        groups_with_deps.append(group)
                    else:
                        groups_to_delete.append(group)
                
                # Delete groups without dependencies
                if groups_to_delete:
                    CleanupGroup.objects.filter(id__in=[g.id for g in groups_to_delete]).delete()
                    messages.success(request, f'{len(groups_to_delete)} groups deleted successfully!')
                
                # Deactivate groups with dependencies
                if groups_with_deps:
                    CleanupGroup.objects.filter(id__in=[g.id for g in groups_with_deps]).update(is_active=False)
                    messages.warning(request, f'{len(groups_with_deps)} groups deactivated instead of deleted due to existing events or members.')
            
        except Exception as e:
            messages.error(request, f'Error performing bulk action: {str(e)}')
    
    return redirect('admin_dashboard:groups_management')


@staff_member_required
def group_statistics_admin(request):
    """Admin view for detailed group statistics"""
    from collaboration.models import CleanupGroup, GroupEvent, GroupMembership
    from django.db.models import Avg, Count, Q
    from django.db.models.functions import TruncMonth
    
    # Basic statistics
    total_groups = CleanupGroup.objects.count()
    active_groups = CleanupGroup.objects.filter(is_active=True).count()
    inactive_groups = total_groups - active_groups
    
    # Growth statistics
    thirty_days_ago = timezone.now() - timedelta(days=30)
    ninety_days_ago = timezone.now() - timedelta(days=90)
    
    new_groups_30d = CleanupGroup.objects.filter(created_at__gte=thirty_days_ago).count()
    new_groups_90d = CleanupGroup.objects.filter(created_at__gte=ninety_days_ago).count()
    
    # Performance statistics
    avg_members_per_group = GroupMembership.objects.filter(is_active=True).values('group').annotate(
        member_count=Count('user')
    ).aggregate(avg_members=Avg('member_count'))['avg_members'] or 0
    
    avg_events_per_group = GroupEvent.objects.values('group').annotate(
        event_count=Count('id')
    ).aggregate(avg_events=Avg('event_count'))['avg_events'] or 0
    
    # District distribution
    district_stats = CleanupGroup.objects.values('district').annotate(
        total_count=Count('id'),
        active_count=Count('id', filter=Q(is_active=True))
    ).order_by('-total_count')
    
    # Monthly growth chart data
    monthly_growth_data = CleanupGroup.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=365)
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Format monthly growth data for template
    monthly_growth = []
    for item in monthly_growth_data:
        monthly_growth.append({
            'month': item['month'].strftime('%b %Y') if item['month'] else '',
            'count': item['count']
        })
    
    # Social media adoption
    groups_with_social = CleanupGroup.objects.filter(
        Q(facebook_url__isnull=False, facebook_url__gt='') |
        Q(whatsapp_url__isnull=False, whatsapp_url__gt='') |
        Q(twitter_url__isnull=False, twitter_url__gt='')
    ).count()
    
    social_adoption_rate = (groups_with_social / total_groups * 100) if total_groups > 0 else 0
    
    context = {
        'total_groups': total_groups,
        'active_groups': active_groups,
        'inactive_groups': inactive_groups,
        'new_groups_30d': new_groups_30d,
        'new_groups_90d': new_groups_90d,
        'avg_members_per_group': round(avg_members_per_group, 1),
        'avg_events_per_group': round(avg_events_per_group, 1),
        'district_stats': district_stats,
        'monthly_growth': monthly_growth,
        'groups_with_social': groups_with_social,
        'social_adoption_rate': round(social_adoption_rate, 1),
        'page_title': 'Group Statistics',
    }
    
    return render(request, 'admin_dashboard/group_statistics_admin.html', context)