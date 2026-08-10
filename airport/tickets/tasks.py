from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from tickets.models import Ticket


@shared_task
def cancel_expired_tickets():
    now = timezone.now()
    expiration_time = now - timedelta(minutes=15)

    tickets = Ticket.objects.filter(
        status="pending",
        created_at__lte=expiration_time,
    )

    count = tickets.update(status="cancelled")

    print(f"Cancelled {count} expired tickets.")