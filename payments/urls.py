from django.urls import path
from .views import TossConfirmAPIView, pay_page, OrderCreateAPIView
app_name = 'payments'

urlpatterns = [
    path("toss/pay/", pay_page),
    path("toss/orders/", OrderCreateAPIView.as_view()),
    path("toss/confirm/", TossConfirmAPIView.as_view()),
]