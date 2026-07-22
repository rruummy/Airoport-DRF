from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from serializers import TicketSerializer
from models import Ticket

class UserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Ticket.objects.all()
        serializer = TicketSerializer(queryset, many=True)
        return Response(serializer.data)

    def retieve(self, request, pk=None):
        queryset = Ticket.objects.all()
        



