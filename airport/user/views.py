from django.shortcuts import redirect
from rest_framework.response import Response
from user.models import User
from user.serializers import (RegisterSerializer,
                              UserProfileSerializer,
                              PasswordChangeSerializer,
                              BalanceSerializer)
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from django.http import request
from django.db import transaction
from user.permissions import IsAdminRole, IsUserRole

def root_redirect_view(request):
    if request.user.is_authenticated:
        return redirect("swagger-ui")
    return redirect("register")

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsUserRole]
    http_method_names = ['patch']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'detail': 'Password was changed'},
                        status=status.HTTP_200_OK)

class UserProfileGetView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsUserRole]

    def get_object(self):
        return self.request.user.profile

class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsUserRole]
    http_method_names = ["patch"]

    def get_object(self):
        return self.request.user.profile


        
