from datetime import timedelta

import requests

from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
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

    return count


@shared_task
def generate_ticket_pdf_task(ticket_id):
    ticket = Ticket.objects.select_related(
        "user",
        "user__profile",
        "flight",
        "flight__airline",
        "flight__departure_airport",
        "flight__departure_airport__country",
        "flight__arrival_airport",
        "flight__arrival_airport__country",
    ).get(id=ticket_id)

    user = ticket.user
    flight = ticket.flight
    profile = user.profile

    # -----------------------------------------
    # Data for PDF service
    # -----------------------------------------

    data = {
        "ticket_id": ticket.id,

        "passenger_name": (
            f"{profile.first_name} {profile.last_name}"
        ),

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

        "departure_time": (
            flight.departure_time.isoformat()
        ),

        "arrival_time": (
            flight.arrival_time.isoformat()
        ),

        "seat_number": ticket.seat_number,

        "airline": flight.airline.name,
    }

    # -----------------------------------------
    # Generate PDF through FastAPI microservice
    # -----------------------------------------

    response = requests.post(
        settings.PDF_SERVICE_URL,
        json=data,
        timeout=30,
    )

    if response.status_code != 200:
        print("PDF SERVICE ERROR:")
        print(response.status_code)
        print(response.text)

    response.raise_for_status()

    pdf = response.content

    # -----------------------------------------
    # Save PDF to S3
    # -----------------------------------------

    ticket.pdf_file.save(
        f"ticket_{ticket.id}.pdf",
        ContentFile(pdf),
        save=True,
    )

    # -----------------------------------------
    # Send email
    # -----------------------------------------

    email = EmailMessage(
        subject="Airport DRF | Your ticket",
        body=(
            f"Hello {profile.first_name},\n\n"
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

    return ticket.id