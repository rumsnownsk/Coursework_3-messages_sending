from django.urls import path
from mailing.apps import MailingConfig
from .models import Message
from .views import *

app_name = MailingConfig.name


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('account/', MailingListView.as_view(), name='mailings'),
    path('account/mailing/create', MailingCreateView.as_view(), name='mailing_create'),
    path('account/mailing/<int:pk>/update', MailingUpdateView.as_view(), name='mailing_update'),
    path('account/mailing/<int:pk>/delete', MailingDeleteView.as_view(), name='mailing_delete'),


    path('account/recipient', RecipientListView.as_view(), name='recipients'),
    path('account/recipient/create', RecipientCreateView.as_view(), name='recipient_create'),
    path('account/recipient/<int:pk>/update', RecipientUpdateView.as_view(), name='recipient_update'),
    path('account/recipient/<int:pk>/delete', RecipientDeleteView.as_view(), name='recipient_delete'),


    path('account/messages', MessageListView.as_view(), name='messages'),
    # path('account/recipient/create', RecipientCreateView.as_view(), name='recipient_create'),
    # path('account/recipient/<int:pk>/update', RecipientUpdateView.as_view(), name='recipient_update'),
    # path('account/recipient/<int:pk>/delete', RecipientDeleteView.as_view(), name='recipient_delete'),




    path('request-verification/', EmailVerificationRequestView.as_view(), name='request_verification'),

    path('verify-email/<uidb64>/<token>/', EmailVerificationConfirmView.as_view(), name='verify_email_confirm'),


]

