from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"  # this is used in validation error messages


class UserProfileSerializer(serializers.ModelSerializer):
    avatarUrl = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["name", "gender", "dob", "createdAt", "avatarUrl", "avatarColor"]
        read_only_fields = ["createdAt"]

    def get_avatarUrl(self, obj):
        request = self.context.get('request')
        if obj.avatarUrl and request:
            if obj.avatarUrl.startswith('http://') or obj.avatarUrl.startswith('https://'):
                return obj.avatarUrl
            return request.build_absolute_uri(obj.avatarUrl)
        return obj.avatarUrl


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    id = serializers.IntegerField(source="pk", read_only=True)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "profile",
        ]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        # Update UserProfile fields
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        return instance


class UserRegisterRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    gender = serializers.ChoiceField(
        choices=[("male", "male"), ("female", "female"), ("other", "other")]
    )
    dob = serializers.DateField()
