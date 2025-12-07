from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    # Points & Rewards
    path('points/', views.points_dashboard, name='points_dashboard'),
    path('rewards/', views.rewards_catalog, name='rewards_catalog'),
    path('rewards/<int:reward_id>/redeem/', views.redeem_reward, name='redeem_reward'),
    
    # Leaderboard
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
    
    # Challenges
    path('challenges/', views.challenges_view, name='challenges'),
    path('challenges/<int:challenge_id>/join/', views.join_challenge, name='join_challenge'),
    
    # Badges
    path('badges/', views.badges_view, name='badges'),
    
    # Community Impact
    path('community-impact/', views.community_impact_view, name='community_impact'),
]
