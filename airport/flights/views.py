from rest_framework import viewsets, permissions, generics
from flights.models import Country, Airline, Airplane, Airport, Flight
from user.permissions import IsAdminRole, IsUserRole, IsAdminOrReadOnly
from flights.serializers import (CountrySerializer,
                                 AirportSerializer,
                                 AirlineSerializer,
                                 )

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrReadOnly]

class AirlinesViewSet(viewsets.ModelViewSet):
    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [IsAdminOrReadOnly]

"""class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminRole]"""