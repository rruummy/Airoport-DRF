from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator, MinValueValidator
from decimal import Decimal
from datetime import date

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
    balance = models.DecimalField(decimal_places=2,
                                  max_digits=10,
                                  default=Decimal(0.00),
                                  validators=[MinValueValidator(0.00)])
    @property
    def age(self) -> int:

        today = date.today()
        return (today.year - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day)))
    birth_date = models.DateField()
    bio = models.TextField(blank=True)