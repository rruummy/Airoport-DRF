from django.db import models

class Flight(models.Model):
    STATUS = [
        ('scheduled', 'Scheduled'),
        ('boarding', 'Boarding'),
        ('departed', 'Departed'),
        ('delayed', 'Delayed '),
        ('cancelled', 'Cancelled'),
    ]

    departure_airport = models.ForeignKey(
        'Airport', on_delete=models.CASCADE, related_name='departures'
    )
    arrival_airport = models.ForeignKey(
        'Airport', on_delete=models.CASCADE, related_name='arrivals'
    )

    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='scheduled')

    airplane = models.ForeignKey('Airplane', on_delete=models.CASCADE, related_name='flights')
    airline = models.ForeignKey('Airline', on_delete=models.CASCADE, related_name='flights')

    def __str__(self):
        return f'{self.departure_airport} -> {self.arrival_airport}'

class Country(models.Model):
    title = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return f"{self.title}"

class Airport(models.Model):
    name = models.CharField(max_length=255, unique=True)
    city = models.CharField(max_length=255)

    country = models.ForeignKey('Country', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'

class Airline(models.Model):
    name = models.CharField(max_length=255)
    airport = models.ManyToManyField('Airport', related_name='airlines')

    def __str__(self):
        return f'{self.name}'

class Airplane(models.Model):
    model = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()

    airline = models.ForeignKey('Airline', on_delete=models.CASCADE)

    def __str__(self):
        return f'model: {self.model} capacity: {self.capacity}'
