from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type_notif', 'channel', 'is_read', 'created_at')
    list_filter = ('type_notif', 'channel', 'is_read')
    search_fields = ('title', 'message', 'user__username', 'user__email')
    list_editable = ('is_read',)
    list_select_related = ('user',)
    date_hierarchy = 'created_at'
    
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_read']
    
    @admin.action(description='Marquer comme lu')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)