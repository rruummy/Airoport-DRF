from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator

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
    status = models.CharField(max_length=20, choices=STATUS, default='booked')
    price = models.DecimalField(decimal_places=2,
                                  max_digits=10,
                                  default=Decimal(0.00),
                                  validators=[MinValueValidator(0.00)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['flight', 'seat_number'],
                                    name='unique_seat_per_flights')
        ]

    def __str__(self):
        return f'Ticket #{self.flight_id}/{self.id}'