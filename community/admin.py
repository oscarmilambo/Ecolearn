# community/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.auth import get_user_model
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import (
    ForumCategory, ForumTopic, ForumReply,
    CommunityEvent, EventParticipant,
    SuccessStory, SocialMediaShare,
    Notification, HealthAlert,
    CommunityChallenge, ChallengeParticipant, ChallengeProof
)

User = get_user_model()


# Import-Export Resources
class CommunityEventResource(resources.ModelResource):
    class Meta:
        model = CommunityEvent
        fields = ('id', 'title', 'event_type', 'location', 'start_date', 'end_date', 'max_participants', 'is_active')
        export_order = fields


class SuccessStoryResource(resources.ModelResource):
    class Meta:
        model = SuccessStory
        fields = ('id', 'title', 'author__username', 'story_type', 'location', 'is_featured', 'is_approved', 'created_at')
        export_order = fields


class HealthAlertResource(resources.ModelResource):
    class Meta:
        model = HealthAlert
        fields = ('id', 'alert_type', 'severity', 'title', 'location', 'is_active', 'created_at')
        export_order = fields


@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_bem', 'name_ny', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'name_bem', 'name_ny')
    list_editable = ('order', 'is_active')
    ordering = ('order',)


@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_pinned', 'views', 'reply_count', 'created_at')
    list_filter = ('category', 'is_pinned', 'is_locked', 'created_at')
    search_fields = ('title', 'content', 'author__username', 'author__first_name')
    readonly_fields = ('views', 'created_at')  # REMOVED 'updated_at' – it doesn't exist!
    ordering = ('-is_pinned', '-created_at')

    def reply_count(self, obj):
        return obj.reply_count
    reply_count.short_description = "Replies"


@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ('topic_link', 'author', 'short_content', 'is_solution', 'created_at')
    list_filter = ('is_solution', 'created_at', 'topic__category')
    search_fields = ('content', 'author__username', 'topic__title')
    readonly_fields = ('created_at',)  # REMOVED 'updated_at' – it doesn't exist!

    def topic_link(self, obj):
        url = obj.topic.get_absolute_url()
        return format_html('<a href="{}">{}</a>', url, obj.topic.title)
    topic_link.short_description = "Topic"

    def short_content(self, obj):
        return obj.content[:80] + "..." if len(obj.content) > 80 else obj.content
    short_content.short_description = "Reply Preview"


@admin.register(CommunityEvent)
class CommunityEventAdmin(ImportExportModelAdmin):
    resource_class = CommunityEventResource
    list_display = ('title', 'event_type', 'location', 'start_date', 'participant_count', 'is_active')
    list_filter = ('event_type', 'is_active', 'start_date')
    search_fields = ('title', 'location', 'organizer__username')
    readonly_fields = ('created_at',)
    ordering = ('-start_date',)

    def participant_count(self, obj):
        return obj.participant_count
    participant_count.short_description = "Participants"


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registered_at', 'attended')
    list_filter = ('attended', 'registered_at')
    search_fields = ('user__username', 'event__title')
    readonly_fields = ('registered_at',)


@admin.register(SuccessStory)
class SuccessStoryAdmin(ImportExportModelAdmin):
    resource_class = SuccessStoryResource
    list_display = ('title', 'author', 'story_type', 'is_approved', 'is_featured', 'like_count', 'created_at')
    list_filter = ('story_type', 'is_approved', 'is_featured', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('created_at',)
    list_editable = ('is_approved', 'is_featured')
    actions = ['approve_stories', 'feature_stories']

    def approve_stories(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} stories approved.")
    approve_stories.short_description = "Approve selected stories"

    def feature_stories(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count} stories featured.")
    feature_stories.short_description = "Feature on homepage"


@admin.register(SocialMediaShare)
class SocialMediaShareAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'content_type', 'content_id', 'shared_at')
    list_filter = ('platform', 'shared_at')
    search_fields = ('user__username',)
    readonly_fields = ('shared_at',)
    date_hierarchy = 'shared_at'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at',)
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f"{count} notifications marked as read.")
    mark_as_read.short_description = "Mark as read"


