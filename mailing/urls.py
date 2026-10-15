from django.urls import path
from mailing.apps import MailingConfig
from .views import HomeView

app_name = MailingConfig.name


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
]