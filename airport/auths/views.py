from rest_framework import generics, status
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.db import transaction

from auths.utils import send_verification_code, verify_google_token, send_password_reset_code
from emails.utils import send_password_successfully_updated_email
from auths.serializers import (VerifyEmailSerializer,
                               ResendVerificationSerializer,
                               RegisterSerializer,
                               LoginSerializer,
                               GoogleLoginSerializer,
                               ForgotPasswordSerializer,
                               ResetPasswordSerializer)
from urllib.parse import urlencode
import requests

from user.permissions import IsVerifiedUser
from user.models import User, UserProfile



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

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = serializer.save()

            send_verification_code(user)

            return Response(
                {
                    "message": (
                        "Registration successful",
                        "Verification code has been sent to your email"
                    )
                },
                status=status.HTTP_201_CREATED,
            )

class GoogleLoginView(GenericAPIView):
    serializer_class = GoogleLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        try:
            google_data = verify_google_token(token)
        except Exception:
            return Response(
                {"detail": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = google_data["email"]

        with transaction.atomic():
            try:
                user = User.objects.get(email=email)
                created = False

            except User.DoesNotExist:
                base_username = email.split("@")[0]
                username = base_username

                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User.objects.create(
                    username=username,
                    email=email,
                    is_active=True,
                    is_profile_completed=False,
                )
                created = True

                UserProfile.objects.create(
                    user=user,
                    first_name=google_data.get("given_name", ""),
                    last_name=google_data.get("family_name", ""),
                    bio="",
                )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "created": created,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

class GoogleAuthUrlView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URL,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }

        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth?"
            + urlencode(params)
        )

        return Response({"authorization_url": auth_url})

class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.query_params.get("code")

        if not code:
            return Response(
                {"detail": "Code is missing"},
                status=400,
            )

        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URL,
                "grant_type": "authorization_code",
            },
        )

        return Response(token_response.json())

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)

class ForgotPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        send_password_reset_code(serializer.user)

        return Response(
            {"message": "Password reset code has been sent."}
        )

class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        reset = serializer.validated_data["reset"]

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        send_password_successfully_updated_email(user)

        reset.delete()
        return Response(
            {"message": "Password changed."}
        )
