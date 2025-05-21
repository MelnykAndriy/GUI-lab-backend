from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=255)
    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
    )
    dob = models.DateField()
    createdAt = models.DateTimeField(auto_now_add=True)
    avatarUrl = models.URLField(blank=True, null=True)
    avatarColor = models.CharField(max_length=16, blank=True, null=True)

    def __str__(self):
        return self.name
