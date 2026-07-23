from django.db import models
from user.models import User
from flights.models import Flight

class Ticket(models.Model):
    STATUS = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('used', 'Used'),
        ('paid', 'Paid'),
    ]

    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    flight = models.ForeignKey('flights.Flight', on_delete=models.CASCADE)

    seat_number = models.PositiveIntegerField()

    status = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f'Ticket #{self.id}'