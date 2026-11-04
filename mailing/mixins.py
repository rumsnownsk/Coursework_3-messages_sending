from django import forms
from django.forms import BooleanField

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