from rest_framework import serializers 
from flights.models import Flight, Airport, Airplane, Airline, Country
import re

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'title', 'code')

class AirportSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    class Meta:
        model = Airport
        fields = ('id', 'name', 'country')

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ('id', 'name', 'country')

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
        # .remove() відв'язує вказані аеропорти від авіакомпанії
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
    def validate(self, attrs):
        dep_time = attrs.get('departure_time', getattr(self.instance, 'departure_time', None))
        arr_time = attrs.get('arrival_time', getattr(self.instance, 'arrival_time', None))
        if attrs['departure_airport'] == attrs['arrival_airport']:
            raise serializers.ValidationError("The departure and arrival airports cannot be same")
        if arr_time < dep_time:
            raise serializers.ValidationError("The arrival time must be after deparute time")
        return attrs
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("The price cannot equel 0 or less")
        return value

    departure_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    arrival_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())
    airline = serializers.PrimaryKeyRelatedField(queryset=Airline.objects.all())

    class Meta:
        model = Flight
        fields = ('id',
                  'departure_airport',
                  'arrival_airport',
                  'departure_time',
                  'arrival_time',
                  'airplane',
                  'airline',
                  'price',
                  'status')
    