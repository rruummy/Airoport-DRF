from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from test_factories import create_flight, create_user
from tickets.models import Ticket
from payment.models import Payment
from payment.services import StripeService


class StripeServiceTests(TestCase):
    def setUp(self):
        self.flight = create_flight()
        self.user = create_user(email="payer@example.com")
        self.ticket = Ticket.objects.create(
            user=self.user, flight=self.flight, seat_number=1,
            status="pending", price=self.flight.price,
        )
        self.payment = Payment.objects.create(
            ticket=self.ticket, user=self.user, price=self.ticket.price,
        )

    @patch("payment.services.stripe.checkout.Session.create")
    def test_create_checkout_stores_session_id_and_returns_session(self, mock_create):
        mock_create.return_value = SimpleNamespace(id="cs_test_123", url="https://stripe.test/pay")

        session = StripeService.create_checkout(self.payment)

        self.payment.refresh_from_db()
        self.assertEqual(session.url, "https://stripe.test/pay")
        self.assertEqual(self.payment.stripe_checkout_session_id, "cs_test_123")

    @patch("payment.services.stripe.checkout.Session.create")
    def test_create_checkout_sends_amount_in_cents(self, mock_create):
        mock_create.return_value = SimpleNamespace(id="cs_test_456", url="https://stripe.test/pay")

        StripeService.create_checkout(self.payment)

        _, kwargs = mock_create.call_args
        unit_amount = kwargs["line_items"][0]["price_data"]["unit_amount"]
        self.assertEqual(unit_amount, int(self.payment.price * 100))
