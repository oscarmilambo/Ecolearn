from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import (
    PaymentProvider, PaymentPlan, Payment, Subscription,
    PaymentWebhook, PaymentStatistics
)

@admin.register(PaymentProvider)
class PaymentProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'is_active', 'test_mode')
    list_filter = ('is_active', 'test_mode')
    search_fields = ('name', 'display_name')
    
    fieldsets = (
        ('Provider Information', {
            'fields': ('name', 'display_name', 'is_active', 'test_mode')
        }),
        ('API Configuration', {
            'fields': ('api_endpoint', 'api_key', 'api_secret'),
            'classes': ('collapse',)
        })
    )


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'price', 'currency', 'duration_days', 'is_active')
    list_filter = ('plan_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('plan_type', 'price')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'plan', 'amount', 'currency', 'status', 'provider', 'created_at')
    list_filter = ('status', 'provider', 'currency', 'created_at')
    search_fields = ('payment_id', 'transaction_id', 'user__username', 'plan__name')
    readonly_fields = ('payment_id', 'created_at', 'updated_at', 'completed_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'transaction_id', 'user', 'plan')
        }),
        ('Amount & Provider', {
            'fields': ('amount', 'currency', 'provider', 'phone_number', 'payment_method')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'failure_reason', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
        ('Provider Data', {
            'fields': ('provider_response', 'metadata'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='completed', completed_at=timezone.now())
        self.message_user(request, f"{queryset.count()} payments marked as completed.")
    mark_as_completed.short_description = "Mark selected payments as completed"
    
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"{queryset.count()} payments marked as failed.")
    mark_as_failed.short_description = "Mark selected payments as failed"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active', 'auto_renew')
    list_filter = ('is_active', 'auto_renew', 'plan__plan_type', 'start_date')
    search_fields = ('user__username', 'plan__name')
    readonly_fields = ('created_at',)
    ordering = ('-start_date',)
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscriptions activated.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscriptions deactivated.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = ('provider', 'payment', 'processed', 'created_at')
    list_filter = ('provider', 'processed', 'created_at')
    search_fields = ('provider', 'payment__payment_id')
    readonly_fields = ('created_at', 'webhook_data')
    ordering = ('-created_at',)


@admin.register(PaymentStatistics)
class PaymentStatisticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_payments', 'successful_payments', 'failed_payments', 'total_amount')
    list_filter = ('date',)
    readonly_fields = ('date', 'total_payments', 'successful_payments', 'failed_payments', 'total_amount', 'mtn_payments', 'airtel_payments', 'zamtel_payments')
    ordering = ('-date',)
