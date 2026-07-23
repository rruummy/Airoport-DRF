from rest_framework import viewsets, permissions
from tickets.serializers import TicketSerializer
from tickets.models import Ticket
from flights.views import FlightViewSet, AirportViewSet, AirlineViewSet, AirplaneSerializerViewSet, CountryViewSet



class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
