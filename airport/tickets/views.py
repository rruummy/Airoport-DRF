import stripe
from rest_framework import viewsets, generics, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from tickets.serializers import TicketSerializer, BookTicketSerializer, MyTicketSerializer
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from tickets.filters import TicketFilter
from tickets.models import Ticket
from flights.models import Flight
from payment.models import Payment
from payment.services import StripeService
from rest_framework.response import Response
from rest_framework.views import APIView
from user.permissions import IsAdminRole, IsVerifiedUser
from tickets.services import generate_ticket_pdf

# Statuses that "hold" a seat - a ticket in one of these states blocks
# anyone else from booking the same seat on the same flight (this list
# mirrors the partial unique constraint on the Ticket model).
ACTIVE_TICKET_STATUSES = ("pending", "booked", "paid")

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAdminRole]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TicketFilter

    search_fields = ['status', 'flight', 'price']

class BookTicketView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsVerifiedUser]

    def get_serializer_class(self):
        if self.action == "list":
            return MyTicketSerializer

        return BookTicketSerializer

    def get_queryset(self):
        return (
            Ticket.objects
            .filter(user=self.request.user)
            .select_related(
                "flight",
                "flight__departure_airport",
                "flight__arrival_airport",
                "flight__airline",
            )
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flight = serializer.validated_data["flight"]
        seat_number = serializer.validated_data["seat_number"]

        with transaction.atomic():
            # Lock the flight row for the duration of this transaction.
            # Every concurrent booking attempt for the SAME flight has to
            # wait here for its turn, which closes the race window between
            # "is this seat free?" (checked in the serializer, before the
            # lock) and the INSERT below - without this, two requests could
            # both pass validation for the same seat and one of them would
            # only fail with a raw IntegrityError from the DB constraint.
            flight = Flight.objects.select_for_update().get(pk=flight.pk)

            seat_taken = Ticket.objects.filter(
                flight=flight,
                seat_number=seat_number,
                status__in=ACTIVE_TICKET_STATUSES,
            ).exists()

            if seat_taken:
                return Response(
                    {
                        "seat_number": (
                            "This seat was just booked by someone else. "
                            "Please choose another seat."
                        )
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            ticket = serializer.save(
                user=request.user,
                price=flight.price,
                status="pending",
            )

            payment = Payment.objects.create(
                ticket=ticket,
                user=request.user,
                price=ticket.price,
            )

        session = StripeService.create_checkout(payment)

        return Response(
            {
                "ticket_id": ticket.id,
                "payment_id": payment.id,
                "checkout_url": session.url,
                "message": "Ticket booked successfully. Proceed to payment.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, *args, **kwargs):
        ticket = self.get_object()  # already scoped to request.user

        if ticket.status not in ACTIVE_TICKET_STATUSES:
            return Response(
                {"detail": "This ticket cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ticket.flight.departure_time <= timezone.now():
            return Response(
                {"detail": "This flight has already departed, the ticket can no longer be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refund_warning = None

        with transaction.atomic():
            ticket.status = "cancelled"
            ticket.save(update_fields=["status"])

            payment = getattr(ticket, "payment", None)

            if payment is not None and payment.status == "succeeded":
                try:
                    StripeService.refund_payment(payment)
                except stripe.error.StripeError:
                    # The ticket is still cancelled (the seat is freed
                    # either way) - but the refund needs to be retried or
                    # handled manually, so we don't silently swallow this.
                    refund_warning = (
                        "Ticket cancelled, but the refund could not be "
                        "processed automatically. Our support team will "
                        "follow up."
                    )
                else:
                    payment.status = "refunded"
                    payment.save(update_fields=["status"])

        data = MyTicketSerializer(ticket).data
        if refund_warning:
            data["warning"] = refund_warning

        return Response(data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        ticket = self.get_object()

        if not ticket.pdf_file:
            return Response(
                {
                    "detail": "PDF ticket has not been generated yet."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        response = HttpResponse(
            ticket.pdf_file.read(),
            content_type="application/pdf",
        )

        response["Content-Disposition"] = (
            f'attachment; filename="ticket-{ticket.id}.pdf"'
        )

        return response

class TicketPDFView(APIView):
    permission_classes = [IsVerifiedUser]

    def get(self, request, ticket_id):
        ticket = Ticket.objects.select_related(
            "user",
            "flight",
            "flight__departure_airport",
            "flight__arrival_airport",
            "flight__airline",
        ).get(
            id=ticket_id,
            user=request.user,
        )
        user=request.user
        pdf = generate_ticket_pdf(ticket, user)

        response = HttpResponse(
            pdf,
            content_type="application/pdf",
        )

        response[
            "Content-Disposition"
        ] = f'attachment; filename="ticket-{ticket.id}.pdf"'

        return response