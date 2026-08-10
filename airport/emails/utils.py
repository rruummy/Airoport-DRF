from django.core.mail import send_mail, EmailMessage
from django.conf import settings


def send_profile_update_email(user, changes):
    changes_text = "\n".join(
        f"{field}: {old} -> {new}"
        for field, (old, new) in changes.items()
    )

    send_mail(
        subject="Airport DRF | Profile updated",
        message=(
            f"Hello {user.username},\n\n"
            "Your profile has been successfully updated.\n\n"
            "Changed fields:\n"
            f"{changes_text}\n\n"
            "If you did not make these changes, please contact support."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
def send_password_successfully_updated_email(user):
    send_mail(
        subject="Airport DRF | Password updated",
        message=(
            f"Hello {user.username},\n\n"
            "Your password was changed.\n\n"
            "If you did not make these changes, please contact support."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_ticket_purchase_email(ticket):
    flight = ticket.flight
    user = ticket.user

    subject = f"Airport DRF | Ticket #{ticket.id}"

    message = f"""Hello {user.username},

Your ticket has been successfully purchased!

Ticket information:
--------------------------------
Ticket: #{ticket.id}
Status: {ticket.get_status_display()}
Price: {ticket.price} EUR

Flight:
Flight ID: #{flight.id}

Departure:
Airport: {flight.departure_airport.name}
City: {flight.departure_airport.city}
Time: {flight.departure_time.strftime("%d.%m.%Y %H:%M")}

Arrival:
Airport: {flight.arrival_airport.name}
City: {flight.arrival_airport.city}
Time: {flight.arrival_time.strftime("%d.%m.%Y %H:%M")}

Seat: {ticket.seat_number}
Airline: {flight.airline.name}
Airplane: {flight.airplane.model}

--------------------------------

Thank you for using Airport DRF!
"""

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.send(fail_silently=False)

def send_flight_reminder_email(ticket):
    flight = ticket.flight
    user = ticket.user

    send_mail(
        subject="Airport DRF | Flight reminder",
        message=(
            f"Hello {user.username},\n\n"
            f"This is a reminder about your upcoming flight.\n\n"
            f"Flight: #{flight.id}\n"
            f"Seat: {ticket.seat_number}\n"
            f"Departure: {flight.departure_time}\n\n"
            "Your flight departs in approximately 12 hours.\n\n"
            "Have a nice flight!"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
