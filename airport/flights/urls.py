from django.urls import path, include
from rest_framework.routers import DefaultRouter
from flights.views import (CountryViewSet,
                           AirportViewSet,
                           AirlinesViewSet,
                           AirplaneViewSet,
                           FlightViewSet,
                           FlightWeatherView,
                           )

router = DefaultRouter()
router.register(r"country", CountryViewSet, basename="country")
router.register(r"airport", AirportViewSet, basename="airport")
router.register(r"airline", AirlinesViewSet, basename="airline")
router.register(r"airplane", AirplaneViewSet, basename="airplane")
router.register(r"flight", FlightViewSet, basename="flight")

urlpatterns = [
    path("", include(router.urls)),
    path("flight/<int:pk>/weather/", FlightWeatherView.as_view(), name="flight-weather"),
]