from django.urls import path, include
from rest_framework.routers import DefaultRouter
from flights.views import (CountryViewSet,
                           AirportViewSet,
                           AirlinesViewSet,
                           )

router = DefaultRouter()
router.register(r"country", CountryViewSet, basename="country")
router.register(r"airport", AirportViewSet, basename="airport")
router.register(r"airline", AirlinesViewSet, basename="airline")
# router.register(r"airplane", AirplaneViewSet, basename="airplane")

urlpatterns = [
    path("", include(router.urls)),
]