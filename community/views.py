from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import (
    ForumCategory, ForumTopic, ForumReply, CommunityEvent, 
    EventParticipant, SuccessStory, SocialMediaShare, Notification,
    CommunityCampaign, CampaignParticipant
)
from .forms import TopicForm, ReplyForm, EventForm, SuccessStoryForm
import requests
from django.conf import settings


@login_required
def forum_home(request):
    categories = ForumCategory.objects.filter(is_active=True)
    recent_topics = ForumTopic.objects.select_related('author', 'category').order_by('-created_at')[:10]
    
    context = {
        'categories': categories,
        'recent_topics': recent_topics,
    }
    return render(request, 'community/forum_home.html', context)


@login_required
def category_topics(request, category_id):
    category = get_object_or_404(ForumCategory, id=category_id, is_active=True)
    topics = ForumTopic.objects.filter(category=category).select_related('author')
    
    # Pagination
    paginator = Paginator(topics, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'community/category_topics.html', context)


@login_required
def topic_detail(request, topic_id):
    topic = get_object_or_404(ForumTopic, id=topic_id)
    replies = topic.replies.select_related('author').order_by('created_at')
    
    # Increment view count
    topic.views += 1
    topic.save(update_fields=['views'])
    
    # Handle reply form
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.topic = topic
            reply.author = request.user
            reply.save()
            messages.success(request, 'Your reply has been posted!')
            
            # REAL-TIME NOTIFICATION: Notify topic creator of new reply
            if topic.author != request.user:  # Don't notify if replying to own topic
                try:
                    from .notifications import notification_service
                    
                    prefs = getattr(topic.author, 'notification_preferences', None)
                    
                    # SMS notification
                    if prefs and prefs.sms_enabled and prefs.forum_replies and topic.author.phone_number:
                        sms_message = f"New reply in '{topic.title}' by {request.user.username}"
                        result = notification_service.send_sms(str(topic.author.phone_number), sms_message)
                        if result.get('success'):
                            print(f"✅ Forum reply SMS sent to {topic.author.username}")
                    
                    # WhatsApp notification
                    if prefs and prefs.whatsapp_enabled and prefs.forum_replies and topic.author.phone_number:
                        whatsapp_message = f"💬 *New Reply in Your Topic*\n\n*Topic:* {topic.title}\n*Reply by:* {request.user.username}\n\n{reply.content[:100]}{'...' if len(reply.content) > 100 else ''}"
                        result = notification_service.send_whatsapp(str(topic.author.phone_number), whatsapp_message)
                        if result.get('success'):
                            print(f"✅ Forum reply WhatsApp sent to {topic.author.username}")
                    
                    # In-app notification
                    Notification.objects.create(
                        user=topic.author,
                        notification_type='forum_reply',
                        title=f'New reply in "{topic.title}"',
                        message=f'{request.user.username} replied to your topic.',
                        url=topic.get_absolute_url()
                    )
                except Exception as e:
                    print(f"Forum reply notification error: {e}")
            
            return redirect('community:topic_detail', topic_id=topic.id)
    else:
        form = ReplyForm()
    
    context = {
        'topic': topic,
        'replies': replies,
        'form': form,
    }
    return render(request, 'community/topic_detail.html', context)


@login_required
def create_topic(request, category_id):
    category = get_object_or_404(ForumCategory, id=category_id, is_active=True)
    
    if request.method == 'POST':
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.category = category
            topic.author = request.user
            topic.save()
            messages.success(request, 'Topic created successfully!')
            return redirect('community:topic_detail', topic_id=topic.id)
    else:
        form = TopicForm()
    
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'community/create_topic.html', context)


