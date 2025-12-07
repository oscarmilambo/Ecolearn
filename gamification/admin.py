from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import (
    PointTransaction, UserPoints, Challenge, ChallengeParticipant,
    Reward, RewardRedemption, CommunityImpact
)


# Import-Export Resources
class ChallengeResource(resources.ModelResource):
    class Meta:
        model = Challenge
        fields = ('id', 'title', 'challenge_type', 'points_reward', 'start_date', 'end_date', 'target_metric', 'target_value', 'is_active')
        export_order = fields


class RewardResource(resources.ModelResource):
    class Meta:
        model = Reward
        fields = ('id', 'name', 'reward_type', 'points_cost', 'stock_quantity', 'is_available')
        export_order = fields


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'available_points', 'redeemed_points', 'rank', 'updated_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['updated_at']
    ordering = ['-total_points']


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'points', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'description']
    date_hierarchy = 'created_at'


@admin.register(Challenge)
class ChallengeAdmin(ImportExportModelAdmin):
    resource_class = ChallengeResource
    list_display = ['title', 'challenge_type', 'points_reward', 'start_date', 'end_date', 'is_active']
    list_filter = ['challenge_type', 'is_active', 'start_date']
    search_fields = ['title', 'description']


@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'challenge', 'progress', 'is_completed', 'joined_at']
    list_filter = ['is_completed', 'joined_at']
    search_fields = ['user__username', 'challenge__title']


@admin.register(Reward)
class RewardAdmin(ImportExportModelAdmin):
    resource_class = RewardResource
    list_display = ['name', 'reward_type', 'points_cost', 'stock_quantity', 'is_available']
    list_filter = ['reward_type', 'is_available']
    search_fields = ['name', 'description']


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward', 'points_spent', 'status', 'redemption_code', 'redeemed_at']
    list_filter = ['status', 'redeemed_at']
    search_fields = ['user__username', 'redemption_code', 'reward__name']
    date_hierarchy = 'redeemed_at'


@admin.register(CommunityImpact)
class CommunityImpactAdmin(admin.ModelAdmin):
    list_display = ['community_name', 'district', 'total_reports', 'resolved_reports', 'tons_collected', 'active_members']
    search_fields = ['community_name', 'district']
    list_filter = ['district']
