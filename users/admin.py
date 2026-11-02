from django.contrib import admin
from users.models import CustomUser

# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_blocked', 'is_email_verified', 'is_active', 'date_joined')
    list_filter = ('is_blocked', 'is_email_verified', 'is_active')
    search_fields = ('username', 'email')

    actions = ['block_users', 'unblock_users']

    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)
    block_users.short_description = "Заблокировать рассылку (для выбранных)"

    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)
    unblock_users.short_description = "Разрешить рассылку (для выбранных)"