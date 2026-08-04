from django.shortcuts import redirect
from user.serializers import UserProfileSerializer, PasswordChangeSerializer
from rest_framework import generics
from django.http import request

from user.permissions import IsUserRole, IsNotCompletedProfile, IsCompletedProfile

def root_redirect_view(request):
    return redirect("swagger-ui")

class UserProfileGetView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsUserRole]

    def get_object(self):
        return self.request.user.profile

class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsNotCompletedProfile, IsUserRole]
    http_method_names = ["patch"]

    def get_object(self):
        return self.request.user.profile

    def perform_update(self, serializer):
        profile = serializer.save()

        if (
            profile.first_name
            and profile.last_name
            and profile.passport_number
            and profile.birth_date
        ):
            profile.user.is_profile_completed = True
            profile.user.save(update_fields=["is_profile_completed"])

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


        
