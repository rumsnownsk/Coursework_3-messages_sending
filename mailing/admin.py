from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
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



# --- 1. Функция для МАССОВОГО запуска (через галочки и выпадающий список) ---
def action_send_mailings(modeladmin, request, queryset):
    """
    Запускает выбранные рассылки.
    request: объект запроса (нужен для сообщений пользователю)
    queryset: набор выбранных объектов (те, где стоят галочки)
    """
    success_count = 0
    error_count = 0
    for mailing in queryset:
        success, _ = send_mailing(mailing)
        if success:
            success_count += 1
        else:
            error_count += 1

    if success_count:
        messages.success(request, f"{success_count} рассылок успешно отправлено.")
    if error_count:
        messages.error(request, f"В {error_count} рассылках были ошибки.")
action_send_mailings.short_description = "Запустить выбранные рассылки"


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    # --- 2. Настройка колонок ---
    list_display = ('id', 'name_link', 'status', 'formatted_start', 'formatted_end', 'action_buttons')
    list_filter = ('status',)
    inlines = [MailingAttemptInline]
    actions = [action_send_mailings, 'delete_selected']

    def action_buttons(self, obj):
        # Ссылка на индивидуальный запуск (кастомный view)
        send_url = reverse('admin:mailing_mailing_send', args=[obj.pk])
        # Ссылка на стандартное удаление Django (с подтверждением)
        delete_url = reverse('admin:mailing_mailing_delete', args=[obj.pk])

        buttons = format_html(
            '<a href="{}" class="button">Запустить</a> '
            '<a href="{}" class="button button-danger">Удалить</a>',
            send_url, delete_url
        )
        return buttons
    action_buttons.short_description = "Действия"

    def name_link(self, obj):
        url = reverse('admin:mailing_mailing_change', args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)
    name_link.short_description = "Название рассылки"

    def formatted_start(self, obj):
        return obj.start_time.strftime('%d.%m.%Y %H:%M')
    formatted_start.short_description = 'время первой отправки'

    def formatted_end(self, obj):
        return obj.end_time.strftime('%d.%m.%Y %H:%M')
    formatted_end.short_description = 'время окончания отправки'

    def get_urls(self):
        urls = super().get_urls()
        # Добавляем наш кастомный путь: /admin/mailing/mailing/<id>/send/
        # Путь для кнопки "Запустить" в строке
        custom_urls = [
            path('<int:pk>/send/', self.admin_site.admin_view(self.send_view), name='mailing_mailing_send'),
        ]
        return custom_urls + urls

    def send_view(self, request, pk):
        try:
            mailing = Mailing.objects.get(pk=pk)

            success, _ = send_mailing(mailing)


            if success:
                messages.success(request, f"Рассылка <{mailing.name}> успешно выполнена.")
            else:
                messages.error(request, f"Провал в выполнении рассылки <{mailing.name}>")


        except Mailing.DoesNotExist:
            self.message_user(request, "Рассылка не найдена")

        # После действия возвращаем пользователя обратно в список рассылок
        return HttpResponseRedirect(reverse('admin:mailing_mailing_changelist'))


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'attempt_time', 'status')
    list_filter = ('status',)
    readonly_fields = ('attempt_time',)