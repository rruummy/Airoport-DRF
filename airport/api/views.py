from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from serializers import TicketSerializer
from models.ticket_model import Ticket

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class ExampleView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)

class UserViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Ticket.objects.all()
        serializer = TicketSerializer(queryset, many=True)
        return Response(serializer.data)

    def retieve(self, request, pk=None):
        queryset = Ticket.objects.all()




