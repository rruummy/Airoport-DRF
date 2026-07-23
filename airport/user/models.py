from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator

class User(AbstractUser):
    ROLES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    role = models.CharField(max_length=10, choices=ROLES, default='user')

    @property
    def is_admin_role(self):
        return self.role == 'admin' or self.is_superuser

    def __str__(self):
        return f"{self.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='profile')
    first_name = models.CharField(max_length=24)
    last_name = models.CharField(max_length=24)
    passport_number = models.CharField(max_length=10,
                                       unique=True,
                                       validators=[MinLengthValidator(10)])
    age = models.PositiveIntegerField()
    bio = models.TextField(blank=True)