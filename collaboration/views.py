from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.utils import timezone
from .models import (
    CleanupGroup, GroupMembership, GroupEvent, GroupChat,
    GroupImpactReport
)


@login_required
def groups_list(request):
    """Display all cleanup groups"""
    groups = CleanupGroup.objects.filter(is_active=True).order_by('-created_at')
    
    # Get user's groups
    user_groups = request.user.cleanup_groups.all()
    
    context = {
        'groups': groups,
        'user_groups': user_groups,
    }
    return render(request, 'collaboration/groups_list.html', context)


@login_required
def group_detail(request, group_id):
    """Display group details"""
    group = get_object_or_404(CleanupGroup, id=group_id, is_active=True)
    
    # Check if user is a member
    is_member = group.members.filter(id=request.user.id).exists()
    membership = None
    
    if is_member:
        membership = GroupMembership.objects.get(group=group, user=request.user)
    
    # Get group events
    upcoming_events = group.events.filter(
        scheduled_date__gte=timezone.now(),
        status__in=['planned', 'ongoing']
    ).order_by('scheduled_date')[:5]
    
    past_events = group.events.filter(
        status='completed'
    ).order_by('-scheduled_date')[:5]
    
    # Get recent chat messages
    recent_chats = group.chats.select_related('sender').order_by('-created_at')[:20]
    
    context = {
        'group': group,
        'is_member': is_member,
        'membership': membership,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'recent_chats': recent_chats,
    }
    return render(request, 'collaboration/group_detail.html', context)


