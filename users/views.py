from django.contrib.auth.views import LoginView
from django.views.generic import CreateView

from .forms import CustomUserLoginForm



# Create your views here.

class CustomRegisterView(CreateView):
    pass
    # template_name = 'users/register.html'
    # form_class = CustomUserCreationForm
    # success_url = reverse_lazy('catalog:products_list')
    #
    # def form_valid(self, form):
    #     user = form.save()
    #
    #     user_authenticated = authenticate(
    #         request=self.request,
    #         username=user.email,
    #         password=form.cleaned_data['password1'],
    #         backend='users.backends.EmailAuthBackend'
    #     )
    #
    #     if user_authenticated is None:
    #         return self.render_to_response(
    #             self.get_context_data(form=form, error="Не удалось подтвердить пароль")
    #         )
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
    form_class = CustomUserLoginForm
    redirect_authenticated_user = True  # если залогинен, не пускать на страницу логина