from django import forms
from django.forms import BooleanField, CharField
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

from users.models import CustomUser


class StyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs.setdefault('class', 'form-check-input')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class CustomLoginForm(StyleMixin, AuthenticationForm):
    remember_me = BooleanField(required=False, label="Запомнить меня")

    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваш логин'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = '⚠️ Логин'
        self.fields['password'].label = '⚠️ Пароль'

        self.fields['username'].widget.attrs.update({'placeholder': 'Логин или email'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Пароль'})


class CustomRegisterForm(StyleMixin, UserCreationForm):
    username = CharField(
        required=True,
        help_text=''
    )
    email = forms.EmailField(
        required=False,
        label="Ваш Email (Не обязательно)"
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 1. Переименовываем стандартные поля
        self.fields['username'].label = "Придумайте логин (⚠️ Обязательно для регистрации)"

        self.fields['email'].label = "Ваш Email (Не обязательно)"

        # 2. САМОЕ ВАЖНОЕ: меняем названия для паролей
        # password1 — это первое поле пароля
        self.fields['password1'].label = "🔒 Придумайте пароль (Минимум 4 символа.)"
        # password2 — это подтверждение пароля
        self.fields['password2'].label = "🔒 Повторите пароль"

        # Опционально: меняем help_text (подсказки под полем)
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""

        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'form-control password-field',
            'id': 'id_password1',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'form-control password-field',
            'id': 'id_password2',
            'placeholder': 'Повторите пароль'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')

        # ГЛАВНОЕ: если пользователь ничего не ввёл, превращаем '' в None
        if email == '':
            return None

        # Если email заполнен — проверяем уникальность вручную, чтобы дать понятное сообщение
        if email:
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("Такой email уже зарегистрирован. Используйте другой или оставьте поле пустым.")

        return email