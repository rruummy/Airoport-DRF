from rest_framework import serializers 
from flights.models import Flight, Airport, Airplane, Airline, Country
import re

class CountrySerializer(serializers.ModelSerializer):
    def validate_code(self, value):
        if not re.fullmatch(r"^[A-Z]{2}$", value):
            raise serializers.ValidationError("Invalid code. Country code should have only 2 big letter #UA")
        if Country.objects.filter(code=value).exists():
            raise serializers.ValidationError("Country with this code already exist")
        if Country.objects.filter(title=value).exists():
            raise serializers.ValidationError("Country with this title already exist")
        return value
    
    class Meta:
        model = Country
        fields = ('id', 'title', 'code')

class AirportSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())
    class Meta:
        model = Airport
        fields = ('id', 'name', 'city', 'country')

class AirlineSerializer(serializers.ModelSerializer):
    airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    class Meta:
        model = Airline
        fields = ('id','name', 'airport')

"""class AirplaneSerializer(serializers.ModelSerializer):
    def validate_capacity(self, value):
        if 20 > value > 800:
            raise serializers.ValidationError("The capacity shoulde be between 20 to 800.")
    airline = serializers.PrimaryKeyRelatedField(queryset=Airline.objects.all())
    class Meta:
        model = Airplane
        fields = ('id', 'model', 'capacity', 'airline')"""