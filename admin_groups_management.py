#!/usr/bin/env python
"""
Groups Management Views for Admin Dashboard
"""

# Add these functions to admin_dashboard/views.py

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
    
    # Base queryset with annotations
    groups = CleanupGroup.objects.select_related('coordinator').annotate(
        member_count=Count('members'),
        event_count=Count('events'),
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
        total_impact=Count('events', filter=Q(events__status='completed'))
    ).order_by('-total_impact')[:5]
    
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
    
    # Social media adoption trends
    social_stats = {
        'facebook': CleanupGroup.objects.filter(facebook_url__isnull=False, facebook_url__gt='').count(),
        'whatsapp': CleanupGroup.objects.filter(whatsapp_url__isnull=False, whatsapp_url__gt='').count(),
        'twitter': CleanupGroup.objects.filter(twitter_url__isnull=False, twitter_url__gt='').count(),
    }
    
    # Group size distribution
    size_distribution = {
        'small': CleanupGroup.objects.annotate(member_count=Count('members')).filter(member_count__lt=10).count(),
        'medium': CleanupGroup.objects.annotate(member_count=Count('members')).filter(member_count__gte=10, member_count__lt=25).count(),
        'large': CleanupGroup.objects.annotate(member_count=Count('members')).filter(member_count__gte=25).count(),
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
        'district_impact': district_impact,
        'social_stats': social_stats,
        'size_distribution': size_distribution,
        'active_coordinators': active_coordinators,
    }
    
    return render(request, 'admin_dashboard/groups_analytics.html', context)


@staff_member_required
def group_events_admin(request, group_id):
    """Manage group events"""
    from collaboration.models import CleanupGroup, GroupEvent
    
    group = get_object_or_404(CleanupGroup, id=group_id)
    events = GroupEvent.objects.filter(group=group).order_by('-scheduled_date')
    
    # Event statistics
    total_events = events.count()
    completed_events = events.filter(status='completed').count()
    upcoming_events = events.filter(scheduled_date__gte=timezone.now()).count()
    
    context = {
        'group': group,
        'events': events,
        'total_events': total_events,
        'completed_events': completed_events,
        'upcoming_events': upcoming_events,
    }
    
    return render(request, 'admin_dashboard/group_events_admin.html', context)


@staff_member_required
def export_groups_data(request):
    """Export groups data to Excel"""
    from collaboration.models import CleanupGroup
    from django.http import HttpResponse
    from openpyxl import Workbook
    from django.utils import timezone
    
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
        member_count=Count('members'),
        event_count=Count('events'),
        waste_collected=Sum('events__waste_collected')
    )
    
    for group in groups:
        ws.append([
            group.name,
            group.coordinator.get_full_name() or group.coordinator.username,
            group.community,
            group.district,
            group.member_count,
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