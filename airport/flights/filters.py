import django_filters
from flights.models import Airport, Airline, Flight

class AirportFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(
        field_name='country__title',
        lookup_expr='icontains',
    )
    class Meta:
        model = Airport
        fields = ['country', 'city']

class AirlineFilter(django_filters.FilterSet):
    country = django_filters.CharFilter(
        field_name='airport__country__title',
        lookup_expr='icontains',
    )
    class Meta:
        model = Airline
        fields = ['name',]

class FlightFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )

    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )

    departure_after = django_filters.DateTimeFilter(
        field_name="departure_time",
        lookup_expr="gte"
    )

    departure_before = django_filters.DateTimeFilter(
        field_name="departure_time",
        lookup_expr="lte"
    )

    arrival_after = django_filters.DateTimeFilter(
        field_name="arrival_time",
        lookup_expr="gte"
    )

    arrival_before = django_filters.DateTimeFilter(
        field_name="arrival_time",
        lookup_expr="lte"
    )

    class Meta:
        model = Flight
        fields = [
            "departure_airport__country__title",
            "arrival_airport__country__title",
            "airline__name",
            "status",
        ]