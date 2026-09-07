from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from test_factories import create_flight, create_user
from tickets.models import Ticket
from tickets.tasks import cancel_expired_tickets


class CancelExpiredTicketsTests(TestCase):
    def setUp(self):
        self.flight = create_flight()
        self.user = create_user(email="expiring@example.com")

    def make_ticket(self, seat_number, created_at, status="pending"):
        ticket = Ticket.objects.create(
            user=self.user,
            flight=self.flight,
            seat_number=seat_number,
            status=status,
            price=self.flight.price,
        )
        # created_at has auto_now_add=True, so it must be backdated separately.
        Ticket.objects.filter(pk=ticket.pk).update(created_at=created_at)
        ticket.refresh_from_db()
        return ticket

    def test_old_pending_tickets_are_cancelled(self):
        now = timezone.now()
        old_ticket = self.make_ticket(1, now - timedelta(minutes=20))
        recent_ticket = self.make_ticket(2, now - timedelta(minutes=5))

        count = cancel_expired_tickets()

        old_ticket.refresh_from_db()
        recent_ticket.refresh_from_db()

        self.assertEqual(count, 1)
        self.assertEqual(old_ticket.status, "cancelled")
        self.assertEqual(recent_ticket.status, "pending")

    def test_already_booked_tickets_are_left_alone_even_if_old(self):
        now = timezone.now()
        booked = self.make_ticket(3, now - timedelta(minutes=30), status="booked")

        count = cancel_expired_tickets()
        booked.refresh_from_db()

        self.assertEqual(count, 0)
        self.assertEqual(booked.status, "booked")
