from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from api.serializers import TicketSerializer
from api.models.booking_models import Ticket

from rest_framework.views import APIView

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer





