import os

from django.conf import settings
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import UserProfile
from .serializers import (EmailTokenObtainPairSerializer,
                          UserRegisterRequestSerializer, UserSerializer)

# Message and chat views have been moved to messages/views.py and chats/views.py
# Only user-related views should remain here.
# This file can be deleted after confirming all logic is migrated.


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        avatar = request.FILES.get("avatar")
        if not avatar:
            return Response({"code": 400, "message": "No file uploaded"}, status=400)
        if avatar.size > 2 * 1024 * 1024:  # 2MB limit
            return Response({"code": 400, "message": "File too large"}, status=400)
        ext = os.path.splitext(avatar.name)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".gif"]:
            return Response({"code": 400, "message": "Invalid file format"}, status=400)
        filename = f"avatar_{request.user.id}{ext}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        with open(filepath, "wb+") as dest:
            for chunk in avatar.chunks():
                dest.write(chunk)
        avatar_url = f"{settings.MEDIA_URL}avatars/{filename}"
        request.user.profile.avatarUrl = (
            avatar_url if hasattr(request.user, "profile") else avatar_url
        )
        request.user.save()
        return Response({"avatarUrl": avatar_url})


class UserByEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"code": 404, "message": "User not found"}, status=404)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"code": 400, "message": "Invalid input", "details": serializer.errors},
                status=400,
            )
        data = serializer.validated_data
        if User.objects.filter(email=data["email"]).exists():
            return Response(
                {"code": 400, "message": "Email already exists"}, status=400
            )
        user = User.objects.create(
            username=data["email"],
            email=data["email"],
        )
        user.set_password(data["password"])
        user.save()
        profile = UserProfile.objects.create(
            user=user,
            name=data["name"],
            gender=data["gender"],
            dob=data["dob"],
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {"token": str(refresh.access_token), "user": UserSerializer(user).data},
            status=201,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = EmailTokenObtainPairSerializer
