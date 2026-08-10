from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from flights.models import Flight
from tickets.models import Ticket
from emails.utils import send_flight_reminder_email


@shared_task
def send_flight_reminders():
    now = timezone.now()
    reminder_time = now + timedelta(hours=12)

    print("NOW:", now)
    print("REMINDER TIME:", reminder_time)

    flights = Flight.objects.filter(
        departure_time__gte=reminder_time - timedelta(minutes=5),
        departure_time__lt=reminder_time + timedelta(minutes=5),
        status="scheduled",
    )

    print("FOUND FLIGHTS:", flights.count())

    for flight in flights:
        print(
            "FLIGHT:",
            flight.id,
            "DEPARTURE:",
            flight.departure_time,
        )

        tickets = Ticket.objects.filter(
            flight=flight,
            status="paid",
            reminder_sent=False,
        ).select_related("user")

        print("FOUND TICKETS:", tickets.count())

        for ticket in tickets:
            print(
                "SENDING REMINDER:",
                ticket.id,
                "TO:",
                ticket.user.email,
            )

            send_flight_reminder_email(ticket)

            ticket.reminder_sent = True
            ticket.save(update_fields=["reminder_sent"])

            print("REMINDER SENT:", ticket.id)