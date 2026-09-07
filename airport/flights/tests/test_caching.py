from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from test_factories import create_flight, create_airport, create_airline, create_airplane, create_user
from flights.cache import get_flight_list_cache_version, bump_flight_list_cache_version


class FlightListCacheVersionTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_version_starts_at_one(self):
        self.assertEqual(get_flight_list_cache_version(), 1)

    def test_bump_increments_the_version(self):
        get_flight_list_cache_version()  # initialize to 1
        bump_flight_list_cache_version()

        self.assertEqual(get_flight_list_cache_version(), 2)

    def test_bump_without_prior_read_still_works(self):
        bump_flight_list_cache_version()
        self.assertIsInstance(get_flight_list_cache_version(), int)


class FlightListCachingTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.flight = create_flight()
        self.admin = create_user(email="admin-cache@example.com", role="admin", is_active=True)
        # /flight/ requires an authenticated, verified user even for GET
        # (IsAdminOrReadOnly has no fully-public branch), so reads in these
        # tests go through a plain verified user rather than anonymously.
        self.reader = create_user(email="reader-cache@example.com", role="user", is_active=True)
        self.url = reverse("flight-list")

    def as_reader(self):
        self.client.force_authenticate(user=self.reader)

    def test_second_identical_request_is_served_from_cache(self):
        self.as_reader()

        # First request populates the cache and hits the DB.
        first = self.client.get(self.url)
        self.assertEqual(first.status_code, 200)

        # Second, identical request should not need any DB queries at all.
        with self.assertNumQueries(0):
            second = self.client.get(self.url)

        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data, second.data)

    def test_different_query_strings_are_cached_separately(self):
        self.as_reader()
        create_flight(price=999)

        response_all = self.client.get(self.url)
        response_filtered = self.client.get(self.url, {"ordering": "price"})

        self.assertEqual(response_all.status_code, 200)
        self.assertEqual(response_filtered.status_code, 200)
        # Different query strings must not collide on the same cache entry.
        prices_all = [item["price"] for item in response_all.data["results"]]
        prices_ordered = [item["price"] for item in response_filtered.data["results"]]
        self.assertEqual(prices_ordered, sorted(prices_ordered))
        self.assertEqual(set(prices_all), set(prices_ordered))

    def test_creating_a_flight_invalidates_the_cached_list(self):
        self.as_reader()
        first = self.client.get(self.url)
        first_count = first.data["count"]

        self.client.force_authenticate(user=self.admin)
        airport1 = create_airport("New Airport A")
        airport2 = create_airport("New Airport B", city="Somewhere")
        airline = create_airline(name="Cache Test Airline")
        airplane = create_airplane(airline=airline)

        create_response = self.client.post("/flight/", {
            "departure_airport": airport1.id,
            "arrival_airport": airport2.id,
            "airplane": airplane.id,
            "airline": airline.id,
            "departure_time": "01.01.2027 10:00",
            "arrival_time": "01.01.2027 14:00",
            "price": "200.00",
            "status": "scheduled",
        })
        self.assertEqual(create_response.status_code, 201)

        self.as_reader()
        second = self.client.get(self.url)

        self.assertEqual(second.data["count"], first_count + 1)

    def test_deleting_a_flight_invalidates_the_cached_list(self):
        extra_flight = create_flight(price=555)

        self.as_reader()
        first = self.client.get(self.url)
        first_count = first.data["count"]

        self.client.force_authenticate(user=self.admin)
        delete_response = self.client.delete(f"/flight/{extra_flight.id}/")
        self.assertEqual(delete_response.status_code, 204)

        self.as_reader()
        second = self.client.get(self.url)

        self.assertEqual(second.data["count"], first_count - 1)
