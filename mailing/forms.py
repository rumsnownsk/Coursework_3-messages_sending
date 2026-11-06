from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from mailing.models import Mailing, Recipient, Message
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
            'autocomplete': 'email',
        }),
        label='Email'
    )

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)   # current_user сюда НЕ передаём
        self.current_user = current_user

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        User = get_user_model()
        qs = User.objects.filter(email=email)
        if self.current_user:
            qs = qs.exclude(pk=self.current_user.pk)  # свой email — не «занятый»
        if qs.exists():
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
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',  # формат, который понимает datetime-local
            ),
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем только тех получателей, которые принадлежат текущему пользователю
        if user is not None:
            # В списках выбора — только свои записи
            if 'message' in self.fields:
                self.fields['message'].queryset = Message.objects.filter(created_by=user)
            if 'recipients' in self.fields:
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
        if not self.instance.pk:
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

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']  # created_by НЕ включаем в форму — заполним во вьюхе
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Рассылка про скидки ноября'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Текст письма... Можно использовать HTML, если планируешь позже'
            }),
        }
        labels = {
            'subject': 'Тема письма',
            'body': 'Текст письма (тело)',
        }