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
    CommunityCampaign, CampaignParticipant,
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


class CommunityCampaignResource(resources.ModelResource):
    class Meta:
        model = CommunityCampaign
        fields = ('id', 'title', 'campaign_type', 'location', 'start_date', 'end_date', 'recurrence', 'participant_count', 'is_active', 'is_published')
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


@admin.register(CommunityCampaign)
class CommunityCampaignAdmin(ImportExportModelAdmin):
    resource_class = CommunityCampaignResource
    list_display = ('title', 'campaign_type', 'location', 'start_date', 'recurrence_display', 'participant_count', 'status_display', 'is_published')
    list_filter = ('campaign_type', 'recurrence', 'is_active', 'is_published', 'start_date')
    search_fields = ('title', 'location', 'organizer__username')
    readonly_fields = ('participant_count', 'created_at', 'updated_at', 'next_occurrence')
    ordering = ('-start_date',)
    
    fieldsets = (
        ('Campaign Details', {
            'fields': ('title', 'title_bem', 'title_ny', 'description', 'description_bem', 'description_ny', 'campaign_type')
        }),
        ('Schedule & Location', {
            'fields': ('start_date', 'end_date', 'location', 'latitude', 'longitude')
        }),
        ('Recurrence Settings', {
            'fields': ('recurrence', 'next_occurrence'),
            'description': 'For recurring campaigns, the system will automatically create new instances.'
        }),
        ('Registration', {
            'fields': ('max_participants', 'registration_deadline')
        }),
        ('Organizer Details', {
            'fields': ('organizer', 'contact_phone', 'contact_email')
        }),
        ('Media & Status', {
            'fields': ('image', 'is_active', 'is_published')
        }),
        ('Statistics', {
            'fields': ('participant_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_campaigns', 'unpublish_campaigns', 'create_recurring_campaigns']
    
    def recurrence_display(self, obj):
        if obj.recurrence == 'one_time':
            return '🔄 One-time'
        else:
            return f'🔄 {obj.get_recurrence_display()}'
    recurrence_display.short_description = 'Recurrence'
    
    def status_display(self, obj):
        now = timezone.now()
        if obj.is_past:
            return format_html('<span style="color:gray;">📅 Past</span>')
        elif obj.is_ongoing:
            return format_html('<span style="color:green;">🟢 Ongoing</span>')
        elif obj.is_upcoming:
            return format_html('<span style="color:blue;">🔵 Upcoming</span>')
        else:
            return format_html('<span style="color:orange;">⏳ Scheduled</span>')
    status_display.short_description = 'Status'
    
    def publish_campaigns(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"✅ {count} campaign(s) published and visible to users!")
    publish_campaigns.short_description = "✅ Publish selected campaigns"
    
    def unpublish_campaigns(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"❌ {count} campaign(s) unpublished.")
    unpublish_campaigns.short_description = "❌ Unpublish selected campaigns"
    
    def create_recurring_campaigns(self, request, queryset):
        count = 0
        for campaign in queryset.filter(recurrence__in=['monthly', 'quarterly', 'yearly']):
            if campaign.create_next_occurrence():
                count += 1
        self.message_user(request, f"🔄 {count} recurring campaign(s) created!")
    create_recurring_campaigns.short_description = "🔄 Create next occurrence for recurring campaigns"


@admin.register(CampaignParticipant)
class CampaignParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'campaign', 'interest_level_display', 'registered_at', 'attended', 'reminder_status')
    list_filter = ('interest_level', 'attended', 'registered_at', 'campaign__campaign_type')
    search_fields = ('user__username', 'campaign__title')
    readonly_fields = ('registered_at', 'reminder_3days_sent', 'reminder_1day_sent', 'confirmation_sent')
    ordering = ('-registered_at',)
    
    actions = ['send_reminders', 'mark_attended']
    
    def interest_level_display(self, obj):
        colors = {
            'join': 'green',
            'interested': 'blue',
            'maybe': 'orange'
        }
        color = colors.get(obj.interest_level, 'gray')
        icons = {
            'join': '✅',
            'interested': '👍',
            'maybe': '🤔'
        }
        icon = icons.get(obj.interest_level, '❓')
        return format_html(
            '<span style="color:{};">{} {}</span>',
            color, icon, obj.get_interest_level_display()
        )
    interest_level_display.short_description = 'Interest Level'
    
    def reminder_status(self, obj):
        status = []
        if obj.confirmation_sent:
            status.append('✅ Confirmed')
        if obj.reminder_3days_sent:
            status.append('📅 3-day')
        if obj.reminder_1day_sent:
            status.append('⏰ 1-day')
        return ' | '.join(status) if status else '❌ No reminders'
    reminder_status.short_description = 'Reminders Sent'
    
    def send_reminders(self, request, queryset):
        count = 0
        for participant in queryset:
            days_until = (participant.campaign.start_date - timezone.now()).days
            if days_until == 3 and not participant.reminder_3days_sent:
                participant.send_reminder(3)
                count += 1
            elif days_until == 1 and not participant.reminder_1day_sent:
                participant.send_reminder(1)
                count += 1
        self.message_user(request, f"📱 {count} reminder(s) sent!")
    send_reminders.short_description = "📱 Send campaign reminders"
    
    def mark_attended(self, request, queryset):
        count = queryset.update(attended=True, attendance_confirmed_at=timezone.now())
        self.message_user(request, f"✅ {count} participant(s) marked as attended!")
    mark_attended.short_description = "✅ Mark as attended"


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