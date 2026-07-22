from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    role = models.CharField(max_length=20, choices=ROLES, default='user')

    def __str__(self):
        return self.username

"""
class UserProfile(models):
    id       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='id')
    name     = models.CharField(max_length=32),
    surname  = models.CharField(max_length=32),
    document = models.CharField(max_length=32),
    bio      = models.CharField(max_length=256),

    def __str__(self):
        return f"NS: {self.name} {self.surname} Doc: {self.document}
"""
