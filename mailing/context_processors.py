from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count

from mailing.models import Mailing, Recipient


def common_data(request):
    if request.user.is_authenticated:
        user_mailings = Mailing.objects.filter(created_by=request.user)
        now = timezone.now()

        return {
            'is_manager': (
                request.user.is_superuser
                or request.user.groups.filter(name='Менеджер').exists()
            ),
            'total_mailings': user_mailings.count(),
            'active_mailings': user_mailings.filter(
                status=Mailing.STATUS_RUNNING,
                start_time__lte=now,
                end_time__gte=now
            ).count(),
            'unique_recipients': user_mailings.aggregate(
                total=Count('recipients', distinct=True)
            )['total'],

        }

    return {
        'is_manager': False,
        'recipients': Recipient.objects.none(),
        'total_users': get_user_model().objects.count(),
        'latest_mailings': (
            Mailing.objects
            .select_related('created_by', 'message')
            .annotate(recipients_count=Count('recipients'))
            .order_by('-created_at')[:10]
        ),
    }
