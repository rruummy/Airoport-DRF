from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from flights.filters import FlightFilter
from flights.filters import AirportFilter, AirlineFilter
from flights.models import Country, Airline, Airplane, Airport, Flight
from user.permissions import IsAdminRole, IsUserRole, IsAdminOrReadOnly
from flights.serializers import (CountrySerializer,
                                 AirportSerializer,
                                 AirlineSerializer,
                                 AirlineAirportSerializer,
                                 AirplaneSerializer,
                                 FlightSerializer,
                                 )

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AirportFilter

    search_fields = ['name',]

class AirlinesViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    queryset = Airline.objects.all().prefetch_related('airport')
    serializer_class = AirlineSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = AirlineFilter

    search_fields = ['name', 'country']

    @action(detail=True, methods=['post'], url_path='add-airport')
    def add_airports(self, request, pk=None):
        airline = self.get_object()
        serializer = AirlineAirportSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.add_airports(airline)
            return Response(
                AirlineSerializer(airline).data, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='remove-airport')
    def remove_airports(self, request, pk=None):
        airline = self.get_object()
        serializer = AirlineAirportSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.remove_airports(airline)
            return Response(
                AirlineSerializer(airline).data, 
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminOrReadOnly]

class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_class = FlightFilter

    search_fields = ["airline__name"]

    ordering_fields = ["price", "departure_time"]