from rest_framework import viewsets, permissions, generics, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.core.cache import cache
from flights.filters import FlightFilter
from flights.filters import AirportFilter, AirlineFilter
from flights.models import Country, Airline, Airplane, Airport, Flight
from flights.cache import get_flight_list_cache_version, bump_flight_list_cache_version
from user.permissions import IsAdminRole, IsVerifiedUser, IsAdminOrReadOnly
from flights.serializers import (CountrySerializer,
                                 AirportSerializer,
                                 AirlineSerializer,
                                 AirlineAirportSerializer,
                                 AirplaneSerializer,
                                 FlightSerializer,
                                 WeatherSerializer,
                                 )
from flights.weather import get_weather_forecast
from django.shortcuts import get_object_or_404

FLIGHT_LIST_CACHE_TTL = getattr(settings, "FLIGHT_LIST_CACHE_TTL", 60)


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

    def list(self, request, *args, **kwargs):
        # The flight list is read far more often than it changes and isn't
        # user-specific, so it's a good candidate for a short-lived cache.
        # The cache key is versioned (see flights.cache) rather than
        # relying on delete_pattern, since the built-in Redis cache
        # backend doesn't support pattern deletes.
        version = get_flight_list_cache_version()
        cache_key = f"flights:list:v{version}:{request.get_full_path()}"

        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=FLIGHT_LIST_CACHE_TTL)

        return response

    def perform_create(self, serializer):
        super().perform_create(serializer)
        bump_flight_list_cache_version()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        bump_flight_list_cache_version()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        bump_flight_list_cache_version()

class FlightWeatherView(generics.GenericAPIView):
    serializer_class = WeatherSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk):
        flight = get_object_or_404(Flight, pk=pk)
        weather = get_weather_forecast(
            city=flight.arrival_airport.city,
            arrival_time=flight.arrival_time,
        )

        if weather is None:
            return Response(
                {
                    "detail": (
                        f"Weather forecast not found for "
                        f"city '{flight.arrival_airport.city}'."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = WeatherSerializer(weather)

        return Response(serializer.data)