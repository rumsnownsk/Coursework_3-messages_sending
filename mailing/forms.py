from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from mailing.models import Mailing, Recipient
from users.models import CustomUser
from django.forms import BooleanField
from django.utils import timezone
from .mixins import StyleMixin
from .widgets import ISODateTimeLocalWidget

User = get_user_model()


class EmailVerificationForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите ваш email',
            'autocomplete': 'email'
        }),
        label='Email'
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже используется другим аккаунтом.")
        return email


class MailingForm(StyleMixin, forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=Recipient.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Получатели'
    )

    class Meta:
        model = Mailing
        fields = ['name', 'message','recipients', 'start_time', 'end_time']  # подстрой под свои поля
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только тех получателей, которые принадлежат текущему пользователю
        self.fields['recipients'].queryset = Recipient.objects.filter(users=user)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')

        now = timezone.now()

        # 1. Конец должен быть позже начала
        if start and end and end <= start:
            raise ValidationError('Время окончания должно быть позже времени начала.')

        # 2. Начало не должно быть в прошлом
        if start and start < now:
            raise ValidationError('Дата начала рассылки не может быть в прошлом.')

        # (опционально) Конец тоже можно запретить в прошлом, если нужно
        if end and end < now:
            raise ValidationError('Дата окончания рассылки не может быть в прошлом.')

        return cleaned_data


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }