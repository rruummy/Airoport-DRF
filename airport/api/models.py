from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]

    role = models.CharField(max_length=20, choices=ROLES,
                     default='user')

    def __str__(self):
        return self.username

class Country(models.Model):
    title   = models.CharField(max_length=255)
    code    = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return self.title
 
class Airport(models.Model):
    name    = models.CharField(max_length=255)
    city    = models.CharField(max_length=255)

    country  = models.ForeignKey('Country', on_delete=models.CASCADE)

    def __str__(self):
        return {self.name}

class Airline(models.Model):
    name    = models.CharField(max_length=255)
    airport = models.ForeignKey('Airport', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
 
class Airplane(models.Model):
    model   = models.CharField(max_length=255)
    capacity= models.PositiveIntegerField()

    airline = models.ForeignKey('Airline', on_delete=models.CASCADE)

    def __str__(self):
        return f"model: {self.model} capacity: {self.capacity}"

class Flight(models.Model):
    STATUS = [
        ('scheduled', 'Scheduled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('delayed', 'Delayed '),
        ('cancelled', 'Cancelled'),
    ]

    departure_airport= models.ForeignKey('Airport', on_delete=models.CASCADE, related_name='departures')
    arrival_airport  = models.ForeignKey('Airport', on_delete=models.CASCADE, related_name='arrivals')

    departure_time    = models.DateTimeField()
    arrival_time     = models.DateTimeField()

    price            = models.DecimalField(max_digits=10, decimal_places=2)
    status           = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f"departure: {self.departure_airport} -> arrival: {self.arrival_airport}"

class Ticket(models.Model):
    STATUS = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('used', 'Used'),
    ]

    user    = models.ForeignKey('User', on_delete=models.CASCADE)
    flight  = models.ForeignKey('Flight', on_delete=models.CASCADE)

    seat_number = models.PositiveIntegerField()

    status = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f"Ticket #{self.id}"
