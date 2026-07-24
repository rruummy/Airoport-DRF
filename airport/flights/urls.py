from django.urls import path, include
from rest_framework.routers import DefaultRouter
from flights.views import CountryViewSet, AirportViewSet

router = DefaultRouter()
router.register(r"country", CountryViewSet, basename="country")
router.register(r"airport", AirportViewSet, basename="airport")

urlpatterns = [
    path("", include(router.urls)),
]