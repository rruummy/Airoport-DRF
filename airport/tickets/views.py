from rest_framework import viewsets, permissions, generics, mixins
from tickets.serializers import TicketSerializer, BookTicketSerializer
from tickets.models import Ticket

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAdminUser]

class BookTicketView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet):
    serializer_class = BookTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        flight = serializer.validated_data["flight"]

        serializer.save(
            user=self.request.user,
            price=flight.price)