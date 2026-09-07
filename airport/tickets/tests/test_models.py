from django.db import IntegrityError, transaction
from django.test import TestCase

from test_factories import create_flight, create_user
from tickets.models import Ticket


class TicketSeatConstraintTests(TestCase):
    def setUp(self):
        self.flight = create_flight()
        self.user = create_user(email="ticket-owner@example.com")

    def make_ticket(self, seat_number, status):
        return Ticket.objects.create(
            user=self.user,
            flight=self.flight,
            seat_number=seat_number,
            status=status,
            price=self.flight.price,
        )

    def test_two_active_tickets_for_same_seat_are_rejected(self):
        self.make_ticket(seat_number=5, status="booked")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_ticket(seat_number=5, status="pending")

    def test_active_statuses_conflict_with_each_other(self):
        self.make_ticket(seat_number=7, status="paid")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_ticket(seat_number=7, status="booked")

    def test_cancelled_ticket_frees_up_the_seat(self):
        self.make_ticket(seat_number=9, status="cancelled")

        # Should not raise: "cancelled" is not one of the active statuses.
        second = self.make_ticket(seat_number=9, status="pending")
        self.assertIsNotNone(second.pk)

    def test_different_seats_on_same_flight_are_fine(self):
        self.make_ticket(seat_number=1, status="booked")
        second = self.make_ticket(seat_number=2, status="booked")
        self.assertIsNotNone(second.pk)
