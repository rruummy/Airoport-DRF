import django_filters
from tickets.models import Ticket

class TicketFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
    )

    max_price = django_filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
    )
    class Meta:
        model = Ticket
        fields = ['status', 'flight',]