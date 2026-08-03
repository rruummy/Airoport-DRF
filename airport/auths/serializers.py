import hashlib
import secrets

from django.utils import timezone
from rest_framework import serializers

from user.models import User
from auths.models import EmailVerificationCode


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        email = attrs["email"]
        code = attrs["code"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or verification code")

        if user.is_active:
            raise serializers.ValidationError("This account is already verified")

        try:
            verification = user.email_verification
        except EmailVerificationCode.DoesNotExist:
            raise serializers.ValidationError("Verification code not found")

        if verification.expires_at < timezone.now():
            raise serializers.ValidationError("Verification code has expired")

        code_hash = hashlib.sha256(code.encode()).hexdigest()

        if not secrets.compare_digest(code_hash, verification.code_hash):
            raise serializers.ValidationError("Invalid verification code")

        attrs["user"] = user

        return attrs

class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")

        if user.is_active:
            raise serializers.ValidationError("Email is already verified")

        self.user = user
        return value