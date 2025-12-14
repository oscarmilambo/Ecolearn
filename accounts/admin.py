from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserProfile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'preferred_language', 'is_verified', 'date_joined')
    list_filter = ('preferred_language', 'is_verified', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # Override fieldsets to exclude non-editable fields
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Additional Info', {
            'fields': ('phone_number', 'preferred_language', 'profile_picture', 'date_of_birth', 'location', 'is_verified')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('email', 'phone_number', 'preferred_language')
        }),
    )
    
    # Explicitly exclude non-editable fields
    readonly_fields = ('date_joined', 'last_login')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'certificates_earned', 'modules_completed')
    list_filter = ('certificates_earned', 'modules_completed')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('points', 'certificates_earned', 'modules_completed')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
