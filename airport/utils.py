import hashlib
from django.conf import settings

def hash_passport(passport: str) -> str:
    data = f"{passport}{settings.PASSPORT_SECRET}"
    return hashlib.sha256(data.encode("utf-8")).hexdigest()