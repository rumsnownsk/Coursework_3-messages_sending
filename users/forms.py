from django.forms import BooleanField
from django.contrib.auth.forms import AuthenticationForm


class StyleMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs.setdefault('class', 'form-check-input')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class CustomUserLoginForm(StyleMixin, AuthenticationForm):
    remember_me = BooleanField(required=False, label="Запомнить меня")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = '✅ Логин или email'
        self.fields['password'].label = '✅ Пароль'

        self.fields['username'].widget.attrs.update({'placeholder': 'Логин или email'})
        self.fields['password'].widget.attrs.update({'placeholder': 'Пароль'})