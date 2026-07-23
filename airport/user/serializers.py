from rest_framework import serializers
from user.models import User, UserProfile
from django.contrib.auth.password_validation import validate_password
import re

class RegisterSerializer(serializers.ModelSerializer):
    def validate_age(self, value):
        if value > 120:
            raise serializers.ValidationError("The age cannot be greater 120")
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
        if not re.fullmatch(r"[A-Z]{2}\d{8}", value):
            raise serializers.ValidationError("Password number should have 2 letters and 8 digits 'AA1234568'")
        if UserProfile.objects.filter(passport_number=value).exists():
            raise serializers.ValidationError("User with this passport number already exist")
        return value
    
    def validate(self, attrs):
        if attrs["first_name"] == attrs["last_name"]:
            raise serializers.ValidationError("First name and last name cannot be the same.")
        return attrs
    
    def validate_password(self, value):
        validate_password(value, self.context['request'].user)
        return value

    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    passport_number = serializers.CharField(write_only=True)
    age = serializers.IntegerField(write_only=True)
    bio = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "first_name",
            "last_name",
            "passport_number",
            "age",
            "bio",
        )

    def create(self, validated_data):
        profile_data = {
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "passport_number": validated_data.pop("passport_number"),
            "age": validated_data.pop("age"),
            "bio": validated_data.pop("bio"),
        }
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(
            user=user,
            **profile_data)
         
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    def validate_age(self, value):
        if value > 120:
            raise serializers.ValidationError("Write correct number.")
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
        if not re.fullmatch(r"[A-Z]{2}\d{8}", value):
            raise serializers.ValidationError("Password number should have 2 letters and 8 digits 'AA1234568'")
        return value
    
    def validate(self, attrs):
        if attrs["first_name"] == attrs["last_name"]:
            raise serializers.ValidationError("First name and last name cannot be the same.")
        return attrs
    class Meta:
        model = UserProfile
        fields = (
            "first_name",
            "last_name",
            "passport_number",
            "age",
            "bio",
        )

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorect password.")
        return value
    def validate_new_password(self, value):
        validate_password(value, self.context['request'].user)
        return value