# mailing/decorators.py
from django.contrib import messages
from django.shortcuts import redirect
from functools import wraps

def require_verified_email(redirect_name='mailing:profile'):
    def decorator(cls):
        original_dispatch = cls.dispatch

        @wraps(original_dispatch)
        def wrapped_dispatch(self, request, *args, **kwargs):
            # Перехватываем только отправку формы
            if request.method == 'POST' and request.user.is_authenticated \
                    and not request.user.is_email_verified:
                messages.warning(
                    request,
                    'Ваш email не подтверждён. Сохранение недоступно — сначала подтвердите email.'
                )
                # Возвращаем на ту же страницу: визуально «ничего не произошло»
                referer = request.META.get('HTTP_REFERER')
                if referer:
                    return redirect(referer)
                return redirect(redirect_name)

            # GET — страница открывается, форма отображается как обычно
            return original_dispatch(self, request, *args, **kwargs)

        cls.dispatch = wrapped_dispatch
        return cls
    return decorator