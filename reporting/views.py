from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import DumpingReport, ReportUpdate, Authority, ReportStatistics
from .forms import DumpingReportForm, ReportUpdateForm
import requests
import json


@login_required
def report_dumping(request):
    if request.method == 'POST':
        form = DumpingReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            
            # Set reporter if user is authenticated and not anonymous
            if request.user.is_authenticated and not form.cleaned_data.get('is_anonymous'):
                report.reporter = request.user
            
            report.save()
            
            # Forward to appropriate authority
            forward_to_authority(report)
            
            # REAL-TIME NOTIFICATION: Notify ALL admins instantly via WhatsApp/SMS
            try:
                from accounts.models import CustomUser
                from community.notifications import notification_service
                from community.models import Notification
                from django.utils import timezone
                
                # Get all superusers/admins
                admins = CustomUser.objects.filter(Q(is_superuser=True) | Q(is_staff=True))
                
                # Count today's reports
                today_reports = DumpingReport.objects.filter(
                    reported_at__date=timezone.now().date()
                ).count()
                
                for admin in admins:
                    try:
                        prefs = getattr(admin, 'notification_preferences', None)
                        
                        photo_count = sum([1 for p in [report.photo1, report.photo2, report.photo3] if p])
                        
                        # SMS notification - PRO ZNBC style
                        if admin.phone_number and (not prefs or prefs.sms_enabled):
                            sms_message = f"🚨 NEW ILLEGAL DUMP in {report.location_description}! {photo_count} photos attached. Act now!"
                            result = notification_service.send_sms(str(admin.phone_number), sms_message)
                            if result.get('success'):
                                print(f"✅ Admin SMS sent to {admin.username}")
                        
                        # WhatsApp notification - PRO admin alert
                        if admin.phone_number and (not prefs or prefs.whatsapp_enabled):
                            whatsapp_message = f"🚨 NEW ILLEGAL DUMP in {report.location_description}! {photo_count} photos attached. Act now!"
                            result = notification_service.send_whatsapp(str(admin.phone_number), whatsapp_message)
                            if result.get('success'):
                                print(f"✅ Admin WhatsApp sent to {admin.username}")
                        
                        # In-app notification
                        Notification.objects.create(
                            user=admin,
                            notification_type='emergency',
                            title=f'New Report: {report.location_description}',
                            message=f'New illegal dumping report ({report.get_severity_display()} severity). {today_reports} reports today. Ref: {report.reference_number}',
                            url=f'/admin-dashboard/reports/{report.id}/'
                        )
                    except Exception as e:
                        print(f"Error notifying admin {admin.username}: {e}")
            except Exception as e:
                print(f"Error in admin notifications: {e}")
            
            messages.success(
                request, 
                f'Report submitted successfully! Your reference number is: {report.reference_number}'
            )
            return redirect('reporting:report_success', reference_number=report.reference_number)
    else:
        form = DumpingReportForm()
    
    context = {
        'form': form,
    }
    return render(request, 'reporting/report_dumping.html', context)


def report_success(request, reference_number):
    report = get_object_or_404(DumpingReport, reference_number=reference_number)
    context = {
        'report': report,
    }
    return render(request, 'reporting/report_success.html', context)


@login_required
def track_report(request):
    reference_number = request.GET.get('reference_number')
    report = None
    
    if reference_number:
        try:
            report = DumpingReport.objects.get(reference_number=reference_number.upper())
        except DumpingReport.DoesNotExist:
            messages.error(request, 'Report not found. Please check your reference number.')
    
    context = {
        'report': report,
        'reference_number': reference_number,
    }
    return render(request, 'reporting/track_report.html', context)


@login_required
def reports_map(request):
    # Get all verified reports for map display
    reports = DumpingReport.objects.filter(
        status__in=['verified', 'in_progress', 'resolved']
    ).values(
        'id', 'latitude', 'longitude', 'location_description', 
        'severity', 'status', 'reference_number'
    )
    
    context = {
        'reports': list(reports),
    }
    return render(request, 'reporting/reports_map.html', context)


@login_required
def my_reports(request):
    if request.user.is_staff:
        # Staff can see all reports
        reports = DumpingReport.objects.all()
    else:
        # Regular users see only their reports
        reports = DumpingReport.objects.filter(reporter=request.user)
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': DumpingReport.STATUS_CHOICES,
        'current_status': status_filter,
    }
    return render(request, 'reporting/my_reports.html', context)


