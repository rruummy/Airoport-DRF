from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from test_factories import create_flight, create_user, create_profile
from tickets.models import Ticket
from payment.models import Payment


class CancelTicketTests(APITestCase):
    def setUp(self):
        self.flight = create_flight(departure_time=timezone.now() + timedelta(days=2))
        self.user = create_user(email="canceller@example.com", role="user", is_active=True)
        create_profile(self.user, raw_passport="AB123456")
        self.client.force_authenticate(user=self.user)

    def cancel_url(self, ticket_id):
        return reverse("book-tickets-cancel", args=[ticket_id])

    def make_ticket(self, status="pending", user=None):
        return Ticket.objects.create(
            user=user or self.user,
            flight=self.flight,
            seat_number=1,
            status=status,
            price=self.flight.price,
        )

    def test_pending_ticket_can_be_cancelled(self):
        ticket = self.make_ticket(status="pending")

        response = self.client.post(self.cancel_url(ticket.id))

        ticket.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ticket.status, "cancelled")

    def test_cancelling_frees_the_seat_for_a_new_booking(self):
        ticket = self.make_ticket(status="booked")
        self.client.post(self.cancel_url(ticket.id))

        # The unique constraint only blocks pending/booked/paid tickets,
        # so a fresh booking for the same seat must now succeed.
        second = Ticket.objects.create(
            user=self.user, flight=self.flight, seat_number=1,
            status="pending", price=self.flight.price,
        )
        self.assertIsNotNone(second.pk)

    def test_already_cancelled_ticket_cannot_be_cancelled_again(self):
        ticket = self.make_ticket(status="cancelled")

        response = self.client.post(self.cancel_url(ticket.id))

        self.assertEqual(response.status_code, 400)

    def test_used_ticket_cannot_be_cancelled(self):
        ticket = self.make_ticket(status="used")

        response = self.client.post(self.cancel_url(ticket.id))

        self.assertEqual(response.status_code, 400)

    def test_ticket_for_departed_flight_cannot_be_cancelled(self):
        departed_flight = create_flight(
            departure_time=timezone.now() - timedelta(hours=2),
            arrival_time=timezone.now() - timedelta(hours=1),
        )
        ticket = Ticket.objects.create(
            user=self.user, flight=departed_flight, seat_number=1,
            status="booked", price=departed_flight.price,
        )

        response = self.client.post(self.cancel_url(ticket.id))

        ticket.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ticket.status, "booked")

    def test_cannot_cancel_someone_elses_ticket(self):
        other_user = create_user(email="stranger@example.com", role="user", is_active=True)
        ticket = self.make_ticket(status="pending", user=other_user)

        response = self.client.post(self.cancel_url(ticket.id))

        self.assertEqual(response.status_code, 404)

    @patch("tickets.views.StripeService.refund_payment")
    def test_cancelling_a_paid_ticket_triggers_a_refund(self, mock_refund):
        ticket = self.make_ticket(status="paid")
        payment = Payment.objects.create(
            ticket=ticket, user=self.user, price=ticket.price,
            status="succeeded", stripe_payment_intent_id="pi_test_123",
        )

        response = self.client.post(self.cancel_url(ticket.id))

        payment.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payment.status, "refunded")
        mock_refund.assert_called_once_with(payment)

    @patch("tickets.views.StripeService.refund_payment")
    def test_refund_failure_still_cancels_the_ticket_but_warns(self, mock_refund):
        import stripe
        mock_refund.side_effect = stripe.error.StripeError("boom")

        ticket = self.make_ticket(status="paid")
        payment = Payment.objects.create(
            ticket=ticket, user=self.user, price=ticket.price,
            status="succeeded", stripe_payment_intent_id="pi_test_456",
        )

        response = self.client.post(self.cancel_url(ticket.id))
        ticket.refresh_from_db()
        payment.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ticket.status, "cancelled")
        self.assertEqual(payment.status, "succeeded")  # left untouched for manual follow-up
        self.assertIn("warning", response.data)

    @patch("tickets.views.StripeService.refund_payment")
    def test_cancelling_an_unpaid_ticket_does_not_call_stripe(self, mock_refund):
        ticket = self.make_ticket(status="pending")

        self.client.post(self.cancel_url(ticket.id))

        mock_refund.assert_not_called()
