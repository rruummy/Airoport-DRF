from rest_framework import viewsets, generics, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from tickets.serializers import TicketSerializer, BookTicketSerializer, MyTicketSerializer
from django.db import transaction
from tickets.filters import TicketFilter
from tickets.models import Ticket
from payment.models import Payment
from payment.services import StripeService
from rest_framework.response import Response
from user.permissions import IsAdminRole, IsUserRole

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
    viewsets.GenericViewSet):

    permission_classes = [IsUserRole]

    def get_serializer_class(self):
        if self.action == "list":
            return MyTicketSerializer
        return BookTicketSerializer

    def get_queryset(self):
        return (
            Ticket.objects
            .filter(user=self.request.user)
            .select_related("flight")
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flight = serializer.validated_data["flight"]

        with transaction.atomic():
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