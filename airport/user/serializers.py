from rest_framework import serializers
from utils import hash_passport
from user.models import User, UserProfile
from django.contrib.auth.password_validation import validate_password
import re
from datetime import date

class RegisterSerializer(serializers.ModelSerializer):
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
            "password",
            "first_name",
            "last_name",
            "passport_number",
            "birth_date",
            "bio",
        )

    def create(self, validated_data):
        profile_data = {
            "first_name": validated_data.pop("first_name"),
            "last_name": validated_data.pop("last_name"),
            "passport_number": hash_passport(validated_data.pop("passport_number")),
            "birth_date": validated_data.pop("birth_date"),
            "bio": validated_data.pop("bio"),}
        
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(
            user=user,
            **profile_data)
         
        return user

class UserProfileSerializer(serializers.ModelSerializer):
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

        qs = UserProfile.objects.filter(passport_number=passport_hash)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "User with this passport number already exists."
            )

        return passport_hash
    
    def validate(self, attrs):
        first_name = attrs.get("first_name", self.instance.first_name)
        last_name = attrs.get("last_name", self.instance.last_name)

        if first_name == last_name:
            raise serializers.ValidationError(
                "First name and last name cannot be the same."
            )

        return attrs
    def validate_birth_date(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("The birthdate cannot be the future")
        return value
    def validate_age(self, value):
        return UserProfile.age(self)
    class Meta:
        model = UserProfile
        fields = (
            "first_name",
            "last_name",
            "passport_number",
            "age",
            "birth_date",
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
