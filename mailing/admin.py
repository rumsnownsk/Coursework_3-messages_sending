from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from mailing.models import Recipient, Message

from .models import Mailing, MailingAttempt
from .services import send_mailing


# Register your models here.

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name_link', 'email', 'comment')
    search_fields = ('email', 'full_name')

    def full_name_link(self, obj):
        url = reverse('admin:mailing_recipient_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>',
                          url,
                          f"#{obj.id} {obj.full_name}")

    full_name_link.short_description = 'Ф. И. О.'



@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject',)
    search_fields = ('subject', 'body')


class MailingAttemptInline(admin.TabularInline):
    model = MailingAttempt
    extra = 0
    readonly_fields = ('attempt_time', 'status', 'server_response')



def action_send_mailing(modeladmin, request, queryset):
    success_count = 0
    error_count = 0

    for mailing in queryset:
        success, _ = send_mailing(mailing)
        if success:
            success_count += 1
        else:
            error_count += 1

    if success_count:
        modeladmin.message_user(request, f"{success_count} рассылок успешно отправлено.", level='success')
    if error_count:
        modeladmin.message_user(request, f"В {error_count} рассылках были ошибки.", level='error')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_link', 'status', 'formatted_start', 'formatted_end')
    # list_display = ('subject', 'created_at', 'status')
    list_filter = ('status',)
    inlines = [MailingAttemptInline]
    actions = [action_send_mailing]

    def name_link(self, obj):
        url = reverse('admin:mailing_mailing_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)
    name_link.short_description = "Название рассылки"

    def formatted_start(self, obj):
        return obj.start_time.strftime('%d.%m.%Y %H:%M')
    formatted_start.short_description = 'Дата и время первой отправки'

    def formatted_end(self, obj):
        return obj.end_time.strftime('%d.%m.%Y %H:%M')
    formatted_end.short_description = 'Дата и время окончания отправки'

@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'attempt_time', 'status')
    list_filter = ('status',)
    readonly_fields = ('attempt_time',)