from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate

from .forms import CustomLoginForm, CustomRegisterForm



# Create your views here.

class CustomRegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = CustomRegisterForm
    success_url = reverse_lazy('mailing:home')


    def form_valid(self, form):
        user = form.save()

        authenticated_user = authenticate(
            request=self.request,
            username=user.username,
            password=form.cleaned_data['password1'],
        )

        if authenticated_user is not None:
            login(self.request, authenticated_user)

        return redirect('mailing:mailings')

    #     # 3. Теперь безопасно делаем login. Django знает, что этот юзер уже проверен твоим бэкендом.
    #     login(self.request, user_authenticated)
    #
    #     # 4. Отправляем письмо
    #     # self.send_welcome_email(user.email)
    #
    #     # return super().form_valid(form)
    #     return redirect('catalog:products_list')
    #
    # def send_welcome_email(self, user_email):
    #     from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@hw-m6-django.local')
    #
    #     subject = 'Добро пожаловать в наш сервис'
    #     message = 'Спасибо, что зарегистрировались в нашем сервисе!'
    #     recipient_list = [user_email,]
    #     send_mail(subject, message, from_email, recipient_list)

class CustomLoginView(LoginView):
    template_name = 'users/login.html'  # <-- путь к твоему шаблону login.html
    form_class = CustomLoginForm
    redirect_authenticated_user = True  # если залогинен, не пускать на страницу логина
    success_url = reverse_lazy('mailing:mailings')  # <-- сюда после успешного входа

