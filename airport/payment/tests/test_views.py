from unittest.mock import patch
from types import SimpleNamespace

from django.urls import reverse
from rest_framework.test import APITestCase

from test_factories import create_flight, create_user
from tickets.models import Ticket
from payment.models import Payment


class CreateCheckoutViewTests(APITestCase):
    def setUp(self):
        self.flight = create_flight()
        self.user = create_user(email="checkout@example.com", role="user", is_active=True)
        self.ticket = Ticket.objects.create(
            user=self.user, flight=self.flight, seat_number=1,
            status="pending", price=self.flight.price,
        )
        self.payment = Payment.objects.create(
            ticket=self.ticket, user=self.user, price=self.ticket.price,
        )

    @patch("payment.views.StripeService.create_checkout")
    def test_authenticated_owner_can_create_checkout(self, mock_create_checkout):
        mock_create_checkout.return_value = SimpleNamespace(
            id="cs_test_1", url="https://stripe.test/pay"
        )
        self.client.force_authenticate(user=self.user)

        url = reverse("create-checkout", args=[self.payment.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["checkout_url"], "https://stripe.test/pay")

    def test_already_succeeded_payment_cannot_be_re_checked_out(self):
        self.payment.status = "succeeded"
        self.payment.save(update_fields=["status"])
        self.client.force_authenticate(user=self.user)

        url = reverse("create-checkout", args=[self.payment.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 400)

    def test_anonymous_user_is_rejected(self):
        url = reverse("create-checkout", args=[self.payment.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 401)


class StripeWebhookViewTests(APITestCase):
    def setUp(self):
        self.flight = create_flight()
        self.user = create_user(email="webhook@example.com")
        self.ticket = Ticket.objects.create(
            user=self.user, flight=self.flight, seat_number=1,
            status="pending", price=self.flight.price,
        )
        self.payment = Payment.objects.create(
            ticket=self.ticket, user=self.user, price=self.ticket.price,
        )
        self.url = reverse("stripe-webhook")

    def post_event(self, event):
        with patch("payment.views.stripe.Webhook.construct_event", return_value=event):
            return self.client.post(
                self.url,
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test-signature",
            )

    @patch("payment.views.generate_ticket_pdf_task.delay")
    def test_checkout_completed_marks_payment_and_ticket_paid(self, mock_delay):
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"payment_id": str(self.payment.id)},
                    "payment_intent": "pi_test_123",
                }
            },
        }
        response = self.post_event(event)

        self.payment.refresh_from_db()
        self.ticket.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.payment.status, "succeeded")
        self.assertEqual(self.payment.stripe_payment_intent_id, "pi_test_123")
        self.assertEqual(self.ticket.status, "paid")
        mock_delay.assert_called_once_with(self.ticket.id)

    @patch("payment.views.generate_ticket_pdf_task.delay")
    def test_checkout_completed_is_idempotent(self, mock_delay):
        self.payment.status = "succeeded"
        self.payment.save(update_fields=["status"])

        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"payment_id": str(self.payment.id)},
                    "payment_intent": "pi_test_123",
                }
            },
        }
        response = self.post_event(event)

        self.assertEqual(response.status_code, 200)
        mock_delay.assert_not_called()

    def test_payment_failed_marks_payment_failed(self):
        self.payment.stripe_payment_intent_id = "pi_test_999"
        self.payment.save(update_fields=["stripe_payment_intent_id"])

        event = {
            "type": "payment_intent.payment_failed",
            "data": {"object": {"id": "pi_test_999"}},
        }
        response = self.post_event(event)
        self.payment.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.payment.status, "failed")

    def test_invalid_signature_returns_400(self):
        with patch(
            "payment.views.stripe.Webhook.construct_event",
            side_effect=ValueError("bad payload"),
        ):
            response = self.client.post(
                self.url,
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="bad-signature",
            )
        self.assertEqual(response.status_code, 400)
