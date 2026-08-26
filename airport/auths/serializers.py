import hashlib
import secrets
from utils import hash_passport

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from django.utils import timezone
from datetime import date
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User, UserProfile
from emails.models import EmailVerificationCode, PasswordResetCode
import re


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField()

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

class RegisterSerializer(serializers.ModelSerializer):
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email already exists."
            )
        return value
    def validate_birth_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("The birthdate cannot be the future")
        return value
    def validate_first_name(self, value):
        if not re.fullmatch(r"[A-Za-z]+", value):
            raise serializers.ValidationError("Only uppercase and lowercase Latin letters are allowed")
        return value

    def validate_last_name(self, value):
        if not re.fullmatch(r"[A-Za-z]+", value):
            raise serializers.ValidationError("Only uppercase and lowercase Latin letters are allowed")
        return value
    
    def validate_passport_number(self, value):
        cleaned_value = re.sub(r"[\s\-]", "", value).upper()

        is_digit_passport = re.fullmatch(r"\d{9}", cleaned_value)
        is_booklet_passport = re.fullmatch(r"[A-Z]{2}\d{6}", cleaned_value)
        is_international_passport = re.fullmatch(r"[A-Z0-9]{6,9}", cleaned_value)

        if not (is_digit_passport or is_booklet_passport or is_international_passport):
            raise serializers.ValidationError("Invalid passport data format.")

        passport_hash = hash_passport(cleaned_value)

        if UserProfile.objects.filter(passport_number=passport_hash).exists():
            raise serializers.ValidationError(
                "User with this passport number already exists."
            )

        return cleaned_value
    
    def validate(self, attrs):
        if attrs["first_name"] == attrs["last_name"]:
            raise serializers.ValidationError("First name and last name cannot be the same.")
        return attrs
    
    def validate_password(self, value):
        validate_password(value, self.context['request'].user)
        return value

    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    passport_number = serializers.CharField(write_only=True)
    birth_date = serializers.DateField(write_only=True)
    bio = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "passport_number",
            "birth_date",
            "bio",
        )

    def create(self, validated_data):
        with transaction.atomic():
            profile_data = {
                "first_name": validated_data.pop("first_name"),
                "last_name": validated_data.pop("last_name"),
                "passport_number": hash_passport(validated_data.pop("passport_number")),
                "birth_date": validated_data.pop("birth_date"),
                "bio": validated_data.pop("bio"),}
            
            password = validated_data.pop("password")
            user = User(**validated_data)
            user.is_active = False
            user.set_password(password)
            user.save()

            UserProfile.objects.create(
                user=user,
                **profile_data)
            
            return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("Your email is not verified")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
        
        if not user.is_active:
            raise serializers.ValidationError("Email is not verified")
        self.user = user
        return value

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        code = attrs["code"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or code.")

        try:
            reset = user.password_reset
        except PasswordResetCode.DoesNotExist:
            raise serializers.ValidationError("Reset code not found.")

        if reset.expires_at < timezone.now():
            raise serializers.ValidationError("Reset code has expired.")

        code_hash = hashlib.sha256(code.encode()).hexdigest()

        if not secrets.compare_digest(code_hash, reset.code_hash):
            raise serializers.ValidationError("Invalid reset code.")

        validate_password(attrs["new_password"], user)

        attrs["user"] = user
        attrs["reset"] = reset

        return attrs