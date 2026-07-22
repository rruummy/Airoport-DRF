from django.db import models

class Ticket(models.Model):
    STATUS = [
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('used', 'Used'),
        ('paid', 'Paid')
    ]

    user    = models.ForeignKey('User', on_delete=models.CASCADE)
    flight  = models.ForeignKey('Flight', on_delete=models.CASCADE)

    seat_number = models.PositiveIntegerField()

    status = models.CharField(max_length=20, choices=STATUS)

    def __str__(self):
        return f"Ticket #{self.id}"

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