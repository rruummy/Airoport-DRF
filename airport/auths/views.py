from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from auths.utils import send_verification_code
from auths.serializers import VerifyEmailSerializer, ResendVerificationSerializer


class VerifyEmailView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        user.is_active = True
        user.save(update_fields=["is_active"])

        user.email_verification.delete()

        return Response(
            {"message": "Email successfully verified"},
            status=status.HTTP_200_OK
            )

class ResendVerificationView(generics.GenericAPIView):
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        send_verification_code(serializer.user)

        return Response(
            {"message": "Verification code sent successfully."},
            status=status.HTTP_200_OK,
        )