@admin.register(HealthAlert)
class HealthAlertAdmin(ImportExportModelAdmin):
    resource_class = HealthAlertResource
    list_display = ('title', 'alert_type', 'severity_display', 'location', 'is_active', 'created_at')
    list_filter = ('severity', 'alert_type', 'is_active', 'created_at')
    search_fields = ('title', 'location', 'affected_areas')
    readonly_fields = ('created_at', 'created_by')
    ordering = ('-created_at',)

    fieldsets = (
        ('Alert Details', {'fields': ('alert_type', 'severity', 'title', 'message')}),
        ('Location', {'fields': ('location', 'latitude', 'longitude', 'affected_areas')}),
        ('Health Guidance', {'fields': ('hygiene_tips', 'nearest_clinics')}),
        ('Status', {'fields': ('is_active', 'expires_at', 'created_by', 'created_at')}),
    )

    def severity_display(self, obj):
        colors = {'critical': 'red', 'high': 'orange', 'medium': 'yellow', 'low': 'green'}
        color = colors.get(obj.severity, 'gray')
        return format_html('<span style="color:white; background:{}; padding:2px 8px; border-radius:4px;">{}</span>',
                           color, obj.get_severity_display().upper())
    severity_display.short_description = "Severity"


@admin.register(CommunityChallenge)
class CommunityChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge_type', 'progress_bar', 'target_goal', 'current_progress', 'is_active')
    list_filter = ('challenge_type', 'is_active', 'start_date')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-start_date',)

    def progress_bar(self, obj):
        percentage = obj.progress_percentage
        color = "bg-green-500" if percentage >= 80 else "bg-yellow-500" if percentage >= 50 else "bg-red-500"
        return format_html(
            '<div class="w-32 bg-gray-200 rounded-full h-6 overflow-hidden">'
            '<div class="h-full {} text-white text-center text-xs leading-6" style="width: {}%">'
            '{}%</div></div>',
            color, percentage, int(percentage)
        )
    progress_bar.short_description = "Progress"


@admin.register(ChallengeParticipant)
class ChallengeParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'contribution_display', 'points_earned_display', 'joined_at')
    list_filter = ('challenge__challenge_type', 'joined_at')
    search_fields = ('user__username', 'challenge__title')
    readonly_fields = ('joined_at',)
    ordering = ('-contribution',)
    
    def contribution_display(self, obj):
        return f'{obj.contribution} bags'
    contribution_display.short_description = 'Bags Collected'
    
    def points_earned_display(self, obj):
        points = obj.contribution * 30
        return format_html('<strong style="color: green;">{} pts</strong>', points)
    points_earned_display.short_description = 'Points Earned'


@admin.register(ChallengeProof)
class ChallengeProofAdmin(admin.ModelAdmin):
    list_display = ('participant_user', 'challenge_title', 'bags_collected', 'status_badge', 'points_awarded', 'submitted_at')
    list_filter = ('status', 'submitted_at', 'participant__challenge')
    search_fields = ('participant__user__username', 'participant__challenge__title', 'description')
    readonly_fields = ('submitted_at', 'points_awarded', 'reviewed_at', 'reviewed_by')
    ordering = ('-submitted_at',)
    
    fieldsets = (
        ('Submission Details', {
            'fields': ('participant', 'bags_collected', 'description')
        }),
        ('Photos', {
            'fields': ('before_photo', 'after_photo')
        }),
        ('Review Status', {
            'fields': ('status', 'points_awarded', 'submitted_at', 'reviewed_at', 'reviewed_by', 'admin_notes')
        }),
    )
    
    actions = ['approve_proofs', 'reject_proofs']
    
    def participant_user(self, obj):
        return obj.participant.user.get_full_name() or obj.participant.user.username
    participant_user.short_description = 'User'
    
    def challenge_title(self, obj):
        return obj.participant.challenge.title
    challenge_title.short_description = 'Challenge'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color:white; background:{}; padding:4px 12px; border-radius:12px; font-weight:bold;">{}</span>',
            color, obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    
    def approve_proofs(self, request, queryset):
        count = 0
        for proof in queryset.filter(status='pending'):
            proof.approve(request.user)
            count += 1
        self.message_user(request, f"✅ {count} proof(s) approved and points awarded!")
    approve_proofs.short_description = "✅ Approve selected proofs (auto-award 30 pts/bag)"
    
    def reject_proofs(self, request, queryset):
        count = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_by=request.user,
            reviewed_at=timezone.now()
        )
        self.message_user(request, f"❌ {count} proof(s) rejected.")
    reject_proofs.short_description = "❌ Reject selected proofs"