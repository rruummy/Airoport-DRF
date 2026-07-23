from django.shortcuts import render
from user.models import User
from user.serializers import UserSerializer, RegisterSerializer
from rest_framework import viewsets, permissions, generics

class UserView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