@login_required
def start_discussion(request):
    """Allow users to start a discussion and choose the category"""
    categories = ForumCategory.objects.filter(is_active=True)
    
    if request.method == 'POST':
        category_id = request.POST.get('category')
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if category_id and title and content:
            try:
                category = ForumCategory.objects.get(id=category_id, is_active=True)
                topic = ForumTopic.objects.create(
                    title=title,
                    content=content,
                    category=category,
                    author=request.user
                )
                messages.success(request, 'Discussion started successfully!')
                return redirect('community:topic_detail', topic_id=topic.id)
            except ForumCategory.DoesNotExist:
                messages.error(request, 'Invalid category selected.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'categories': categories,
    }
    return render(request, 'community/start_discussion.html', context)


@login_required
def events_list(request):
    upcoming_events = CommunityEvent.objects.filter(
        start_date__gte=timezone.now(),
        is_active=True
    ).order_by('start_date')
    
    past_events = CommunityEvent.objects.filter(
        end_date__lt=timezone.now(),
        is_active=True
    ).order_by('-start_date')[:5]
    
    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }
    return render(request, 'community/events_list.html', context)


@login_required
def event_detail(request, event_id):
    event = get_object_or_404(CommunityEvent, id=event_id, is_active=True)
    is_registered = False
    
    if request.user.is_authenticated:
        is_registered = EventParticipant.objects.filter(
            event=event, user=request.user
        ).exists()
    
    context = {
        'event': event,
        'is_registered': is_registered,
    }
    return render(request, 'community/event_detail.html', context)


@login_required
def register_event(request, event_id):
    event = get_object_or_404(CommunityEvent, id=event_id, is_active=True)
    
    if request.method == 'POST':
        # Check if already registered
        if EventParticipant.objects.filter(event=event, user=request.user).exists():
            messages.warning(request, 'You are already registered for this event.')
        elif event.is_full:
            messages.error(request, 'This event is full.')
        elif event.registration_deadline and timezone.now() > event.registration_deadline:
            messages.error(request, 'Registration deadline has passed.')
        else:
            EventParticipant.objects.create(event=event, user=request.user)
            messages.success(request, 'Successfully registered for the event!')
            
            # Send notification
            Notification.objects.create(
                user=request.user,
                notification_type='event_reminder',
                title=f'Registered for {event.title}',
                message=f'You have successfully registered for {event.title} on {event.start_date.strftime("%B %d, %Y")}.'
            )
    
    return redirect('community:event_detail', event_id=event.id)


@login_required
def success_stories(request):
    stories = SuccessStory.objects.filter(is_approved=True).select_related('author')
    
    # Filter by type if specified
    story_type = request.GET.get('type')
    if story_type:
        stories = stories.filter(story_type=story_type)
    
    # Pagination
    paginator = Paginator(stories, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'story_types': SuccessStory.STORY_TYPES,
        'current_type': story_type,
    }
    return render(request, 'community/success_stories.html', context)


@login_required
def story_detail(request, story_id):
    story = get_object_or_404(SuccessStory, id=story_id, is_approved=True)
    user_liked = False
    
    if request.user.is_authenticated:
        user_liked = story.likes.filter(id=request.user.id).exists()
    
    # Get related stories
    related_stories = SuccessStory.objects.filter(
        is_approved=True,
        story_type=story.story_type
    ).exclude(id=story.id).order_by('-created_at')[:3]
    
    context = {
        'story': story,
        'user_liked': user_liked,
        'related_stories': related_stories,
    }
    return render(request, 'community/story_detail.html', context)


@login_required
def create_story(request):
    if request.method == 'POST':
        form = SuccessStoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            messages.success(request, 'Your success story has been submitted for review!')
            return redirect('community:success_stories')
    else:
        form = SuccessStoryForm()
    
    context = {
        'form': form,
    }
    return render(request, 'community/create_story.html', context)


@login_required
def like_story(request, story_id):
    if request.method == 'POST':
        story = get_object_or_404(SuccessStory, id=story_id, is_approved=True)
        
        if story.likes.filter(id=request.user.id).exists():
            story.likes.remove(request.user)
            liked = False
        else:
            story.likes.add(request.user)
            liked = True
        
        return JsonResponse({
            'liked': liked,
            'like_count': story.like_count
        })
    
    return JsonResponse({'error': 'Invalid request'})


