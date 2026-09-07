"""
Shared helpers for building test fixtures (users, flights, tickets, ...).

These are plain functions (not pytest fixtures / not factory_boy) so they
work with the stdlib ``unittest``/``django.test.TestCase`` classes used
across the project, without adding new dependencies.
"""
from datetime import timedelta
from decimal import Decimal

from django.utils import timezone

from utils import hash_passport
from user.models import User, UserProfile
from flights.models import Airport, Airline, Airplane, Country, Flight


def create_country(title="Ukraine", code="UA"):
    # get_or_create because several factory calls in the same test
    # (e.g. departure + arrival airport) fall back to this same default
    # country, and both "title" and "code" are unique=True on the model.
    country, _ = Country.objects.get_or_create(title=title, defaults={"code": code})
    return country


def create_airport(name, city="Kyiv", country=None):
    country = country or create_country()
    airport, _ = Airport.objects.get_or_create(
        name=name, defaults={"city": city, "country": country}
    )
    return airport


def create_airline(name="Test Airline", airports=None):
    airline = Airline.objects.create(name=name)
    if airports:
        airline.airport.add(*airports)
    return airline


def create_airplane(model="Boeing 737", capacity=180, airline=None):
    airline = airline or create_airline()
    return Airplane.objects.create(model=model, capacity=capacity, airline=airline)


def create_flight(departure_airport=None, arrival_airport=None,
                   airplane=None, airline=None, status="scheduled",
                   departure_time=None, arrival_time=None,
                   price=Decimal("100.00")):
    departure_airport = departure_airport or create_airport("Boryspil")
    arrival_airport = arrival_airport or create_airport("Heathrow", city="London")
    airline = airline or create_airline()
    airplane = airplane or create_airplane(airline=airline)

    departure_time = departure_time or (timezone.now() + timedelta(days=1))
    arrival_time = arrival_time or (departure_time + timedelta(hours=3))

    return Flight.objects.create(
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=departure_time,
        arrival_time=arrival_time,
        status=status,
        airplane=airplane,
        airline=airline,
        price=price,
    )


def create_user(email="user@example.com", username=None, password="StrongPass123!",
                 role="user", is_active=True, is_superuser=False):
    username = username or email.split("@")[0]
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role=role,
        is_active=is_active,
    )
    if is_superuser:
        user.is_superuser = True
        user.save(update_fields=["is_superuser"])
    return user


def create_profile(user, first_name="John", last_name="Doe",
                    raw_passport=None, birth_date=None, bio=""):
    passport_hash = hash_passport(raw_passport) if raw_passport else None
    return UserProfile.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        passport_number=passport_hash,
        birth_date=birth_date,
        bio=bio,
    )
