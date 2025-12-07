from django.contrib import admin
from django.utils.html import format_html
from .models import DumpingReport, ReportUpdate, Authority, ReportStatistics

@admin.register(DumpingReport)
class DumpingReportAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'get_reporter_info', 'location_description', 'severity', 'status', 'reported_at')
    list_filter = ('status', 'severity', 'is_anonymous', 'forwarded_to_authority', 'reported_at')
    search_fields = ('reference_number', 'location_description', 'description', 'reporter_contact', 'reporter__username')
    readonly_fields = ('reference_number', 'reported_at')
    ordering = ('-reported_at',)
    
    def get_reporter_info(self, obj):
        if obj.is_anonymous:
            return format_html('<span style="color: #6b7280;">Anonymous</span>')
        return obj.reporter.username if obj.reporter else 'Unknown'
    get_reporter_info.short_description = 'Reporter'
    
    actions = ['mark_verified', 'mark_in_progress', 'mark_resolved', 'forward_to_authority']
    
    def mark_verified(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='verified', verified_at=timezone.now())
        self.message_user(request, f'{updated} reports marked as verified.')
    mark_verified.short_description = 'Mark as verified'
    
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} reports marked as in progress.')
    mark_in_progress.short_description = 'Mark as in progress'
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} reports marked as resolved.')
    mark_resolved.short_description = 'Mark as resolved'
    
    def forward_to_authority(self, request, queryset):
        count = 0
        for report in queryset:
            if not report.forwarded_to_authority:
                report.forwarded_to_authority = True
                report.save()
                count += 1
        self.message_user(request, f"{count} reports forwarded to authorities.")
    forward_to_authority.short_description = "Forward to authorities"
    
    fieldsets = (
        ('Report Information', {
            'fields': ('reference_number', 'reporter', 'is_anonymous', 'reporter_contact')
        }),
        ('Location', {
            'fields': ('location_description', 'latitude', 'longitude', 'address')
        }),
        ('Details', {
            'fields': ('description', 'severity', 'waste_type', 'estimated_volume')
        }),
        ('Photos', {
            'fields': ('photo1', 'photo2', 'photo3')
        }),
        ('Status', {
            'fields': ('status', 'forwarded_to_authority', 'authority_name', 'authority_contact')
        }),
        ('Timestamps', {
            'fields': ('reported_at', 'verified_at', 'resolved_at')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes', 'authority_response')
        })
    )


@admin.register(ReportUpdate)
class ReportUpdateAdmin(admin.ModelAdmin):
    list_display = ('report', 'updated_by', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'report__status')
    search_fields = ('report__reference_number', 'update_text', 'updated_by__username')
    readonly_fields = ('created_at',)


@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'contact_phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'contact_email', 'coverage_areas')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_email', 'contact_phone', 'coverage_areas', 'is_active')
        }),
        ('API Integration', {
            'fields': ('api_endpoint', 'api_key'),
            'classes': ('collapse',)
        })
    )


@admin.register(ReportStatistics)
class ReportStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_reports', 'pending_reports', 'resolved_reports', 'average_resolution_days')
    list_filter = ('date',)
    readonly_fields = ('date', 'total_reports', 'pending_reports', 'resolved_reports', 'average_resolution_days')
    ordering = ('-date',)
