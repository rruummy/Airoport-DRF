from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tickets.views import TicketViewSet, BookTicketView

router = DefaultRouter()
router.register("tickets", TicketViewSet, basename="tickets")
router.register("book-tickets", BookTicketView, basename="book-tickets")

urlpatterns = [
    path("", include(router.urls)),
]