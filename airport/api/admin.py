from django.contrib import admin
from api.models.air_model import Country, Airport, Airline, Airplane
from api.models.user_model import User
from api.models.flight_model import Flight
from api.models.ticket_model import Ticket

admin.site.register(User)
admin.site.register(Country)
admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Ticket)
