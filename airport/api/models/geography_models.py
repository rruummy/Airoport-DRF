from django.db import models

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
