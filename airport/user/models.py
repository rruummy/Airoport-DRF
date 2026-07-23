from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    role = models.CharField(max_length=10, choices=ROLES, default='user')

    def __str__(self):
        return f"{self.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='profile')
    first_name = models.CharField(max_length=24)
    last_name = models.CharField(max_length=24)
    passport_number = models.CharField(max_length=32)
    age = models.PositiveIntegerField()
    bio = models.TextField(blank=True)