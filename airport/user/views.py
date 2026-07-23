from django.shortcuts import render
from user.models import User
from user.serializers import UserSerializers
from rest_framework import viewsets, permissions

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    permission_classes = [permissions.IsAuthenticated]
