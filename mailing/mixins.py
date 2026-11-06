from django import forms

from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin

from config import settings


class StyleMixin:
    """
    Универсальный миксин для стилизации форм.
    Подбирает класс Bootstrap по типу виджета, не перезаписывая кастомные.
    """
    BASE_INPUT_CLASS = 'form-control'       # текст, email, дата, число
    CHECKBOX_CLASS = 'form-check-input'     # одиночные и множественные чекбоксы
    SELECT_CLASS = 'form-select'            # выпадающие списки и мультиселекты
    TEXTAREA_CLASS = 'form-control'         # textarea стилизуется как input

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            widget = field.widget
            current_classes = widget.attrs.get('class', '').split()

            # 1. Чекбоксы: и одиночные (CheckboxInput),
            #    и списки галочек (CheckboxSelectMultiple)
            if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
                pass
                # if self.CHECKBOX_CLASS not in current_classes:
                #     current_classes.append(self.CHECKBOX_CLASS)

            # 2. Селекты: обычные и множественные
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                if self.SELECT_CLASS not in current_classes:
                    current_classes.append(self.SELECT_CLASS)

            # 3. Textarea (Textarea наследуется от Input, поэтому проверяем раньше)
            elif isinstance(widget, forms.Textarea):
                if self.TEXTAREA_CLASS not in current_classes:
                    current_classes.append(self.TEXTAREA_CLASS)
                if 'form-control' in current_classes:
                    current_classes.append('mb-2')  # опционально: отступ

            # 4. Всё остальное — обычные текстовые поля
            else:
                if self.BASE_INPUT_CLASS not in current_classes:
                    current_classes.append(self.BASE_INPUT_CLASS)

            widget.attrs['class'] = ' '.join(current_classes)



class EmailVerificationRequiredMixin:
    """
    Запрещает создание сущностей, если email не подтверждён.
    Показывает уведомление и возвращает пользователя обратно.
    """
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_email_verified:
            messages.warning(
                request,
                'Ваш email не подтверждён. Создание доступно только после подтверждения email — '
                'проверьте почту или запросите письмо повторно.'
            )
            # Возвращаем на ту же страницу, откуда нажали кнопку
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)
            # Fallback, если referer пустой (бывает при прямом вводе URL)
            return redirect('mailing:mailings')

        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(UserPassesTestMixin):
    """Доступ только для менеджеров и суперпользователей."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_superuser
            or user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists()
        )