"""
Cache-invalidation helper for the flight list endpoint.

Redis (via django.core.cache.backends.redis.RedisCache) doesn't give us
`delete_pattern`, so instead of trying to enumerate and delete every
individual cached query-string variation of `/flight/`, we use a
versioned-key scheme:

- Every cached list response is stored under a key that includes the
  current "version" number.
- Whenever a flight is created, updated, or deleted, we bump the version.
- Old cached entries are simply never looked up again (they naturally
  expire via their own TTL) - no explicit deletion needed.
"""
from django.core.cache import cache

FLIGHT_LIST_VERSION_KEY = "flights:list:cache_version"


def get_flight_list_cache_version() -> int:
    version = cache.get(FLIGHT_LIST_VERSION_KEY)

    if version is None:
        version = 1
        cache.set(FLIGHT_LIST_VERSION_KEY, version, timeout=None)

    return version


def bump_flight_list_cache_version() -> None:
    try:
        cache.incr(FLIGHT_LIST_VERSION_KEY)
    except ValueError:
        # Key doesn't exist yet (e.g. cache was cleared) - start fresh.
        cache.set(FLIGHT_LIST_VERSION_KEY, 1, timeout=None)
