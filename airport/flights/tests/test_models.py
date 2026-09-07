from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from test_factories import create_airport, create_airline, create_airplane, create_flight


class FlightModelTests(TestCase):
    def test_str_shows_route(self):
        dep = create_airport("Boryspil")
        arr = create_airport("Heathrow", city="London")
        flight = create_flight(departure_airport=dep, arrival_airport=arr)

        self.assertEqual(str(flight), f"{dep} -> {arr}")

    def test_negative_price_is_invalid(self):
        flight = create_flight(price=Decimal("10.00"))
        flight.price = Decimal("-5.00")

        with self.assertRaises(ValidationError):
            flight.full_clean()


class AirlineAirplaneModelTests(TestCase):
    def test_airplane_str_includes_model_and_capacity(self):
        airline = create_airline(name="SkyJet")
        airplane = create_airplane(model="Airbus A320", capacity=150, airline=airline)

        self.assertEqual(str(airplane), "model: Airbus A320 capacity: 150")

    def test_airline_can_have_multiple_airports(self):
        airport1 = create_airport("Boryspil")
        airport2 = create_airport("Heathrow", city="London")
        airline = create_airline(name="MultiHub", airports=[airport1, airport2])

        self.assertEqual(airline.airport.count(), 2)
