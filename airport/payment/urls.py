from django.urls import path
from payment.views import (
    CreateCheckoutView,
    StripeWebhookView,
    PaymentCancelView,
    PaymentSuccessView,
)

urlpatterns = [path("checkout/<int:pk>/", CreateCheckoutView.as_view(), name="create-checkout",),
    path("webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel",),
]