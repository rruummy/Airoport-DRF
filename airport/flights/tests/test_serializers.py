from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from test_factories import create_airport, create_airline, create_airplane
from flights.serializers import FlightSerializer


class FlightSerializerTests(TestCase):
    def setUp(self):
        self.departure_airport = create_airport("Boryspil")
        self.arrival_airport = create_airport("Heathrow", city="London")
        self.airline = create_airline()
        self.airplane = create_airplane(airline=self.airline)

        self.departure_time = timezone.now() + timedelta(days=1)
        self.arrival_time = self.departure_time + timedelta(hours=3)

    def base_payload(self, **overrides):
        payload = {
            "departure_airport": self.departure_airport.id,
            "arrival_airport": self.arrival_airport.id,
            "airplane": self.airplane.id,
            "airline": self.airline.id,
            "departure_time": self.departure_time.strftime("%d.%m.%Y %H:%M"),
            "arrival_time": self.arrival_time.strftime("%d.%m.%Y %H:%M"),
            "price": "150.00",
            "status": "scheduled",
        }
        payload.update(overrides)
        return payload

    def test_valid_flight_data_passes(self):
        serializer = FlightSerializer(data=self.base_payload())
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_same_departure_and_arrival_airport_is_invalid(self):
        serializer = FlightSerializer(
            data=self.base_payload(arrival_airport=self.departure_airport.id)
        )
        self.assertFalse(serializer.is_valid())

    def test_arrival_before_departure_is_invalid(self):
        earlier = self.departure_time - timedelta(hours=1)
        serializer = FlightSerializer(
            data=self.base_payload(arrival_time=earlier.strftime("%d.%m.%Y %H:%M"))
        )
        self.assertFalse(serializer.is_valid())

    def test_zero_or_negative_price_is_invalid(self):
        serializer = FlightSerializer(data=self.base_payload(price="0.00"))
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)
