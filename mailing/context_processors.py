from django.contrib.auth import get_user_model

import users
from mailing.models import Mailing, Recipient


def common_data(request):
    if request.user.is_authenticated:
        user_mailings = Mailing.objects.filter(created_by=request.user)
        return {
            'recipients': Recipient.objects.filter(users=request.user),
            'total_mailings': user_mailings.count(),
            'active_mailings': user_mailings.filter(status=Mailing.STATUS_RUNNING).count(),
        }

    all_mailings = Mailing.objects.all()
    user = get_user_model()
    return {
        'recipients': Recipient.objects.none(),  # пустой список вместо отсутствия ключа
        'total_users': user.objects.count(),
        'total_mailings': all_mailings.count(),
        'active_mailings': all_mailings.filter(status=Mailing.STATUS_RUNNING).count(),
    }