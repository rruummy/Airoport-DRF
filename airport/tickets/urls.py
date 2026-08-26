from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tickets.views import TicketViewSet, BookTicketView, TicketPDFView

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="tickets")
router.register("book-tickets", BookTicketView, basename="book-tickets")

urlpatterns = [
    path("", include(router.urls)),
    path("tickets/<int:ticket_id>/pdf/", TicketPDFView.as_view(), name="ticket-pdf"),
]