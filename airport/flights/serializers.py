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
