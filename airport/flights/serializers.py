from rest_framework import serializers 
from flights.models import Flight, Airport, Airplane, Airline, Country
import re

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'title', 'code')

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ('id', 'name', 'country', 'city')

class AirlineSerializer(serializers.ModelSerializer):
    airports = AirportSerializer(source='airport', many=True, read_only=True)
    class Meta:
        model = Airline
        fields = ('id','name', 'airports')

class AirlineAirportSerializer(serializers.Serializer):
    airport_ids = serializers.PrimaryKeyRelatedField(
        queryset=Airport.objects.all(),
        many=True,
        write_only=True
    )

    def add_airports(self, airline):
        airports = self.validated_data['airport_ids']
        airline.airport.add(*airports)
        return airline

    def remove_airports(self, airline):
        airports = self.validated_data['airport_ids']
        airline.airport.remove(*airports)
        return airline

class AirplaneSerializer(serializers.ModelSerializer):
    def validate_capacity(self, value):
        if not (19 < value < 800):
            raise serializers.ValidationError("The capacity shoulde be between 20 to 800.")
        return value

    airline = serializers.PrimaryKeyRelatedField(queryset=Airline.objects.all())
    class Meta:
        model = Airplane
        fields = ('id', 'model', 'capacity', 'airline')

class FlightSerializer(serializers.ModelSerializer):
    departure_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    arrival_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())
    airline = serializers.PrimaryKeyRelatedField(queryset=Airline.objects.all())

    departure_time = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M",
        input_formats=[
            "%d.%m.%Y %H:%M",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ],
    )

    arrival_time = serializers.DateTimeField(
        format="%d.%m.%Y %H:%M",
        input_formats=[
            "%d.%m.%Y %H:%M",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%fZ",
        ],
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_airport",
            "arrival_airport",
            "departure_time",
            "arrival_time",
            "airplane",
            "airline",
            "price",
            "status",
        )

    def validate(self, attrs):
        dep_time = attrs.get("departure_time", getattr(self.instance, "departure_time", None))
        arr_time = attrs.get("arrival_time",  getattr(self.instance, "arrival_time", None))
        departure_airport = attrs.get("departure_airport", getattr(self.instance, "departure_airport", None))
        arrival_airport = attrs.get("arrival_airport",getattr(self.instance, "arrival_airport", None))

        if departure_airport == arrival_airport:
            raise serializers.ValidationError("The departure and arrival airports cannot be the same")
        if arr_time < dep_time:
            raise serializers.ValidationError("The arrival time must be after the departure time")

        return attrs

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("The price cannot be equal to or less than 0")
        return value

class WeatherSerializer(serializers.Serializer):
    city = serializers.CharField()
    forecast_time = serializers.DateTimeField()

    temperature = serializers.FloatField()
    feels_like = serializers.FloatField()
    humidity = serializers.IntegerField()
    description = serializers.CharField()
    wind_speed = serializers.FloatField()
