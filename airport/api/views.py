from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from api.serializers import TicketSerializer, FlightSerializer, AirplaneSerializer, AirlineSerializer, CountrySerializer, AirportSerializer
from api.models.booking_models import Ticket, Flight
from api.models.aviation_models import Airplane, Airline
from api.models.geography_models import Country, Airport

from rest_framework.views import APIView

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
 
class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
 
class AirlineViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
 
class AirplaneSerializerViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
 
class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
 
class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
 





