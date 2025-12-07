from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserPoints, PointTransaction, Challenge, ChallengeParticipant,
    Reward, RewardRedemption, CommunityImpact
)
from collaboration.models import Leaderboard, Badge, UserBadge


@login_required
def points_dashboard(request):
    """User's points and rewards dashboard"""
    user_points, created = UserPoints.objects.get_or_create(user=request.user)
    
    recent_transactions = PointTransaction.objects.filter(
        user=request.user
    )[:10]
    
    # Get available rewards
    available_rewards = Reward.objects.filter(
        is_available=True,
        points_cost__lte=user_points.available_points
    )
    
    # Get user's redemptions
    redemptions = RewardRedemption.objects.filter(user=request.user)[:5]
    
    context = {
        'user_points': user_points,
        'recent_transactions': recent_transactions,
        'available_rewards': available_rewards,
        'redemptions': redemptions,
    }
    return render(request, 'gamification/points_dashboard.html', context)


@login_required
def leaderboard_view(request):
    """Display leaderboards"""
    leaderboard_type = request.GET.get('type', 'individual')
    period = request.GET.get('period', 'monthly')
    
    if leaderboard_type == 'individual':
        # Individual leaderboard
        top_users = UserPoints.objects.select_related('user').order_by('-total_points')[:50]
        
        # Get user's rank
        user_points = UserPoints.objects.get_or_create(user=request.user)[0]
        user_rank = UserPoints.objects.filter(total_points__gt=user_points.total_points).count() + 1
        
        context = {
            'leaderboard_type': leaderboard_type,
            'period': period,
            'top_users': top_users,
            'user_rank': user_rank,
            'user_points': user_points,
        }
    
    elif leaderboard_type == 'community':
        # Community leaderboard
        communities = CommunityImpact.objects.order_by('-total_points')[:50]
        
        context = {
            'leaderboard_type': leaderboard_type,
            'period': period,
            'communities': communities,
        }
    
    else:
        # District leaderboard
        districts = CommunityImpact.objects.values('district').annotate(
            total_points=Sum('total_points'),
            total_reports=Sum('total_reports'),
            tons_collected=Sum('tons_collected')
        ).order_by('-total_points')[:20]
        
        context = {
            'leaderboard_type': leaderboard_type,
            'period': period,
            'districts': districts,
        }
    
    return render(request, 'gamification/leaderboard.html', context)


@login_required
def challenges_view(request):
    """Display active challenges"""
    active_challenges = Challenge.objects.filter(
        is_active=True,
        end_date__gte=timezone.now()
    ).order_by('-start_date')
    
    # Get user's participations
    user_participations = ChallengeParticipant.objects.filter(
        user=request.user
    ).values_list('challenge_id', flat=True)
    
    context = {
        'challenges': active_challenges,
        'user_participations': list(user_participations),
    }
    return render(request, 'gamification/challenges.html', context)


@login_required
def join_challenge(request, challenge_id):
    """Join a challenge"""
    if request.method == 'POST':
        challenge = get_object_or_404(Challenge, id=challenge_id, is_active=True)
        
        participant, created = ChallengeParticipant.objects.get_or_create(
            challenge=challenge,
            user=request.user
        )
        
        if created:
            messages.success(request, f'You have joined the challenge: {challenge.title}!')
        else:
            messages.info(request, 'You are already participating in this challenge.')
        
        return redirect('gamification:challenges')
    
    return redirect('gamification:challenges')


@login_required
def rewards_catalog(request):
    """Display available rewards"""
    rewards = Reward.objects.filter(is_available=True).order_by('points_cost')
    
    user_points = UserPoints.objects.get_or_create(user=request.user)[0]
    
    context = {
        'rewards': rewards,
        'user_points': user_points,
    }
    return render(request, 'gamification/rewards_catalog.html', context)


@login_required
def redeem_reward(request, reward_id):
    """Redeem a reward"""
    if request.method == 'POST':
        reward = get_object_or_404(Reward, id=reward_id, is_available=True)
        user_points = UserPoints.objects.get_or_create(user=request.user)[0]
        
        if user_points.available_points >= reward.points_cost:
            # Check stock
            if reward.stock_quantity > 0 or reward.reward_type in ['certificate', 'badge']:
                # Create redemption
                contact_info = request.POST.get('contact_info', request.user.phone_number or request.user.email)
                
                redemption = RewardRedemption.objects.create(
                    user=request.user,
                    reward=reward,
                    points_spent=reward.points_cost,
                    contact_info=contact_info
                )
                
                # Deduct points
                user_points.redeem_points(reward.points_cost, f'Redeemed: {reward.name}')
                
                # Update stock
                if reward.stock_quantity > 0:
                    reward.stock_quantity -= 1
                    reward.save()
                
                messages.success(request, f'Successfully redeemed {reward.name}! Your redemption code is: {redemption.redemption_code}')
            else:
                messages.error(request, 'This reward is out of stock.')
        else:
            messages.error(request, 'You do not have enough points to redeem this reward.')
        
        return redirect('gamification:rewards_catalog')
    
    return redirect('gamification:rewards_catalog')


@login_required
def badges_view(request):
    """Display user's badges"""
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge')
    available_badges = Badge.objects.filter(is_active=True).exclude(
        id__in=user_badges.values_list('badge_id', flat=True)
    )
    
    context = {
        'user_badges': user_badges,
        'available_badges': available_badges,
    }
    return render(request, 'gamification/badges.html', context)


@login_required
def community_impact_view(request):
    """Display community impact metrics"""
    # Get user's community
    user_community = request.user.profile.community if hasattr(request.user, 'profile') else None
    
    if user_community:
        community_impact = CommunityImpact.objects.filter(
            community_name=user_community
        ).first()
    else:
        community_impact = None
    
    # Get top communities
    top_communities = CommunityImpact.objects.order_by('-total_points')[:10]
    
    context = {
        'community_impact': community_impact,
        'top_communities': top_communities,
    }
    return render(request, 'gamification/community_impact.html', context)


# Helper function to award points
def award_points(user, transaction_type, points, description, reference_id=None):
    """Award points to a user"""
    user_points, created = UserPoints.objects.get_or_create(user=user)
    user_points.add_points(points, transaction_type, description, reference_id)
    
    # Check for badge eligibility
    check_badge_eligibility(user)
    
    return user_points


def check_badge_eligibility(user):
    """Check if user is eligible for any badges"""
    user_points = UserPoints.objects.get_or_create(user=user)[0]
    
    # Get badges user doesn't have
    earned_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
    available_badges = Badge.objects.filter(
        is_active=True,
        points_required__lte=user_points.total_points
    ).exclude(id__in=earned_badge_ids)
    
    # Award new badges
    for badge in available_badges:
        UserBadge.objects.create(user=user, badge=badge)
        # Could send notification here
