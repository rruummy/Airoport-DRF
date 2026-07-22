from django.contrib import admin
from api.models.geography_models import Country, Airport
from api.models.aviation_models import Airline, Airplane
from api.models.user_model import User
from api.models.booking_models import Flight, Ticket

admin.site.register(User)
admin.site.register(Country)
admin.site.register(Airport)
admin.site.register(Airline)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Ticket)
