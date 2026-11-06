from django.db import models

from config import settings


# получатель
class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Почта')
    full_name = models.CharField(max_length=255, verbose_name='Ф. И. О.')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')

    # Связь: у каждого пользователя есть свой список получателей
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='my_recipients',  # теперь у user.my_recipients.all() — его личный список
        blank=True,
        verbose_name='Пользователи, которым доступен получатель'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения',
    )

    class Meta:
        verbose_name = 'Получатель рассылки'
        verbose_name_plural = 'Получатели рассылок'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


# само сообщение
class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема письма')
    body = models.TextField(verbose_name='Тело письма')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор сообщения',
        related_name='messages',  # удобно: user.messages.all()
        blank=True, null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения',
    )
    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_BLOCKED = 'blocked'          # новый


    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик (создана)'),
        (STATUS_RUNNING, 'В процессе (запущена)'),
        (STATUS_COMPLETED, 'Завершена'),
        (STATUS_FAILED, 'Ошибка'),
        (STATUS_BLOCKED, 'Заблокировано'),
    ]
    name = models.CharField(max_length=255, verbose_name='Название рассылки', blank=True, null=True)
    start_time = models.DateTimeField(verbose_name='Дата и время первой отправки')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='mailings',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Создал рассылку'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name='Статус',
        editable=False
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Сообщение'
    )

    recipients = models.ManyToManyField(
        Recipient,
        related_name='mailings',
        verbose_name='Получатели'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения',
    )
    error_traceback = models.TextField(blank=True, null=True, verbose_name='Полный стек ошибки')

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __str__(self):
        return f"Рассылка #{self.pk} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.name and self.message_id:
            self.name = self.message.subject
        super().save(*args, **kwargs)


class MailingAttempt(models.Model):
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'С ошибкой'),
    ]

    # время попытки отправки сообщения
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='Статус попытки'
    )

    server_response = models.TextField(blank=True, null=True, verbose_name='Ответ почтового сервера')
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка'
    )
    success_count = models.PositiveIntegerField(default=0)   # Опционально
    fail_count = models.PositiveIntegerField(default=0)     # Опционально
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения',
    )
    class Meta:
        verbose_name = 'Попытка рассылки'
        verbose_name_plural = 'Попытки рассылок'
        ordering = ['-attempt_time']

    def __str__(self):
        return f"{self.mailing_id} — {self.attempt_time} — {self.status}"


class AttemptItem(models.Model):
    """Результат отправки письма одному конкретному получателю."""

    class Status(models.TextChoices):
        SUCCESS = 'sent', 'Отправлено'
        FAILED = 'failed', 'Ошибка'

    attempt = models.ForeignKey(
        MailingAttempt,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Попытка',
    )
    recipient = models.ForeignKey(
        'Recipient',          # подставь имя своей модели получателя
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Получатель',
    )
    email = models.EmailField(verbose_name='Email на момент отправки')
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        verbose_name='Статус',
    )
    error_message = models.TextField(blank=True, default='', verbose_name='Ошибка')

    def __str__(self):
        return f'{self.email}: {self.get_status_display()}'

    class Meta:
        verbose_name = 'Деталь попытки'
        verbose_name_plural = 'Детали попыток'




