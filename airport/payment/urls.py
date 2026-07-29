from django.urls import path
from payment.views import CreateCheckoutView, StripeWebhookView, PaymentCancelView, PaymentSuccessView

urlpatterns = [
    path("payment/checkout/<int:pk>/", CreateCheckoutView.as_view(), name="create-checkout"),
    path("webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("payment/success/", PaymentSuccessView.as_view()),
    path("payment/cancel/", PaymentCancelView.as_view()),
]