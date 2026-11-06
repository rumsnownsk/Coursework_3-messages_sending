from django.urls import path
from mailing.apps import MailingConfig
from .apps import UsersConfig
from .views import CustomLoginView, CustomRegisterView
from django.contrib.auth.views import LogoutView

app_name = UsersConfig.name


urlpatterns = [
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='mailing:main'), name='logout')
]