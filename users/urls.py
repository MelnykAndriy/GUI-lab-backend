from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (AvatarUploadView, CurrentUserView, LoginView, RegisterView,
                    UserByEmailView)

urlpatterns = [
    path("me/", CurrentUserView.as_view(), name="current_user"),
    path("me/avatar", AvatarUploadView.as_view(), name="upload_avatar"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("search/<str:email>/", UserByEmailView.as_view(), name="user_by_email"),
]
