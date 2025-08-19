"""
URL configuration for Atmos payment app.
"""

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import AtmosWebhookAPIView

urlpatterns = [
    path('payments/atmos/webhook/',
         csrf_exempt(AtmosWebhookAPIView.as_view()),
         name='atmos_webhook'),
]
