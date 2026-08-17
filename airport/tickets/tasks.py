from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from django.core.mail import EmailMessage
from django.conf import settings
import requests

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

@shared_task
def send_ticket_email(ticket_id):
    ticket = Ticket.objects.select_related(
        "user",
        "flight",
        "flight__airline",
        "flight__departure_airport",
        "flight__arrival_airport",
        "flight__departure_airport__country",
        "flight__arrival_airport__country",
    ).get(id=ticket_id)

    user = ticket.user
    flight = ticket.flight

    # Data for PDF service
    data = {
        "ticket_id": ticket.id,
        "passenger_name": f"{user.profile.first_name} {user.profile.last_name}",
        "flight_number": f"FL-{flight.id}",

        "departure_country": (
            flight.departure_airport.country.title
        ),
        "departure_airport": (
            flight.departure_airport.name
        ),

        "arrival_country": (
            flight.arrival_airport.country.title
        ),
        "arrival_airport": (
            flight.arrival_airport.name
        ),

        "departure_time": flight.departure_time.isoformat(),
        "arrival_time": flight.arrival_time.isoformat(),

        "seat_number": ticket.seat_number,

        "airline": flight.airline.name,
    }

    # request to pdf service
    response = requests.post(
        settings.PDF_SERVICE_URL,
        json=data,
        timeout=30,
    )

    response.raise_for_status()

    pdf = response.content

    # Email
    email = EmailMessage(
        subject="Airport DRF | Your ticket",
        body=(
            f"Hello {user.profile.first_name},\n\n"
            f"Your ticket has been successfully purchased.\n\n"
            f"Flight: FL-{flight.id}\n"
            f"Seat: {ticket.seat_number}\n"
            f"Airline: {flight.airline.name}\n\n"
            f"Your boarding pass is attached to this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach(
        f"ticket_{ticket.id}.pdf",
        pdf,
        "application/pdf",
    )

    email.send(fail_silently=False)