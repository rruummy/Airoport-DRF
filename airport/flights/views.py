from rest_framework import viewsets, permissions, generics
from flights.models import Country, Airline, Airplane, Airport, Flight
from user.permissions import IsAdminRole, IsUserRole
from flights.serializers import CountrySerializer

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminRole]

