# ecolearn/urls.py (Main URL Configuration)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import views from accounts.views (since you don't have ecolearn/views.py)
from accounts.views import (
    landing_page_view,
    dashboard_view,
    set_language,
    about,
    features,
    contact,
)

urlpatterns = [
    # Language switcher - MUST be before 'accounts/' to avoid conflicts
    path('set-language/<str:lang_code>/', set_language, name='set_language'),

    # Core apps
    path('admin/', admin.site.urls),
    
    
    # Landing page (home) - shows landing page for unauthenticated, redirects to dashboard for authenticated
    path('', landing_page_view, name='home'),
    
    # Dashboard - for authenticated users only
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Static/Info Pages - accessible to everyone
    path('about/', about, name='about'),
    path('features/', features, name='features'),
    path('contact/', contact, name='contact'),
    
    # App URLs
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('elearning/', include('elearning.urls')),
    path('community/', include('community.urls')),
    path('reporting/', include('reporting.urls')),
    path('payments/', include('payments.urls')),
    path('admin-dashboard/', include('admin_dashboard.urls')),
    path('ai-assistant/', include('ai_assistant.urls')),  # AI Assistant

    # 🌟 NEW: Gamification App 
    path('rewards/', include('gamification.urls', namespace='gamification')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)