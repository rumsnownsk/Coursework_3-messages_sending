from django.core.mail import send_mail
from django.conf import settings
from .models import MailingAttempt

def send_mailing(mailing):
    if not mailing.message or not mailing.recipients.exists():
        return False, "Нет сообщения или получателей."

    success_count = 0
    fail_count = 0
    response_lines = []

    for recipient in mailing.recipients.all():
        try:
            # Эта функция умная: если стоит console backend — она пишет в консоль.
            # Если вернёшь реальный SMTP — она отправит письмо.
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

    overall_status = MailingAttempt.STATUS_SUCCESS if fail_count == 0 else MailingAttempt.STATUS_FAILED
    response_text = "\n".join(response_lines)

    MailingAttempt.objects.create(
        mailing=mailing,
        status=overall_status,
        server_response=response_text,
    )

    return fail_count == 0, response_text