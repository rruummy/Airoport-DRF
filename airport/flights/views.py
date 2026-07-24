from rest_framework import viewsets, permissions, generics
from flights.models import Country, Airline, Airplane, Airport, Flight
from user.permissions import IsAdminRole, IsUserRole
from flights.serializers import CountrySerializer, AirportSerializer

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminRole]

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminRole]
