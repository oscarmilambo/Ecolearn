from django.contrib import admin
from .models import (
    CleanupGroup, GroupMembership, GroupEvent, GroupChat,
    GroupImpactReport, Badge, UserBadge, Leaderboard
)


@admin.register(CleanupGroup)
class CleanupGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'community', 'district', 'coordinator', 'member_count_display', 'is_active', 'created_at')
    list_filter = ('district', 'is_active', 'created_at')
    search_fields = ('name', 'community', 'district', 'coordinator__username')
    readonly_fields = ('created_at',)
    
    def member_count_display(self, obj):
        return obj.member_count
    member_count_display.short_description = 'Members'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'is_active', 'joined_at')
    list_filter = ('role', 'is_active', 'joined_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)


@admin.register(GroupEvent)
class GroupEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'location', 'scheduled_date', 'status', 'participants_count', 'waste_collected')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('title', 'group__name', 'location')
    readonly_fields = ('created_at',)
    ordering = ('-scheduled_date',)


@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'group', 'message_preview', 'is_announcement', 'created_at')
    list_filter = ('is_announcement', 'created_at')
    search_fields = ('sender__username', 'group__name', 'message')
    readonly_fields = ('created_at',)
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'


@admin.register(GroupImpactReport)
class GroupImpactReportAdmin(admin.ModelAdmin):
    list_display = ('group', 'report_period_start', 'report_period_end', 'total_events', 'waste_collected_kg', 'generated_at')
    list_filter = ('generated_at',)
    search_fields = ('group__name',)
    readonly_fields = ('generated_at',)


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon', 'points_required', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at',)


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('badge__category', 'earned_at')
    search_fields = ('user__username', 'badge__name')
    readonly_fields = ('earned_at',)


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('leaderboard_type', 'period_type', 'period_start', 'period_end', 'generated_at')
    list_filter = ('leaderboard_type', 'period_type', 'generated_at')
    readonly_fields = ('generated_at',)
