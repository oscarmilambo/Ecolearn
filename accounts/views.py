# accounts/views.py
# Oscar Milambo — EcoLearn Zambia — FINAL VERSION
# November 17, 2025 — National Launch Ready

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.translation import activate
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum

from .forms import CustomUserCreationForm, UserProfileForm, SMSVerificationForm
from .models import CustomUser, UserProfile
from elearning.models import Module


# ===================================================================
# 1. PUBLIC PAGES
# ===================================================================
def landing_page_view(request):
    """Home page — redirects logged-in users to dashboard"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'accounts/landing_page.html')

def about(request):
    return render(request, 'pages/about.html')

def features(request):
    return render(request, 'pages/features.html')

def contact(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you can add logic to save to database or send email
        # For now, just show success message
        messages.success(request, f'Thank you {name}! We received your message and will get back to you soon.')
        return redirect('contact')  # Fixed: was 'accounts:contact', now just 'contact'
    return render(request, 'pages/contact.html')


# ===================================================================
# 2. AUTHENTICATION VIEWS (FUNCTION-BASED — CLEAN & SECURE)
# ===================================================================
def login_view(request):
    """Custom login view with flexible username support"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username_input = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try multiple authentication methods to support both old and new usernames
        user = None
        
        # Method 1: Direct username match (for both old and new formats)
        user = authenticate(request, username=username_input, password=password)
        
        # Method 2: If direct match fails, try to find user by email
        if user is None and '@' in username_input:
            try:
                user_obj = CustomUser.objects.get(email=username_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        # Method 3: If still no match, try to find by full name parts
        if user is None and ' ' in username_input:
            try:
                # Split the input and try to find by first and last name
                parts = username_input.strip().split()
                if len(parts) >= 2:
                    first_name = parts[0]
                    last_name = ' '.join(parts[1:])  # Handle multiple last names
                    
                    # Try to find user by first and last name
                    user_obj = CustomUser.objects.get(
                        first_name__iexact=first_name, 
                        last_name__iexact=last_name
                    )
                    user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        # Method 4: Try old-style usernames (for legacy users like oscarmilambo2)
        if user is None:
            # Check if there's a user with this exact username (case-insensitive)
            try:
                user_obj = CustomUser.objects.get(username__iexact=username_input)
                user = authenticate(request, username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            next_url = request.GET.get('next')
            return redirect(next_url or 'dashboard')
        else:
            messages.error(request, 'Invalid username or password. Try your full name, email, or original username.')
    
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """Secure logout with message"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')  # Back to beautiful landing page


# Registration success view removed - users go directly to login after registration


# Phone verification only - users are activated immediately upon registration


# ===================================================================
# PASSWORD RESET VIEWS
# ===================================================================

def password_reset_request(request):
    """Request password reset via phone number"""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        
        if not phone_number:
            messages.error(request, 'Please enter your phone number.')
            return render(request, 'accounts/password_reset_request.html')
        
        # Find user by phone number
        try:
            user = CustomUser.objects.get(phone_number=phone_number, is_active=True)
        except CustomUser.DoesNotExist:
            messages.error(request, 'No active account found with this phone number.')
            return render(request, 'accounts/password_reset_request.html')
        
        # Create reset code
        from .models import PasswordResetCode
        
        # Deactivate any existing codes for this user
        PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new reset code
        reset_code = PasswordResetCode.objects.create(
            user=user,
            phone_number=phone_number
        )
        
        # Send SMS (if Twilio is configured)
        try:
            from community.notifications import notification_service
            sms_message = f"Your EcoLearn password reset code is: {reset_code.code}. Valid for 10 minutes."
            result = notification_service.send_sms(phone_number, sms_message)
            
            if result.get('success'):
                messages.success(request, f'Reset code sent to {phone_number}. Check your SMS.')
            else:
                messages.warning(request, f'Reset code generated: {reset_code.code} (SMS service unavailable)')
        except Exception as e:
            messages.warning(request, f'Reset code generated: {reset_code.code} (SMS service unavailable)')
        
        # Redirect to verification page
        request.session['reset_phone'] = phone_number
        return redirect('accounts:password_reset_verify')
    
    return render(request, 'accounts/password_reset_request.html')


def password_reset_verify(request):
    """Verify reset code and set new password"""
    phone_number = request.session.get('reset_phone')
    
    if not phone_number:
        messages.error(request, 'Session expired. Please start the password reset process again.')
        return redirect('accounts:password_reset_request')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not all([code, new_password, confirm_password]):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'accounts/password_reset_verify.html', {'phone_number': phone_number})
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/password_reset_verify.html', {'phone_number': phone_number})
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'accounts/password_reset_verify.html', {'phone_number': phone_number})
        
        # Find and verify reset code
        from .models import PasswordResetCode
        
        try:
            reset_code = PasswordResetCode.objects.get(
                phone_number=phone_number,
                code=code,
                is_used=False
            )
            
            if reset_code.is_expired():
                messages.error(request, 'Reset code has expired. Please request a new one.')
                return redirect('accounts:password_reset_request')
            
            # Reset password
            user = reset_code.user
            user.set_password(new_password)
            user.save()
            
            # Mark code as used
            reset_code.is_used = True
            reset_code.save()
            
            # Clear session
            if 'reset_phone' in request.session:
                del request.session['reset_phone']
            
            messages.success(request, 'Password reset successful! You can now log in with your new password.')
            return redirect('accounts:login')
            
        except PasswordResetCode.DoesNotExist:
            messages.error(request, 'Invalid reset code.')
            return render(request, 'accounts/password_reset_verify.html', {'phone_number': phone_number})
    
    return render(request, 'accounts/password_reset_verify.html', {'phone_number': phone_number})


def register_view(request):
    """Enhanced registration with phone number only and rate limiting"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Rate limiting: Check registration attempts
    if request.method == 'POST':
        # Simple rate limiting using session
        attempts_key = 'registration_attempts'
        attempts_time_key = 'registration_attempts_time'
        
        current_time = timezone.now()
        attempts = request.session.get(attempts_key, 0)
        last_attempt_time = request.session.get(attempts_time_key)
        
        # Reset counter if more than 1 hour has passed
        if last_attempt_time:
            from datetime import datetime
            last_time = datetime.fromisoformat(last_attempt_time)
            if (current_time - last_time).total_seconds() > 3600:  # 1 hour
                attempts = 0
        
        # Check if rate limit exceeded
        if attempts >= 5:
            messages.error(request, 'Too many registration attempts. Please try again in 1 hour.')
            return render(request, 'accounts/register.html', {'form': CustomUserCreationForm()})
        
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Increment attempts
            request.session[attempts_key] = attempts + 1
            request.session[attempts_time_key] = current_time.isoformat()
            
            # Create user manually with contact method (phone or email)
            contact_method = form.cleaned_data['contact_method']
            email = form.cleaned_data['email']
            
            # Determine if contact_method is phone or email
            if '@' in contact_method:
                # Contact method is email, use it as primary email
                phone_number = None
                user_email = contact_method
            else:
                # Contact method is phone number
                phone_number = contact_method
                user_email = email
            
            # Use full name exactly as entered (what user expects)
            first_name = form.cleaned_data['first_name'].strip()
            last_name = form.cleaned_data['last_name'].strip()
            
            # Create username from full name exactly as entered (e.g., "Edward Jere")
            base_username = f"{first_name} {last_name}"
            
            # Ensure unique username
            counter = 1
            username = base_username
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username} {counter}"
                counter += 1
            
            # Create user
            user = CustomUser.objects.create_user(
                username=username,
                email=user_email,
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                gender=form.cleaned_data['gender'],
                phone_number=phone_number,
                is_active=True  # User is active immediately
            )
            
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            
            # User is now active immediately upon registration
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('accounts:login')
        else:
            # Increment attempts even on form errors
            request.session[attempts_key] = attempts + 1
            request.session[attempts_time_key] = current_time.isoformat()
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def verify_view(request):
    """Phone verification placeholder"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
        
    if request.method == 'POST':
        form = SMSVerificationForm(request.POST)
        if form.is_valid():
            request.user.profile.phone_verified = True
            request.user.profile.save()
            messages.success(request, 'Phone number verified!')
            return redirect('accounts:dashboard')
    else:
        form = SMSVerificationForm()
    
    return render(request, 'accounts/verify.html', {'form': form})


# ===================================================================
# 3. USER PROFILE & DASHBOARD
# ===================================================================
@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def dashboard_view(request):
    """
    Unified User Dashboard - Shows everything from all apps
    Updated November 18, 2025
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # ==================== ELEARNING ====================
    enrolled_modules = Module.objects.filter(enrollment__user=user).distinct()
    
    try:
        from elearning.models import UserProgress, Certificate
        
        modules_completed = UserProgress.objects.filter(
            user=user,
            completion_percentage=100
        ).count()
        
        modules_in_progress = UserProgress.objects.filter(
            user=user,
            completion_percentage__gt=0,
            completion_percentage__lt=100
        ).count()
        
        certificates_earned = Certificate.objects.filter(user=user).count()
    except Exception as e:
        modules_completed = 0
        modules_in_progress = 0
        certificates_earned = 0
    
    # ==================== COMMUNITY APP ====================
    try:
        from community.models import (
            EventParticipant, ChallengeParticipant, SuccessStory,
            ForumTopic, ForumReply, Notification
        )
        
        # Upcoming events
        upcoming_events = EventParticipant.objects.filter(
            user=user,
            event__start_date__gte=timezone.now(),
            event__is_active=True
        ).select_related('event').order_by('event__start_date')[:3]
        
        # Active challenges
        active_challenges = ChallengeParticipant.objects.filter(
            user=user,
            challenge__is_active=True,
            challenge__end_date__gte=timezone.now()
        ).select_related('challenge')[:3]
        
        # Forum activity
        forum_topics_count = ForumTopic.objects.filter(author=user).count()
        forum_replies_count = ForumReply.objects.filter(author=user).count()
        
        # Success stories
        approved_stories = SuccessStory.objects.filter(author=user, is_approved=True).count()
        pending_stories = SuccessStory.objects.filter(author=user, is_approved=False).count()
        
        # Notifications
        unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
        recent_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
        
        # Events attended
        events_attended = EventParticipant.objects.filter(user=user, attended=True).count()
        
    except Exception as e:
        upcoming_events = []
        active_challenges = []
        forum_topics_count = 0
        forum_replies_count = 0
        approved_stories = 0
        pending_stories = 0
        unread_notifications = 0
        recent_notifications = []
        events_attended = 0
    
    # ==================== REPORTING APP ====================
    try:
        from reporting.models import Report
        
        total_reports = Report.objects.filter(reporter=user).count()
        pending_reports = Report.objects.filter(reporter=user, status='pending').count()
        resolved_reports = Report.objects.filter(reporter=user, status='resolved').count()
        recent_reports = Report.objects.filter(reporter=user).order_by('-created_at')[:3]
        
    except Exception as e:
        total_reports = 0
        pending_reports = 0
        resolved_reports = 0
        recent_reports = []
    
    # ==================== CAMPAIGNS APP (if exists) ====================
    try:
        from campaigns.models import CampaignParticipant, Campaign
        
        upcoming_campaigns = CampaignParticipant.objects.filter(
            user=user,
            campaign__start_date__gte=timezone.now(),
            status='registered'
        ).select_related('campaign')[:3]
        
        campaigns_participated = CampaignParticipant.objects.filter(
            user=user,
            status__in=['attended', 'completed']
        ).count()
        
        waste_collected = CampaignParticipant.objects.filter(user=user).aggregate(
            total=Sum('waste_collected_kg')
        )['total'] or 0
        
        hours_volunteered = CampaignParticipant.objects.filter(user=user).aggregate(
            total=Sum('hours_contributed')
        )['total'] or 0
        
        available_campaigns = Campaign.objects.filter(
            status='scheduled',
            start_date__gte=timezone.now()
        ).exclude(participants__user=user)[:3]
        
    except Exception as e:
        upcoming_campaigns = []
        campaigns_participated = 0
        waste_collected = 0
        hours_volunteered = 0
        available_campaigns = []
    
    # ==================== PAYMENTS APP ====================
    try:
        from payments.models import Payment
        
        active_subscription = Payment.objects.filter(
            user=user,
            status='completed',
            plan__isnull=False
        ).order_by('-payment_date').first()
        
        total_paid = Payment.objects.filter(
            user=user,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
    except Exception as e:
        active_subscription = None
        total_paid = 0
    
    # ==================== CALCULATE IMPACT SCORE ====================
    impact_score = (
        modules_completed * 10 +
        certificates_earned * 50 +
        total_reports * 20 +
        events_attended * 30 +
        len(list(active_challenges)) * 15 +
        approved_stories * 25 +
        campaigns_participated * 40 +
        int(waste_collected * 2) +
        forum_topics_count * 5 +
        forum_replies_count * 2
    )
    
    # ==================== ACHIEVEMENTS ====================
    achievements = []
    
    if modules_completed >= 5:
        achievements.append({
            'icon': 'fa-graduation-cap',
            'title': 'Learning Champion',
            'description': f'Completed {modules_completed} modules',
            'color': 'blue'
        })
    
    if certificates_earned >= 3:
        achievements.append({
            'icon': 'fa-certificate',
            'title': 'Certified Expert',
            'description': f'Earned {certificates_earned} certificates',
            'color': 'yellow'
        })
    
    if total_reports >= 10:
        achievements.append({
            'icon': 'fa-flag',
            'title': 'Community Guardian',
            'description': f'Reported {total_reports} issues',
            'color': 'red'
        })
    
    if waste_collected >= 50:
        achievements.append({
            'icon': 'fa-recycle',
            'title': 'Waste Warrior',
            'description': f'Collected {waste_collected:.1f}kg of waste',
            'color': 'green'
        })
    
    if campaigns_participated >= 5:
        achievements.append({
            'icon': 'fa-users',
            'title': 'Campaign Hero',
            'description': f'Participated in {campaigns_participated} campaigns',
            'color': 'purple'
        })
    
    # ==================== CONTEXT ====================
    context = {
        # Profile & Basic
        'profile': profile,
        'user': user,
        
        # Learning
        'enrolled_modules': enrolled_modules,
        'total_modules': enrolled_modules.count(),
        'modules_completed': modules_completed,
        'modules_in_progress': modules_in_progress,
        'certificates_earned': certificates_earned,
        
        # Community
        'upcoming_events': upcoming_events,
        'active_challenges': active_challenges,
        'forum_topics_count': forum_topics_count,
        'forum_replies_count': forum_replies_count,
        'approved_stories': approved_stories,
        'pending_stories': pending_stories,
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
        'events_attended': events_attended,
        
        # Campaigns
        'upcoming_campaigns': upcoming_campaigns,
        'campaigns_participated': campaigns_participated,
        'waste_collected': waste_collected,
        'hours_volunteered': hours_volunteered,
        'available_campaigns': available_campaigns,
        
        # Reporting
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'resolved_reports': resolved_reports,
        'recent_reports': recent_reports,
        
        # Payments
        'active_subscription': active_subscription,
        'total_paid': total_paid,
        
        # Overall
        'impact_score': impact_score,
        'achievements': achievements,
    }
    
    # CORRECT PATH: templates/dashboard/user_dashboard.html
    return render(request, 'dashboard/user_dashboard.html', context)


# ===================================================================
# 4. LANGUAGE SWITCHER
# ===================================================================
def set_language(request, lang_code=None):
    """Switch user language preference"""
    if lang_code is None:
        lang_code = request.GET.get('lang')
    
    # Validate language code
    valid_languages = [lang[0] for lang in settings.LANGUAGES]
    
    if lang_code and lang_code in valid_languages:
        # Activate language for current request
        activate(lang_code)
        
        # Get redirect URL
        next_url = request.GET.get('next') or request.META.get('HTTP_REFERER', '/')
        response = HttpResponseRedirect(next_url)
        
        # Set language cookie
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang_code,
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path='/',
            samesite='Lax'
        )
        
        # Save to user profile if authenticated
        if request.user.is_authenticated:
            request.user.preferred_language = lang_code
            request.user.save(update_fields=['preferred_language'])
        
        # Store in session as well
        request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
        
        lang_names = {'en': 'English', 'bem': 'Chibemba', 'ny': 'Chinyanja'}
        messages.success(request, f'Language changed to {lang_names.get(lang_code, lang_code)}')
    else:
        response = redirect('accounts:landing')
        messages.error(request, 'Invalid language selection')
    
    return response


# ===================================================================
# 5. SESSION SECURITY (AJAX ENDPOINTS)
# ===================================================================
@login_required
def session_keep_alive(request):
    request.session.modified = True
    return JsonResponse({'status': 'alive'})

@login_required
def session_status(request):
    return JsonResponse({
        'authenticated': True,
        'username': request.user.username,
        'full_name': request.user.get_full_name(),
    })

@login_required
def session_extend(request):
    request.session.set_expiry(3600 * 2)  # 2 hours
    return JsonResponse({'status': 'extended'})

@login_required
def secure_logout(request):
    logout(request)
    return JsonResponse({'status': 'logged_out'})


# ===================================================================
# 6. ADMIN & ROLE MANAGEMENT
# ===================================================================
@login_required
def role_management_view(request):
    if not request.user.is_staff:
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard')
    
    users = CustomUser.objects.all().select_related('profile')
    return render(request, 'accounts/role_management.html', {'users': users})


@login_required
def switch_dashboard_view(request):
    if not request.user.is_staff:
        messages.error(request, "Permission denied.")
        return redirect('accounts:dashboard')
    
    if request.session.get('admin_mode'):
        request.session.pop('admin_mode')
        messages.success(request, "Switched to User Dashboard")
    else:
        request.session['admin_mode'] = True
        messages.success(request, "Switched to Admin Dashboard")
    
    return redirect('accounts:dashboard')


# ===================================================================
# NOTIFICATION PREFERENCES
# ===================================================================
@login_required
def notification_preferences(request):
    """Manage notification preferences"""
    from accounts.models import NotificationPreference
    
    # Get or create preferences
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        # Update preferences
        preferences.sms_enabled = request.POST.get('sms_enabled') == 'on'
        preferences.whatsapp_enabled = request.POST.get('whatsapp_enabled') == 'on'
        preferences.email_enabled = request.POST.get('email_enabled') == 'on'
        
        preferences.event_reminders = request.POST.get('event_reminders') == 'on'
        preferences.challenge_updates = request.POST.get('challenge_updates') == 'on'
        preferences.forum_replies = request.POST.get('forum_replies') == 'on'
        preferences.reward_updates = request.POST.get('reward_updates') == 'on'
        preferences.community_news = request.POST.get('community_news') == 'on'
        
        preferences.frequency = request.POST.get('frequency', 'instant')
        
        preferences.save()
        
        messages.success(request, 'Notification preferences updated successfully!')
        return redirect('accounts:notification_preferences')
    
    context = {
        'preferences': preferences
    }
    return render(request, 'accounts/notification_preferences.html', context)


@login_required
def test_notification(request):
    """Send a test notification"""
    if request.method == 'POST':
        try:
            from community.notifications import notification_service
            
            data = {
                'message': 'This is a test notification from EcoLearn! Your notifications are working correctly. 🎉'
            }
            
            results = notification_service.notify_user(
                request.user,
                'test',
                data,
                channels=['email']  # Start with email only for testing
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Test notification sent!',
                'results': results
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def notification_count_api(request):
    """API endpoint to get unread notification count"""
    try:
        from community.models import Notification
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'unread_count': 0
        })