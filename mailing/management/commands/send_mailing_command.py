from django.core.management import BaseCommand

from mailing.models import Mailing
from mailing.services import send_mailing


class Command(BaseCommand):
    help = 'Запускает функцию send_mailing для рассылки писем'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mailing-id',
            type=int,
            help='ID рассылки для отправки'
        )

    def handle(self, *args, **options):
        mailing_id = options.get('mailing_id')

        self.stdout.write(self.style.SUCCESS('Начинаем отправку рассылки...'))

        try:
            mailing = Mailing.objects.get(id=mailing_id)
            send_mailing(mailing)
            self.stdout.write(self.style.SUCCESS('Рассылка успешно отправлена!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Произошла ошибка при отправке: {e}'))
            raise