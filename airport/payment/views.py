import stripe
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from payment.models import Payment
from tickets.models import Ticket
from user.permissions import IsAdminRole, IsVerifiedUser, IsAdminOrReadOnly
from payment.services import StripeService


stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutView(APIView):
    permission_classes = [IsVerifiedUser]

    def post(self, request, pk):
        payment = get_object_or_404(
            Payment,
            pk=pk,
            user=request.user,
        )

        if payment.status == "succeeded":
            return Response(
                {"detail": "Payment already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = StripeService.create_checkout(payment)

        return Response(
            {
                "checkout_url": session.url,
                "session_id": session.id,
            }
        )

class StripeWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):

        payload = request.body
        sig_header = request.headers.get("Stripe-Signature")

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError:
            return HttpResponse(status=400)

        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":

            session = event["data"]["object"]

            payment_id = session["metadata"]["payment_id"]

            payment = Payment.objects.get(pk=payment_id)

            payment.status = "succeeded"
            payment.stripe_payment_intent_id = session["payment_intent"]

            payment.save()

            ticket = payment.ticket
            ticket.status = "paid"
            ticket.save()

        elif event["type"] == "payment_intent.payment_failed":

            intent = event["data"]["object"]

            payment = Payment.objects.get(
                stripe_payment_intent_id=intent["id"]
            )

            payment.status = "failed"
            payment.save()

        return HttpResponse(status=200)

class PaymentSuccessView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"message": "Payment successful"})


class PaymentCancelView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"message": "Payment cancelled"})