@login_required
def share_content(request):
    if request.method == 'POST':
        platform = request.POST.get('platform')
        content_type = request.POST.get('content_type')
        content_id = request.POST.get('content_id')
        
        # Record the share
        SocialMediaShare.objects.create(
            user=request.user,
            platform=platform,
            content_type=content_type,
            content_id=content_id
        )
        
        # Generate share URLs
        share_urls = {
            'whatsapp': f"https://wa.me/?text={request.build_absolute_uri()}",
            'facebook': f"https://www.facebook.com/sharer/sharer.php?u={request.build_absolute_uri()}",
            'twitter': f"https://twitter.com/intent/tweet?url={request.build_absolute_uri()}",
        }
        
        return JsonResponse({
            'success': True,
            'share_url': share_urls.get(platform, '')
        })
    
    return JsonResponse({'error': 'Invalid request'})


@login_required
def notifications_view(request):
    # Get filter type
    filter_type = request.GET.get('type', 'all')
    
    # Base query
    notifications = Notification.objects.filter(user=request.user)
    
    # Apply filter
    if filter_type == 'events':
        notifications = notifications.filter(notification_type__in=['event_reminder', 'new_event'])
    elif filter_type == 'challenges':
        notifications = notifications.filter(notification_type='challenge_update')
    elif filter_type == 'forum':
        notifications = notifications.filter(notification_type='forum_reply')
    elif filter_type == 'rewards':
        notifications = notifications.filter(notification_type='reward_redeemed')
    elif filter_type == 'community':
        notifications = notifications.filter(notification_type__in=['campaign_launch', 'community_news', 'general'])
    
    notifications = notifications.order_by('-created_at')
    
    # Handle mark all as read
    if request.method == 'POST' and 'mark_all_read' in request.POST:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read!')
        return redirect('community:notifications')
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get counts for filters
    all_count = Notification.objects.filter(user=request.user).count()
    events_count = Notification.objects.filter(user=request.user, notification_type__in=['event_reminder', 'new_event']).count()
    challenges_count = Notification.objects.filter(user=request.user, notification_type='challenge_update').count()
    forum_count = Notification.objects.filter(user=request.user, notification_type='forum_reply').count()
    rewards_count = Notification.objects.filter(user=request.user, notification_type='reward_redeemed').count()
    community_count = Notification.objects.filter(user=request.user, notification_type__in=['campaign_launch', 'community_news', 'general']).count()
    
    context = {
        'page_obj': page_obj,
        'filter_type': filter_type,
        'all_count': all_count,
        'events_count': events_count,
        'challenges_count': challenges_count,
        'forum_count': forum_count,
        'rewards_count': rewards_count,
        'community_count': community_count,
    }
    return render(request, 'community/notifications.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def notification_count(request):
    """Get unread notification count for live updates"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


# ===================================================================
# HEALTH ALERTS & EMERGENCY NOTIFICATIONS
# ===================================================================

@login_required
def health_alerts(request):
    """Display active health alerts"""
    from .models import HealthAlert
    
    active_alerts = HealthAlert.objects.filter(
        is_active=True
    ).order_by('-severity', '-created_at')
    
    context = {
        'alerts': active_alerts,
    }
    return render(request, 'community/health_alerts.html', context)


@login_required
def alert_detail(request, alert_id):
    """View detailed health alert information"""
    from .models import HealthAlert
    
    alert = get_object_or_404(HealthAlert, id=alert_id)
    
    context = {
        'alert': alert,
    }
    return render(request, 'community/alert_detail.html', context)


def send_emergency_sms(user, alert):
    """Send emergency SMS alert to user"""
    try:
        from twilio.rest import Client
        
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_number = settings.TWILIO_PHONE_NUMBER
        
        client = Client(account_sid, auth_token)
        
        message_body = f"⚠️ EMERGENCY ALERT: {alert.title}\n{alert.message}\n{alert.hygiene_tips}"
        
        if user.phone_number:
            message = client.messages.create(
                body=message_body,
                from_=twilio_number,
                to=str(user.phone_number)
            )
            return True
    except Exception as e:
        print(f"SMS Error: {e}")
        return False


def send_whatsapp_alert(user, alert):
    """Send WhatsApp alert to user"""
    try:
        from twilio.rest import Client
        
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        
        client = Client(account_sid, auth_token)
        
        message_body = f"⚠️ *{alert.title}*\n\n{alert.message}\n\n*Hygiene Tips:*\n{alert.hygiene_tips}\n\n*Nearest Clinics:*\n{alert.nearest_clinics}"
        
        if user.phone_number:
            message = client.messages.create(
                body=message_body,
                from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
                to=f'whatsapp:{user.phone_number}'
            )
            return True
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return False


# ===================================================================
# COMMUNITY CAMPAIGNS (FR08 & FR09)
# ===================================================================

@login_required
def campaigns_list(request):
    """Display active and upcoming community campaigns (FR08)"""
    from .models import CommunityCampaign, CampaignParticipant
    
    # Get active and published campaigns
    upcoming_campaigns = CommunityCampaign.objects.filter(
        is_active=True,
        is_published=True,
        start_date__gte=timezone.now()
    ).order_by('start_date')
    
    ongoing_campaigns = CommunityCampaign.objects.filter(
        is_active=True,
        is_published=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).order_by('start_date')
    
    past_campaigns = CommunityCampaign.objects.filter(
        is_active=True,
        is_published=True,
        end_date__lt=timezone.now()
    ).order_by('-start_date')[:5]
    
    # Get user's participation status
    user_campaigns = CampaignParticipant.objects.filter(
        user=request.user
    ).values_list('campaign_id', flat=True)
    
    context = {
        'upcoming_campaigns': upcoming_campaigns,
        'ongoing_campaigns': ongoing_campaigns,
        'past_campaigns': past_campaigns,
        'user_campaigns': list(user_campaigns),
    }
    return render(request, 'community/campaigns_list.html', context)


@login_required
def campaign_detail(request, campaign_id):
    """View campaign details and participant list (FR08)"""
    from .models import CommunityCampaign, CampaignParticipant
    
    campaign = get_object_or_404(CommunityCampaign, id=campaign_id, is_active=True, is_published=True)
    
    # Check if user is registered
    user_participation = CampaignParticipant.objects.filter(
        campaign=campaign,
        user=request.user
    ).first()
    
    # Get recent participants (for display)
    recent_participants = CampaignParticipant.objects.filter(
        campaign=campaign
    ).select_related('user').order_by('-registered_at')[:10]
    
    # Get next occurrence if recurring
    next_campaign = None
    if campaign.recurrence != 'one_time' and campaign.next_occurrence:
        next_campaign = CommunityCampaign.objects.filter(
            title=campaign.title,
            start_date__gt=campaign.end_date,
            is_active=True,
            is_published=True
        ).first()
    
    context = {
        'campaign': campaign,
        'user_participation': user_participation,
        'recent_participants': recent_participants,
        'next_campaign': next_campaign,
    }
    return render(request, 'community/campaign_detail.html', context)


@login_required
def join_campaign(request, campaign_id):
    """Join a community campaign with one click (FR08)"""
    from .models import CommunityCampaign, CampaignParticipant
    
    if request.method == 'POST':
        campaign = get_object_or_404(CommunityCampaign, id=campaign_id, is_active=True, is_published=True)
        
        # Check if can register
        if not campaign.can_register:
            if campaign.is_full:
                messages.error(request, 'This campaign is full.')
            elif campaign.registration_deadline and timezone.now() > campaign.registration_deadline:
                messages.error(request, 'Registration deadline has passed.')
            elif campaign.is_past:
                messages.error(request, 'This campaign has already ended.')
            else:
                messages.error(request, 'Registration is not available for this campaign.')
            return redirect('community:campaign_detail', campaign_id=campaign.id)
        
        # Get interest level from form
        interest_level = request.POST.get('interest_level', 'join')
        
        participant, created = CampaignParticipant.objects.get_or_create(
            campaign=campaign,
            user=request.user,
            defaults={'interest_level': interest_level}
        )
        
        if created:
            # Update participant count
            campaign.participant_count += 1
            campaign.save(update_fields=['participant_count'])
            
            # Success message based on interest level
            if interest_level == 'join':
                messages.success(request, f'🎉 You have joined {campaign.title}!')
            elif interest_level == 'interested':
                messages.success(request, f'✅ You have registered interest in {campaign.title}!')
            else:
                messages.success(request, f'👍 You have marked {campaign.title} as "maybe"!')
            
            # Send confirmation (FR09)
            participant.send_confirmation()
            
        else:
            # Update existing participation
            if participant.interest_level != interest_level:
                participant.interest_level = interest_level
                participant.save(update_fields=['interest_level'])
                messages.info(request, f'Updated your participation status for {campaign.title}.')
            else:
                messages.info(request, 'You are already registered for this campaign.')
        
        return redirect('community:campaign_detail', campaign_id=campaign.id)
    
    return redirect('community:campaigns_list')


@login_required
def campaign_calendar(request):
    """Display campaign calendar (FR09)"""
    from .models import CommunityCampaign
    import json
    
    # Get all active campaigns for calendar
    campaigns = CommunityCampaign.objects.filter(
        is_active=True,
        is_published=True
    ).order_by('start_date')
    
    # Format for calendar
    calendar_events = []
    for campaign in campaigns:
        calendar_events.append({
            'id': campaign.id,
            'title': campaign.title,
            'start': campaign.start_date.isoformat(),
            'end': campaign.end_date.isoformat(),
            'url': campaign.get_absolute_url(),
            'description': campaign.description[:100] + '...' if len(campaign.description) > 100 else campaign.description,
            'location': campaign.location,
            'type': campaign.campaign_type,
            'participants': campaign.participant_count,
        })
    
    context = {
        'campaigns': campaigns,
        'calendar_events': json.dumps(calendar_events),
    }
    return render(request, 'community/campaign_calendar.html', context)


# ===================================================================
# COMMUNITY CHALLENGES
# ===================================================================

@login_required
def challenges_list(request):
    """Display active community challenges"""
    from .models import CommunityChallenge, ChallengeParticipant
    
    active_challenges = CommunityChallenge.objects.filter(
        is_active=True,
        end_date__gte=timezone.now()
    ).order_by('-start_date')
    
    # Get user's participation status
    user_challenges = ChallengeParticipant.objects.filter(
        user=request.user
    ).values_list('challenge_id', flat=True)
    
    context = {
        'challenges': active_challenges,
        'user_challenges': list(user_challenges),
    }
    return render(request, 'community/challenges_list.html', context)


@login_required
def challenge_detail(request, challenge_id):
    """View challenge details and leaderboard"""
    from .models import CommunityChallenge, ChallengeParticipant
    
    challenge = get_object_or_404(CommunityChallenge, id=challenge_id)
    
    # Get top 15 leaderboard
    leaderboard = ChallengeParticipant.objects.filter(
        challenge=challenge
    ).select_related('user').order_by('-contribution')[:15]
    
    # Check if user is participating
    user_participation = ChallengeParticipant.objects.filter(
        challenge=challenge,
        user=request.user
    ).first()
    
    # Get user's rank if participating
    user_rank = None
    if user_participation:
        user_rank = ChallengeParticipant.objects.filter(
            challenge=challenge,
            contribution__gt=user_participation.contribution
        ).count() + 1
    
    # Get user's proofs
    user_proofs = []
    if user_participation:
        from .models import ChallengeProof
        user_proofs = ChallengeProof.objects.filter(
            participant=user_participation
        ).order_by('-submitted_at')
    
    context = {
        'challenge': challenge,
        'leaderboard': leaderboard,
        'user_participation': user_participation,
        'user_rank': user_rank,
        'user_proofs': user_proofs,
    }
    return render(request, 'community/challenge_detail.html', context)


@login_required
def join_challenge(request, challenge_id):
    """Join a community challenge"""
    from .models import CommunityChallenge, ChallengeParticipant
    from .notifications import notification_service
    
    if request.method == 'POST':
        challenge = get_object_or_404(CommunityChallenge, id=challenge_id, is_active=True)
        
        participant, created = ChallengeParticipant.objects.get_or_create(
            challenge=challenge,
            user=request.user
        )
        
        if created:
            messages.success(request, f'🎉 You have joined the {challenge.title}!')
            
            # REAL-TIME NOTIFICATION: Send WhatsApp/SMS instantly if enabled
            try:
                prefs = getattr(request.user, 'notification_preferences', None)
                user_name = request.user.get_full_name() or request.user.username
                
                # SMS notification - PRO ZNBC style
                if prefs and prefs.sms_enabled and prefs.challenge_updates and request.user.phone_number:
                    sms_message = f"🎉 {user_name}, welcome to {challenge.title}! Top 3 win airtime. Submit proof now!"
                    result = notification_service.send_sms(str(request.user.phone_number), sms_message)
                    if result.get('success'):
                        print(f"✅ SMS sent to {request.user.username}")
                
                # WhatsApp notification - PRO Zambian style
                if prefs and prefs.whatsapp_enabled and prefs.challenge_updates and request.user.phone_number:
                    whatsapp_message = f"🎉 {user_name}, welcome to {challenge.title}! Top 3 win airtime. Submit proof now!"
                    result = notification_service.send_whatsapp(str(request.user.phone_number), whatsapp_message)
                    if result.get('success'):
                        print(f"✅ WhatsApp sent to {request.user.username}")
                
                # In-app notification
                Notification.objects.create(
                    user=request.user,
                    notification_type='challenge_update',
                    title=f'Joined {challenge.title}!',
                    message=f'You have successfully joined {challenge.title}. Start collecting bags and climb the leaderboard!',
                    url=challenge.get_absolute_url()
                )
            except Exception as e:
                print(f"Notification error: {e}")
        else:
            messages.info(request, 'You are already participating in this challenge.')
        
        return redirect('community:challenge_detail', challenge_id=challenge.id)
    
    return redirect('community:challenges_list')


@login_required
def submit_challenge_proof(request, challenge_id):
    """Submit proof for challenge participation"""
    from .models import CommunityChallenge, ChallengeParticipant, ChallengeProof
    
    challenge = get_object_or_404(CommunityChallenge, id=challenge_id, is_active=True)
    participant = get_object_or_404(ChallengeParticipant, challenge=challenge, user=request.user)
    
    if request.method == 'POST':
        before_photo = request.FILES.get('before_photo')
        after_photo = request.FILES.get('after_photo')
        bags_collected = request.POST.get('bags_collected', 0)
        description = request.POST.get('description', '')
        
        if not before_photo:
            messages.error(request, 'Before photo is required!')
            return redirect('community:challenge_detail', challenge_id=challenge.id)
        
        try:
            bags_collected = int(bags_collected)
            if bags_collected < 1:
                raise ValueError
        except:
            messages.error(request, 'Please enter a valid number of bags collected.')
            return redirect('community:challenge_detail', challenge_id=challenge.id)
        
        # Create proof submission
        proof = ChallengeProof.objects.create(
            participant=participant,
            before_photo=before_photo,
            after_photo=after_photo,
            bags_collected=bags_collected,
            description=description
        )
        
        messages.success(request, '✅ Proof submitted successfully! Awaiting admin approval.')
        return redirect('community:challenge_detail', challenge_id=challenge.id)
    
    return redirect('community:challenge_detail', challenge_id=challenge.id)


# ===================================================================
# SOCIAL MEDIA INTEGRATION
# ===================================================================

@login_required
def share_to_social(request):
    """Generate share links for social media"""
    if request.method == 'POST':
        content_type = request.POST.get('content_type')
        content_id = request.POST.get('content_id')
        platform = request.POST.get('platform')
        
        # Build share URL
        base_url = request.build_absolute_uri('/')
        share_text = "Check out this amazing eco-initiative on EcoLearn Zambia!"
        
        if content_type == 'story':
            from .models import SuccessStory
            story = get_object_or_404(SuccessStory, id=content_id)
            share_text = f"🌍 {story.title} - {story.content[:100]}..."
            content_url = request.build_absolute_uri(
                reverse('community:story_detail', args=[content_id])
            )
        elif content_type == 'event':
            from .models import CommunityEvent
            event = get_object_or_404(CommunityEvent, id=content_id)
            share_text = f"📅 Join us: {event.title} on {event.start_date.strftime('%B %d, %Y')}"
            content_url = request.build_absolute_uri(
                reverse('community:event_detail', args=[content_id])
            )
        else:
            content_url = base_url
        
        # Generate platform-specific URLs
        share_urls = {
            'whatsapp': f"https://wa.me/?text={share_text}%20{content_url}",
            'facebook': f"https://www.facebook.com/sharer/sharer.php?u={content_url}",
            'twitter': f"https://twitter.com/intent/tweet?text={share_text}&url={content_url}",
        }
        
        # Record the share
        SocialMediaShare.objects.create(
            user=request.user,
            platform=platform,
            content_type=content_type,
            content_id=content_id
        )
        
        return JsonResponse({
            'success': True,
            'share_url': share_urls.get(platform, content_url)
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


# ===================================================================
# PERSONAL IMPACT DASHBOARD
# ===================================================================

@login_required
def personal_impact(request):
    """Display user's personal impact dashboard"""
    from .models import ChallengeParticipant, EventParticipant, SuccessStory
    from reporting.models import Report
    from elearning.models import UserProgress, Certificate
    
    # Learning metrics
    modules_completed = UserProgress.objects.filter(
        user=request.user,
        completion_percentage=100
    ).count()
    
    certificates_earned = Certificate.objects.filter(user=request.user).count()
    
    # Community engagement
    reports_filed = Report.objects.filter(reporter=request.user).count()
    events_attended = EventParticipant.objects.filter(
        user=request.user,
        attended=True
    ).count()
    
    challenges_joined = ChallengeParticipant.objects.filter(
        user=request.user
    ).count()
    
    stories_shared = SuccessStory.objects.filter(
        author=request.user,
        is_approved=True
    ).count()
    
    # Calculate total impact score
    impact_score = (
        modules_completed * 10 +
        certificates_earned * 50 +
        reports_filed * 20 +
        events_attended * 30 +
        challenges_joined * 15 +
        stories_shared * 25
    )
    
    context = {
        'modules_completed': modules_completed,
        'certificates_earned': certificates_earned,
        'reports_filed': reports_filed,
        'events_attended': events_attended,
        'challenges_joined': challenges_joined,
        'stories_shared': stories_shared,
        'impact_score': impact_score,
    }
    return render(request, 'community/personal_impact.html', context)



@login_required
def track_share(request):
    """Track social media shares for analytics"""
    if request.method == 'POST':
        import json
        from django.contrib.contenttypes.models import ContentType
        
        try:
            data = json.loads(request.body)
            content_type_str = data.get('content_type')
            object_id = data.get('object_id')
            platform = data.get('platform')
            
            # Get content type
            if content_type_str == 'story':
                content_type = ContentType.objects.get_for_model(SuccessStory)
            elif content_type_str == 'event':
                content_type = ContentType.objects.get_for_model(CommunityEvent)
            elif content_type_str == 'challenge':
                content_type = ContentType.objects.get_for_model(CommunityChallenge)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid content type'})
            
            # Create share record
            SocialShare.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=object_id,
                platform=platform
            )
            
            return JsonResponse({'success': True})
        
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
