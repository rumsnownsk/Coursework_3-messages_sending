from django.forms import DateTimeInput
from django.utils import formats

class ISODateTimeLocalWidget(DateTimeInput):
    input_type = 'datetime-local'

    def format_value(self, value):
        if value is None:
            return ''
        # Принудительно используем ISO-формат, игнорируя USE_L10N
        # Формат YYYY-MM-DDTHH:MM обязателен для datetime-local
        return value.strftime('%Y-%m-%dT%H:%M')