def report_detail(request, report_id):
    report = get_object_or_404(DumpingReport, id=report_id)
    
    # Check permissions
    can_view = (
        request.user.is_staff or 
        (request.user.is_authenticated and report.reporter == request.user) or
        report.status in ['verified', 'resolved']  # Public reports
    )
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('reporting:reports_map')
    
    updates = report.updates.filter(is_public=True).order_by('-created_at')
    
    context = {
        'report': report,
        'updates': updates,
    }
    return render(request, 'reporting/report_detail.html', context)


@login_required
def update_report(request, report_id):
    if not request.user.is_staff:
        messages.error(request, 'Permission denied.')
        return redirect('reporting:reports_map')
    
    report = get_object_or_404(DumpingReport, id=report_id)
    
    if request.method == 'POST':
        form = ReportUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.report = report
            update.updated_by = request.user
            update.save()
            
            # Update report status if provided
            new_status = request.POST.get('new_status')
            if new_status and new_status in dict(DumpingReport.STATUS_CHOICES):
                report.status = new_status
                if new_status == 'resolved':
                    from django.utils import timezone
                    report.resolved_at = timezone.now()
                report.save()
            
            messages.success(request, 'Report updated successfully!')
            return redirect('reporting:report_detail', report_id=report.id)
    else:
        form = ReportUpdateForm()
    
    context = {
        'form': form,
        'report': report,
        'status_choices': DumpingReport.STATUS_CHOICES,
    }
    return render(request, 'reporting/update_report.html', context)


def statistics_view(request):
    # Get recent statistics
    recent_stats = ReportStatistics.objects.all()[:30]  # Last 30 days
    
    # Get summary data
    total_reports = DumpingReport.objects.count()
    pending_reports = DumpingReport.objects.filter(status='pending').count()
    resolved_reports = DumpingReport.objects.filter(status='resolved').count()
    
    # Reports by severity
    severity_stats = DumpingReport.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('severity')
    
    # Reports by status
    status_stats = DumpingReport.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    context = {
        'recent_stats': recent_stats,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'resolved_reports': resolved_reports,
        'severity_stats': severity_stats,
        'status_stats': status_stats,
    }
    return render(request, 'reporting/statistics.html', context)


def forward_to_authority(report):
    """Forward report to appropriate local authority"""
    try:
        # Find appropriate authority based on location
        # This is a simplified version - in production, you'd use more sophisticated location matching
        authority = Authority.objects.filter(is_active=True).first()
        
        if authority:
            report.authority_name = authority.name
            report.authority_contact = authority.contact_email
            
            # Send email notification
            subject = f'New Illegal Dumping Report - {report.reference_number}'
            message = f"""
            New illegal dumping report received:
            
            Reference Number: {report.reference_number}
            Location: {report.location_description}
            Coordinates: {report.latitude}, {report.longitude}
            Severity: {report.get_severity_display()}
            Description: {report.description}
            
            Please log into the EcoLearn system to view full details and photos.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [authority.contact_email],
                fail_silently=True,
            )
            
            # If authority has API endpoint, send via API
            if authority.api_endpoint:
                send_via_api(report, authority)
            
            report.forwarded_to_authority = True
            report.save()
            
    except Exception as e:
        print(f"Error forwarding report to authority: {e}")


def send_via_api(report, authority):
    """Send report data to authority's API endpoint"""
    try:
        data = {
            'reference_number': report.reference_number,
            'location': report.location_description,
            'latitude': float(report.latitude),
            'longitude': float(report.longitude),
            'description': report.description,
            'severity': report.severity,
            'reported_at': report.reported_at.isoformat(),
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {authority.api_key}' if authority.api_key else None
        }
        
        response = requests.post(
            authority.api_endpoint,
            data=json.dumps(data),
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            report.admin_notes += f"\nSuccessfully forwarded to {authority.name} API"
        else:
            report.admin_notes += f"\nFailed to forward to {authority.name} API: {response.status_code}"
            
    except Exception as e:
        report.admin_notes += f"\nAPI forwarding error: {str(e)}"

# reports/views.py (Add this new function)

