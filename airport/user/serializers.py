from rest_framework import serializers
from user.models import User, UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
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
        