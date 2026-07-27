from django.utils import timezone
from rest_framework import serializers
from utils import hash_passport
from tickets.models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("flight", "seat_number")


class BookTicketSerializer(serializers.ModelSerializer):
    passport_number = serializers.CharField(write_only=True)

    class Meta:
        model = Ticket
        fields = ("flight", "seat_number", "passport_number")

    def validate(self, attrs):
        flight = attrs["flight"]
        seat = attrs["seat_number"]
        profile = self.context["request"].user.profile

        if Ticket.objects.filter(
            flight=flight,
            seat_number=seat,
        ).exists():
            raise serializers.ValidationError({"seat_number": "This seat is already booked."})

        if seat < 1 or seat > flight.airplane.capacity:
            raise serializers.ValidationError({"seat_number": "Seat number is out of range."})

        if (flight.departure_time <= timezone.now()
            or flight.status in ("departed", "cancelled")):
            raise serializers.ValidationError({"flight": "This flight has already departed or was cancelled."})

        if profile.passport_number != hash_passport(attrs["passport_number"]):
            raise serializers.ValidationError({"passport_number": "Passport number is incorrect."})
    
        return attrs

    def create(self, validated_data):
        validated_data.pop("passport_number", None)
        return Ticket.objects.create(**validated_data)