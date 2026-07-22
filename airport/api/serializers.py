from rest_framework import serializers

class TicketSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField()
    flight = serializers.IntegerField()
    seat_number = serializers.IntegerField()
    status = serializers.CharField()
