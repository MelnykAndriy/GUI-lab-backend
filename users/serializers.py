from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"  # this is used in validation error messages


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["name", "gender", "dob", "createdAt", "avatarUrl", "avatarColor"]
        read_only_fields = ["createdAt"]


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    name = serializers.CharField(source="profile.name", read_only=True)
    gender = serializers.CharField(source="profile.gender", read_only=True)
    dob = serializers.DateField(source="profile.dob", read_only=True)
    createdAt = serializers.DateTimeField(source="profile.createdAt", read_only=True)
    avatarUrl = serializers.CharField(source="profile.avatarUrl", read_only=True)
    avatarColor = serializers.CharField(source="profile.avatarColor", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "gender",
            "dob",
            "createdAt",
            "avatarUrl",
            "avatarColor",
        ]
        read_only_fields = ["id", "createdAt"]


class UserRegisterRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(
        choices=[("male", "male"), ("female", "female"), ("other", "other")]
    )
    dob = serializers.DateField()
