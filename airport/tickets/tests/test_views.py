from types import SimpleNamespace
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase

from test_factories import create_flight, create_user, create_profile
from payment.models import Payment
from tickets.models import Ticket


class BookTicketViewTests(APITestCase):
    def setUp(self):
        self.flight = create_flight()
        self.user = create_user(email="flyer@example.com", role="user", is_active=True)
        create_profile(self.user, raw_passport="AB123456")
        self.url = reverse("book-tickets-list")

    @patch("tickets.views.StripeService.create_checkout")
    def test_booking_creates_ticket_and_payment_and_returns_checkout_url(self, mock_checkout):
        mock_checkout.return_value = SimpleNamespace(
            id="cs_test_1", url="https://stripe.test/pay"
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {
            "flight": self.flight.id,
            "seat_number": 4,
            "passport_number": "AB123456",
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["checkout_url"], "https://stripe.test/pay")

        ticket = Ticket.objects.get(id=response.data["ticket_id"])
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.status, "pending")
        self.assertEqual(ticket.price, self.flight.price)

        payment = Payment.objects.get(id=response.data["payment_id"])
        self.assertEqual(payment.ticket, ticket)
        self.assertEqual(payment.price, ticket.price)

    def test_wrong_passport_number_is_rejected_with_400(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.url, {
            "flight": self.flight.id,
            "seat_number": 4,
            "passport_number": "WRONG000",
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Ticket.objects.count(), 0)

    def test_unverified_user_cannot_book(self):
        unverified = create_user(email="unverified3@example.com", role="user", is_active=False)
        self.client.force_authenticate(user=unverified)

        response = self.client.post(self.url, {
            "flight": self.flight.id,
            "seat_number": 4,
            "passport_number": "AB123456",
        })

        self.assertEqual(response.status_code, 403)

    @patch("tickets.views.StripeService.create_checkout")
    def test_user_only_sees_their_own_tickets_in_list(self, mock_checkout):
        mock_checkout.return_value = SimpleNamespace(id="cs_x", url="https://stripe.test/pay")
        other_user = create_user(email="otherflyer@example.com", role="user", is_active=True)
        create_profile(other_user, raw_passport="CD654321")

        self.client.force_authenticate(user=other_user)
        self.client.post(self.url, {
            "flight": self.flight.id,
            "seat_number": 5,
            "passport_number": "CD654321",
        })

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 0)
