from django.shortcuts import render
from django.views.generic import TemplateView

from mailing.models import Mailing, Recipient


class HomeView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. Всего рассылок
        context['total_mailings'] = Mailing.objects.count()

        # 2. Активных рассылок (статус 'Запущена')
        context['active_mailings'] = Mailing.objects.filter(status='Запущена').count()

        # 3. Уникальных получателей
        # Если у тебя модель Recipient с полем email:
        context['unique_recipients'] = Recipient.objects.values('email').distinct().count()

        return context