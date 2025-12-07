# elearning/urls.py

from django.urls import path
from . import views

app_name = 'elearning'

urlpatterns = [
    # Module URLs
    path('', views.module_list, name='module_list'),
    path('module/<slug:slug>/', views.module_detail, name='module_detail'),
    path('module/<slug:slug>/enroll/', views.enroll_module, name='enroll_module'),
    
    # Lesson URLs
    path('module/<slug:module_slug>/lesson/<slug:lesson_slug>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/complete/', views.complete_lesson, name='complete_lesson'),
    
    # Quiz URLs
    path('quiz/<int:quiz_id>/take/', views.quiz_take, name='quiz_take'),
    path('quiz/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    
    # Review URLs
    path('module/<slug:module_slug>/review/', views.submit_review, name='submit_review'),
    path('module/<slug:module_slug>/review/edit/', views.edit_review, name='edit_review'),
    
    # App URLs (Category, Tag, Dashboard, Learning Path, Leaderboard, Certificate)
    # The prefix 'app/' is added to these paths
    path('app/category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('app/tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    
    path('app/dashboard/', views.progress_dashboard, name='progress_dashboard'),
    path('app/learning-path/', views.learning_path, name='learning_path'),
    path('app/leaderboard/', views.leaderboard, name='leaderboard'),
    
    path('app/certificates/', views.certificates_view, name='certificates'),
    path('app/certificate/<str:certificate_id>/download/', views.download_certificate, name='download_certificate'),
    path('app/certificate/<str:certificate_id>/verify/', views.verify_certificate, name='verify_certificate'),
    
    # Removed path('i18n/setlang/', set_language, name='set_language') to avoid duplicate name conflict
]