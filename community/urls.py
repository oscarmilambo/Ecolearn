# community/urls.py
from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    # ====================== FORUM ======================
    path('forum/', views.forum_home, name='forum_home'),
    path('forum/category/<int:category_id>/', views.category_topics, name='category_topics'),
    path('forum/category/<int:category_id>/create/', views.create_topic, name='create_topic'),
    path('forum/topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),

    # ====================== EVENTS ======================
    path('events/', views.events_list, name='events_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', views.register_event, name='register_event'),

    # ====================== SUCCESS STORIES ======================
    path('stories/', views.success_stories, name='success_stories'),
    path('stories/create/', views.create_story, name='create_story'),
    path('stories/<int:story_id>/', views.story_detail, name='story_detail'),
    path('stories/<int:story_id>/like/', views.like_story, name='like_story'),

    # ====================== CHALLENGES ======================
    path('challenges/', views.challenges_list, name='challenges_list'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:challenge_id>/join/', views.join_challenge, name='join_challenge'),
    path('challenges/<int:challenge_id>/submit-proof/', views.submit_challenge_proof, name='submit_challenge_proof'),

    # ====================== HEALTH ALERTS ======================
    path('health-alerts/', views.health_alerts, name='health_alerts'),
    path('health-alerts/<int:alert_id>/', views.alert_detail, name='alert_detail'),

    # ====================== USER DASHBOARD ======================
    path('my-impact/', views.personal_impact, name='personal_impact'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/count/', views.notification_count, name='notification_count'),

    # ====================== SOCIAL SHARING ======================
    path('share/', views.share_to_social, name='share_to_social'),
    path('share/track/', views.track_share, name='track_share'),
]