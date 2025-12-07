from django.contrib import admin
from .models import ChatSession, ChatMessage, AssistantFeedback


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content', 'session__user__username')
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'


@admin.register(AssistantFeedback)
class AssistantFeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'message_preview', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'comment')
    readonly_fields = ('created_at',)
    
    def message_preview(self, obj):
        return obj.message.content[:50]
    message_preview.short_description = 'Message'
