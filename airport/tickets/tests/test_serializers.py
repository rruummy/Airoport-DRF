from datetime import timedelta
from types import SimpleNamespace

from django.test import TestCase
from django.utils import timezone

from test_factories import create_flight, create_user, create_profile
from tickets.models import Ticket
from tickets.serializers import BookTicketSerializer


class BookTicketSerializerTests(TestCase):
    def setUp(self):
        self.flight = create_flight(
            departure_time=timezone.now() + timedelta(days=1),
        )
        self.user = create_user(email="booker@example.com")
        self.profile = create_profile(
            self.user, raw_passport="AB123456", first_name="Anna", last_name="Nova"
        )

    def context(self):
        # The serializer only ever touches ``request.user`` in .validate(),
        # so a lightweight stand-in is enough here.
        return {"request": SimpleNamespace(user=self.user)}

    def valid_payload(self, **overrides):
        payload = {
            "flight": self.flight.id,
            "seat_number": 3,
            "passport_number": "AB123456",
        }
        payload.update(overrides)
        return payload

    def test_valid_booking_passes(self):
        serializer = BookTicketSerializer(
            data=self.valid_payload(), context=self.context()
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_seat_already_booked_is_rejected(self):
        Ticket.objects.create(
            user=self.user, flight=self.flight, seat_number=3,
            status="booked", price=self.flight.price,
        )
        serializer = BookTicketSerializer(
            data=self.valid_payload(), context=self.context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("seat_number", serializer.errors)

    def test_seat_number_out_of_range_is_rejected(self):
        too_high = self.flight.airplane.capacity + 1
        serializer = BookTicketSerializer(
            data=self.valid_payload(seat_number=too_high), context=self.context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("seat_number", serializer.errors)

    def test_seat_number_below_one_is_rejected(self):
        serializer = BookTicketSerializer(
            data=self.valid_payload(seat_number=0), context=self.context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("seat_number", serializer.errors)

    def test_departed_flight_is_rejected(self):
        past_flight = create_flight(
            departure_time=timezone.now() - timedelta(hours=1),
            arrival_time=timezone.now() + timedelta(hours=1),
        )
        serializer = BookTicketSerializer(
            data=self.valid_payload(flight=past_flight.id), context=self.context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("flight", serializer.errors)

    def test_cancelled_flight_is_rejected(self):
        cancelled_flight = create_flight(status="cancelled")
        serializer = BookTicketSerializer(
            data=self.valid_payload(flight=cancelled_flight.id), context=self.context()
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("flight", serializer.errors)

    def test_wrong_passport_number_is_rejected(self):
        serializer = BookTicketSerializer(
            data=self.valid_payload(passport_number="ZZ999999"),
            context=self.context(),
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("passport_number", serializer.errors)

    def test_create_does_not_persist_the_raw_passport_number(self):
        serializer = BookTicketSerializer(
            data=self.valid_payload(), context=self.context()
        )
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save(user=self.user, price=self.flight.price, status="pending")

        self.assertFalse(hasattr(ticket, "passport_number"))
        self.assertEqual(ticket.status, "pending")
