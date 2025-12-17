# accounts/urls.py
# Oscar Milambo — EcoLearn Zambia — FINAL VERSION
# November 17, 2025 — National Launch Ready — ZERO ERRORS

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
# ===================================================================
# 1. CORE PAGES & AUTHENTICATION
# ===================================================================
path('', views.landing_page_view, name='landing'),                    # Home page
path('login/', views.login_view, name='login'),                       # ← YOUR CUSTOM FUNCTION-BASED LOGIN
path('logout/', views.logout_view, name='logout'),                    # ← YOUR CUSTOM LOGOUT
path('dashboard/', views.dashboard_view, name='dashboard'),          # ← YOUR REAL DASHBOARD

# ===================================================================
# 2. REGISTRATION & VERIFICATION
# ===================================================================
path('register/', views.register_view, name='register'),
# Phone verification only - users are activated immediately

# ===================================================================
# 3. USER PROFILE & LANGUAGE
# ===================================================================
path('profile/', views.profile_view, name='profile'),
path('language/<str:lang_code>/', views.set_language, name='set_language'),
# OR keep old style if you prefer:
# path('language/set/', views.set_language, name='set_user_language'),

# ===================================================================
# 4. PASSWORD RESET (Phone-based SMS Reset)
# ===================================================================
path('password-reset/', views.password_reset_request, name='password_reset_request'),
path('password-reset/verify/', views.password_reset_verify, name='password_reset_verify'),

# ===================================================================
# 5. SESSION SECURITY (AJAX — All views exist in your views.py)
# ===================================================================
path('session/keep-alive/', views.session_keep_alive, name='session_keep_alive'),
path('session/status/', views.session_status, name='session_status'),
path('session/extend/', views.session_extend, name='session_extend'),
path('session/logout/', views.secure_logout, name='secure_logout'),

# Debug only (remove in production)
# path('session/info/', views.session_info, name='session_info'),

# ===================================================================
# 6. ADMIN & ROLE MANAGEMENT
# ===================================================================
path('roles/', views.role_management_view, name='role_management'),
path('switch-dashboard/', views.switch_dashboard_view, name='switch_dashboard'),

# ===================================================================
# 7. NOTIFICATION PREFERENCES & API
# ===================================================================
path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),
path('notifications/test/', views.test_notification, name='test_notification'),
path('api/notifications/count/', views.notification_count_api, name='notification_count_api'),
]