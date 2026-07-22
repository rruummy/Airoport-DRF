from django.contrib import admin
from api.models import User, Country, Airport, Airline, Airplane, Flight, Ticket

admin.site.register(User)
admin.site.register(Country)
admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Ticket)
