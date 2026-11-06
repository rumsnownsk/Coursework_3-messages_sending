import traceback

from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now

from .models import Mailing, MailingAttempt, AttemptItem, Recipient


def send_mailing(mailing_id):
    mailing = Mailing.objects.filter(pk=mailing_id).first()
    if not mailing:
        return False, f"Рассылка с ID {mailing_id} не найдена."

    if not mailing.message or not mailing.recipients.exists():
        return False, "Нет сообщения или получателей."

    if not mailing.start_time < now() < mailing.end_time:
        return False, f"Дата рассылки <{mailing.name}> ещё не настала"

    from_email = settings.DEFAULT_FROM_EMAIL  # например, sra-bot@ya.ru

    success_count = 0
    fail_count = 0
    response_lines = []

    try:
        # Повторный запуск той же рассылки — защита
        if mailing.status == Mailing.STATUS_RUNNING:
            return False, "Рассылка уже выполняется"

        mailing.status = Mailing.STATUS_RUNNING
        mailing.save()

        # Попытка создаётся в момент старта, а не в конце —
        # если сервер упадёт посередине, попытка останется в логе
        attempt = MailingAttempt.objects.create(
            mailing=mailing,
            status=MailingAttempt.STATUS_FAILED,   # предварительный статус
            server_response='',
            success_count=0,
            fail_count=0,
        )

        for recipient in mailing.recipients.all():
            try:
                send_mail(
                    subject=mailing.message.subject + f'. (отправитель: {mailing.created_by.email})',
                    message=mailing.message.body,
                    from_email=from_email,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                success_count += 1
                AttemptItem.objects.create(
                    attempt=attempt,
                    recipient=recipient,
                    email=recipient.email,
                    status=AttemptItem.Status.SUCCESS,
                )
            except Exception as e:
                fail_count += 1
                response_lines.append(f"FAIL: {fail_count} — {str(e)}")
                AttemptItem.objects.create(
                    attempt=attempt,
                    recipient=recipient,
                    email=recipient.email,
                    status=AttemptItem.Status.FAILED,
                    error_message=str(e),
                )

        # Обновляем существующую попытку итогами
        attempt.success_count = success_count
        attempt.fail_count = fail_count
        attempt.server_response = f"OK: {success_count}; FAIL: {fail_count}"
        attempt.status = (
            MailingAttempt.STATUS_SUCCESS if fail_count == 0
            else MailingAttempt.STATUS_FAILED
        )
        attempt.save()

        # Финальный статус рассылки
        mailing.status = Mailing.STATUS_COMPLETED
        mailing.save()

        if fail_count > 0:
            return False, f"Рассылка завершена с ошибками: {fail_count} писем не доставлено."
        return True, "Все письма успешно отправлены."

    except Exception as e:
        mailing.status = Mailing.STATUS_FAILED
        mailing.error_message = str(e)
        mailing.error_traceback = traceback.format_exc()
        mailing.save()
        return False, str(e)


def is_manager(user):
        return user.is_superuser or user.groups.filter(name='Менеджер').exists()


def get_visible_mailings(user):
    qs = Mailing.objects.select_related('created_by', 'message')

    return qs if is_manager(user) else qs.filter(created_by=user)

def get_visible_recipients(user):
    qs = Recipient.objects.all()
    if is_manager(user):
        return qs
    else:
        return qs.filter(users=user)