@login_required
def create_group(request):
    """Create a new cleanup group"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        community = request.POST.get('community')
        district = request.POST.get('district')
        
        # Social media fields (limited to 3 platforms)
        facebook_url = request.POST.get('facebook_url', '')
        whatsapp_url = request.POST.get('whatsapp_url', '')
        twitter_url = request.POST.get('twitter_url', '')
        
        group = CleanupGroup.objects.create(
            name=name,
            description=description,
            community=community,
            district=district,
            coordinator=request.user,
            facebook_url=facebook_url,
            whatsapp_url=whatsapp_url,
            twitter_url=twitter_url
        )
        
        # Add creator as coordinator
        GroupMembership.objects.create(
            group=group,
            user=request.user,
            role='coordinator'
        )
        
        messages.success(request, f'Group "{name}" created successfully!')
        return redirect('collaboration:group_detail', group_id=group.id)
    
    return render(request, 'collaboration/create_group.html')


@login_required
def join_group(request, group_id):
    """Join a cleanup group"""
    if request.method == 'POST':
        group = get_object_or_404(CleanupGroup, id=group_id, is_active=True)
        
        membership, created = GroupMembership.objects.get_or_create(
            group=group,
            user=request.user,
            defaults={'role': 'member'}
        )
        
        if created:
            messages.success(request, f'You have joined {group.name}!')
        else:
            messages.info(request, 'You are already a member of this group.')
        
        return redirect('collaboration:group_detail', group_id=group.id)
    
    return redirect('collaboration:groups_list')


@login_required
def leave_group(request, group_id):
    """Leave a cleanup group"""
    if request.method == 'POST':
        group = get_object_or_404(CleanupGroup, id=group_id)
        
        # Check if user is coordinator
        if group.coordinator == request.user:
            messages.error(request, 'Coordinators cannot leave the group. Please transfer coordination first.')
        else:
            GroupMembership.objects.filter(group=group, user=request.user).delete()
            messages.success(request, f'You have left {group.name}.')
        
        return redirect('collaboration:groups_list')
    
    return redirect('collaboration:group_detail', group_id=group_id)


@login_required
def create_event(request, group_id):
    """Create a group event"""
    group = get_object_or_404(CleanupGroup, id=group_id, is_active=True)
    
    # Check if user is coordinator or moderator
    membership = GroupMembership.objects.filter(
        group=group,
        user=request.user,
        role__in=['coordinator', 'moderator']
    ).first()
    
    if not membership:
        messages.error(request, 'Only coordinators and moderators can create events.')
        return redirect('collaboration:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        scheduled_date = request.POST.get('scheduled_date')
        duration_hours = request.POST.get('duration_hours', 2)
        
        event = GroupEvent.objects.create(
            group=group,
            title=title,
            description=description,
            location=location,
            scheduled_date=scheduled_date,
            duration_hours=duration_hours,
            created_by=request.user
        )
        
        messages.success(request, f'Event "{title}" created successfully!')
        return redirect('collaboration:group_detail', group_id=group.id)
    
    context = {
        'group': group,
    }
    return render(request, 'collaboration/create_event.html', context)


@login_required
def send_chat_message(request, group_id):
    """Send a chat message to group"""
    if request.method == 'POST':
        group = get_object_or_404(CleanupGroup, id=group_id, is_active=True)
        
        # Check if user is a member
        if not group.members.filter(id=request.user.id).exists():
            return JsonResponse({'error': 'You must be a member to send messages'}, status=403)
        
        message = request.POST.get('message')
        is_announcement = request.POST.get('is_announcement', False)
        
        # Check if user can send announcements
        if is_announcement:
            membership = GroupMembership.objects.get(group=group, user=request.user)
            if membership.role not in ['coordinator', 'moderator']:
                is_announcement = False
        
        chat = GroupChat.objects.create(
            group=group,
            sender=request.user,
            message=message,
            is_announcement=is_announcement
        )
        
        return JsonResponse({
            'success': True,
            'chat_id': chat.id,
            'sender': request.user.get_full_name() or request.user.username,
            'message': chat.message,
            'timestamp': chat.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def get_chat_messages(request, group_id):
    """Get chat messages for a group"""
    group = get_object_or_404(CleanupGroup, id=group_id, is_active=True)
    
    # Check if user is a member
    if not group.members.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'You must be a member to view messages'}, status=403)
    
    chats = group.chats.select_related('sender').order_by('-created_at')[:50]
    
    messages_data = [{
        'id': chat.id,
        'sender': chat.sender.get_full_name() or chat.sender.username,
        'message': chat.message,
        'is_announcement': chat.is_announcement,
        'timestamp': chat.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for chat in reversed(chats)]
    
    return JsonResponse({'messages': messages_data})


@login_required
def generate_impact_report(request, group_id):
    """Generate impact report for a group"""
    group = get_object_or_404(CleanupGroup, id=group_id, is_active=True)
    
    # Check if user is coordinator
    if group.coordinator != request.user:
        messages.error(request, 'Only coordinators can generate reports.')
        return redirect('collaboration:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        period_start = request.POST.get('period_start')
        period_end = request.POST.get('period_end')
        
        # Calculate metrics
        events = group.events.filter(
            scheduled_date__range=[period_start, period_end],
            status='completed'
        )
        
        total_events = events.count()
        total_participants = events.aggregate(Sum('participants_count'))['participants_count__sum'] or 0
        waste_collected = events.aggregate(Sum('waste_collected'))['waste_collected__sum'] or 0
        
        # Create report
        report = GroupImpactReport.objects.create(
            group=group,
            report_period_start=period_start,
            report_period_end=period_end,
            total_events=total_events,
            total_participants=total_participants,
            waste_collected_kg=waste_collected,
            generated_by=request.user
        )
        
        messages.success(request, 'Impact report generated successfully!')
        return redirect('collaboration:view_report', report_id=report.id)
    
    context = {
        'group': group,
    }
    return render(request, 'collaboration/generate_report.html', context)


@login_required
def view_report(request, report_id):
    """View impact report"""
    report = get_object_or_404(GroupImpactReport, id=report_id)
    
    # Check if user is a member of the group
    if not report.group.members.filter(id=request.user.id).exists():
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('collaboration:groups_list')
    
    context = {
        'report': report,
    }
    return render(request, 'collaboration/view_report.html', context)


@login_required
def my_groups(request):
    """Display user's groups"""
    user_groups = request.user.cleanup_groups.filter(is_active=True)
    
    # Get coordinated groups
    coordinated_groups = CleanupGroup.objects.filter(
        coordinator=request.user,
        is_active=True
    )
    
    context = {
        'user_groups': user_groups,
        'coordinated_groups': coordinated_groups,
    }
    return render(request, 'collaboration/my_groups.html', context)


@login_required
def edit_group(request, group_id):
    """Edit group details including social media links"""
    group = get_object_or_404(CleanupGroup, id=group_id, is_active=True)
    
    # Check if user is coordinator
    if group.coordinator != request.user:
        messages.error(request, 'Only coordinators can edit group details.')
        return redirect('collaboration:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        # Update basic info
        group.name = request.POST.get('name', group.name)
        group.description = request.POST.get('description', group.description)
        group.community = request.POST.get('community', group.community)
        group.district = request.POST.get('district', group.district)
        
        # Update social media links (limited to 3 platforms)
        group.facebook_url = request.POST.get('facebook_url', '')
        group.whatsapp_url = request.POST.get('whatsapp_url', '')
        group.twitter_url = request.POST.get('twitter_url', '')
        
        group.save()
        
        messages.success(request, 'Group details updated successfully!')
        return redirect('collaboration:group_detail', group_id=group.id)
    
    context = {
        'group': group,
    }
    return render(request, 'collaboration/edit_group.html', context)
