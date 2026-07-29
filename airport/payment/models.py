from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator


class Payment(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    ticket = models.OneToOneField("tickets.Ticket", on_delete=models.PROTECT, related_name="payment")

    user = models.ForeignKey("user.User", on_delete=models.CASCADE)

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)