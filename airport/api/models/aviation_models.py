from django.db import models

class Airline(models.Model):
    name    = models.CharField(max_length=255)
    airport = models.ForeignKey('Airport', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"
 
class Airplane(models.Model):
    model   = models.CharField(max_length=255)
    capacity= models.PositiveIntegerField()

    airline = models.ForeignKey('Airline', on_delete=models.CASCADE)

    def __str__(self):
        return f"model: {self.model} capacity: {self.capacity}"