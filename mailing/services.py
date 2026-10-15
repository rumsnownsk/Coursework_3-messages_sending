from django.core.mail import send_mail
from django.conf import settings
from .models import Mailing, MailingAttempt


def send_mailing(mailing):
    if not mailing.message or not mailing.recipients.exists():
        return False, "Нет сообщения или получателей."

    success_count = 0
    fail_count = 0
    response_lines = []

    try:
        # Проверка: если уже запущена — не трогаем
        if mailing.status == Mailing.STATUS_RUNNING:
            return False, "Рассылка уже выполняется"

        # Ставим статус «В процессе»
        mailing.status = Mailing.STATUS_RUNNING
        mailing.save()

        for recipient in mailing.recipients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                success_count += 1
                response_lines.append(f"OK: {recipient.email}")
            except Exception as e:
                fail_count += 1
                response_lines.append(f"FAIL: {recipient.email} — {str(e)}")

        overall_status = (
            MailingAttempt.STATUS_SUCCESS
            if fail_count == 0
            else MailingAttempt.STATUS_FAILED
        )
        response_text = "\n".join(response_lines)

        MailingAttempt.objects.create(
            mailing=mailing,
            status=overall_status,
            server_response=response_text,
            success_count=success_count,
            fail_count=fail_count,
        )

        # Финальный статус
        if fail_count == 0:
            mailing.status = Mailing.STATUS_COMPLETED
        else:
            # Вариант 1: всё равно «Завершена», но с ошибками в отчёте
            mailing.status = Mailing.STATUS_COMPLETED
            # Вариант 2 (если хочешь помечать как ошибку):
            # mailing.status = Mailing.STATUS_FAILED

        mailing.save()

        if fail_count > 0:
            return False, f"Рассылка завершена с ошибками: {fail_count} писем не доставлено."
        else:
            return True, "Все письма успешно отправлены."

    except Exception as e:
        # Глобальная ошибка — ставим «Ошибка»
        mailing.status = Mailing.STATUS_FAILED
        mailing.error_message = str(e)
        mailing.save()
        return False, str(e)
