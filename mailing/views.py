from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy, reverse
from django.views.generic import View, ListView, TemplateView, DetailView, CreateView, UpdateView, DeleteView

from mailing.decorators import require_verified_email
from mailing.forms import *
from mailing.mixins import EmailVerificationRequiredMixin
from mailing.models import Mailing, Recipient, Message
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode


User = get_user_model()
class HomeView(TemplateView):
    template_name = 'main.html'

    # def get_context_data(self, **kwargs):
    # context = super().get_context_data(**kwargs)
    #
    # # 1. Всего рассылок
    # context['total_mailings'] = Mailing.objects.count()
    #
    # # 2. Активных рассылок (статус 'Запущена')
    # context['active_mailings'] = Mailing.objects.filter(status='Запущена').count()
    #
    # # 3. Уникальных получателей
    # # Если у тебя модель Recipient с полем email:
    # context['unique_recipients'] = Recipient.objects.values('email').distinct().count()
    #
    # return context

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        # Только рассылки текущего пользователя
        return Mailing.objects.filter(created_by=self.request.user)

@require_verified_email()
class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # передаём пользователя в форму
        return kwargs

    def form_valid(self, form):
        mailing = form.save(commit=False)
        mailing.created_by = self.request.user
        mailing.save()

        # Сохраняем ManyToMany (получатели)
        form.save_m2m()
        return redirect('mailing:mailings')
        # return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'

    def get_queryset(self):
        # Защита: пользователь может редактировать только свои рассылки
        return Mailing.objects.filter(created_by=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        mailing = form.save(commit=False)
        # created_by уже есть, менять не нужно
        mailing.save()
        form.save_m2m()
        return redirect('mailing:mailings')

class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailings')

    def get_queryset(self):
        # Защита: пользователь может удалять только свои рассылки
        return Mailing.objects.filter(created_by=self.request.user)


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'recipient/recipient_list.html'
    # context_object_name = 'recipients'

@require_verified_email()
class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'recipient/recipient_form.html'
    success_url = reverse_lazy('mailing:recipients')

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email', '').strip().lower()
        recipient = Recipient.objects.filter(email__iexact=email).first()

        if recipient:
            # Сценарий 1: Значит этот email уже есть в базе в таблице Recipient (может быть, у другого пользователя)
            if recipient.users.filter(pk=request.user.pk).exists():
                messages.info(request, 'Этот получатель уже есть в вашем списке.')
            else:
                recipient.users.add(request.user)
                messages.success(request, f'Получатель <{email}> уже существовал в системе — мы добавили его в ваш список.')

            return redirect(self.success_url)

        # Сценарий 2: email новый — создаём как обычно
        return super().post(request, *args, **kwargs)


    def form_valid(self, form):
        recipient = form.save()
        recipient.users.add(self.request.user)
        return super().form_valid(form)

class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'recipient/recipient_form.html'
    success_url = reverse_lazy('mailing:recipients')


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'recipient/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailing:recipients')

    def get_queryset(self):
        # Защита: разрывать связь можно только с теми получателями, что есть в вашем списке
        return Recipient.objects.filter(users=self.request.user)

    def form_valid(self, form):
        self.object.users.remove(self.request.user)
        return redirect(self.success_url)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'message/message_list.html'
    context_object_name = 'message_list'

    def get_queryset(self):
        return Message.objects.filter(created_by=self.request.user)

@require_verified_email()
class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'message/message_form.html'  # подставь свой путь к шаблону

    def form_valid(self, form):
        # Создаём объект, но пока не сохраняем в БД
        message = form.save(commit=False)
        # Привязываем к текущему пользователю
        message.created_by = self.request.user
        message.save()

        # Добавляем уведомление для шаблона (то самое messages)
        messages.success(self.request, f'Письмо "{message.subject}" успешно создано!')
        return redirect('mailing:messages')  # имя твоего URL для списка писем

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать шаблон письма'
        return context

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'message/message_form.html'  # тот же шаблон, что и для создания
    context_object_name = 'message'            # в шаблоне будет переменная message (объект)

    def get_queryset(self):
        """
        Показываем только те письма, которые принадлежат текущему пользователю.
        Это защита: пользователь не сможет редактировать чужие письма даже по URL.
        """
        return Message.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        message = form.save(commit=False)
        message.created_by = self.request.user
        message.save()

        messages.success(self.request, f'Письмо "{message.subject}" успешно обновлено!')
        return redirect('mailing:messages')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактировать шаблон письма'
        return context

class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    # template_name нужно указать — это страница «Вы уверены, что хотите удалить?»
    template_name = 'message/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:messages')

    def get_queryset(self):
        # Защита: пользователь видит и может удалять только свои письма
        return Message.objects.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        subject = obj.subject  # сохраняем тему для уведомления
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Письмо "{subject}" успешно удалено.')
        return response


class EmailVerificationRequestView(LoginRequiredMixin, View):
    """
    Принимает POST с email, сохраняет его пользователю (если нужно)
    и отправляет письмо со ссылкой для подтверждения.
    """
    def post(self, request, *args, **kwargs):
        form = EmailVerificationForm(request.POST, current_user=request.user)

        if form.is_valid():
            new_email = form.cleaned_data['email']
            user = request.user

            # 1. Сохраняем email, если его не было или он ещё не подтверждён
            if not user.email or not user.is_email_verified:
                user.email = new_email
                user.is_email_verified = False
                user.save(update_fields=['email', 'is_email_verified'])

            # 2. Генерируем токен
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # 3. Собираем ссылку через reverse, чтобы не хардкодить путь
            path = reverse('mailing:verify_email_confirm', kwargs={
                'uidb64': uid, 'token': token
            })
            verification_link = request.build_absolute_uri(path)

            # 4. Отправляем письмо
            subject = "Подтверждение email для messages_sending"
            message = render_to_string('mailing/email_verification.txt', {
                'user': user,
                'link': verification_link,
            })

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "✅ Ссылка для подтверждения отправлена на ваш email!")
            return redirect('mailing:mailings')

        # Показываем конкретные ошибки валидации
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(request, error)
        return redirect('mailing:mailings')

    # GET-запрос сюда приходить от формы не должен,
    # но если кто-то зайдёт по URL — отправляем на дашборд
    def get(self, request, *args, **kwargs):
        return redirect('mailing:mailings')


class EmailVerificationConfirmView(View):
    """
    Обрабатывает подтверждение по ссылке: проверяет токен и ставит is_email_verified=True
    """
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])
            messages.success(request, "Email успешно подтверждён! Теперь функционал полностью доступен.")
            return redirect('mailing:mailings')
        else:
            messages.error(request, "Неверная или истёкшая ссылка для подтверждения.")
            return redirect('mailing:mailings')