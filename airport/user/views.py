from django.shortcuts import redirect
from user.models import User
from user.serializers import RegisterSerializer, UserProfileSerializer
from rest_framework import viewsets, permissions, generics
from django.http import request

def root_redirect_view(request):
    if request.user.is_authenticated:
        return redirect("swagger-ui")
    return redirect("register")

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class UserProfileGetView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        return self.request.user.profile