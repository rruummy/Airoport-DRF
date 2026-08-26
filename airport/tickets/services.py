import requests
from django.conf import settings


def generate_ticket_pdf(ticket, user):
    flight = ticket.flight
    profile = user.profile

    data = {
    "ticket_id": ticket.id,

    "passenger_name": f"{profile.first_name} {profile.last_name}",
    "flight_number": f"FL-{flight.id}",

    "departure_country": flight.departure_airport.country.title,
    "departure_airport": flight.departure_airport.name,

    "arrival_country": flight.arrival_airport.country.title,
    "arrival_airport": flight.arrival_airport.name,

    "departure_time": flight.departure_time.isoformat(),
    "arrival_time": flight.arrival_time.isoformat(),

    "seat_number": ticket.seat_number,

    "airline": flight.airline.name,
}

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

    return response.content