from django.contrib import admin
from flights.models import Country, Airline, Airplane, Airport, Flight

admin.site.register(Country)
admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Airplane)
admin.site.register(Flight)
