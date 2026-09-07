from django.test import TestCase, override_settings

from utils import hash_passport


class HashPassportTests(TestCase):
    def test_same_input_and_secret_produce_same_hash(self):
        self.assertEqual(hash_passport("AB123456"), hash_passport("AB123456"))

    def test_different_input_produces_different_hash(self):
        self.assertNotEqual(hash_passport("AB123456"), hash_passport("AB123457"))

    def test_hash_is_a_64_char_hex_sha256_digest(self):
        result = hash_passport("AB123456")
        self.assertEqual(len(result), 64)
        int(result, 16)  # raises ValueError if not valid hex

    def test_changing_the_secret_changes_the_hash(self):
        with override_settings(PASSPORT_SECRET="secret-one"):
            first = hash_passport("AB123456")
        with override_settings(PASSPORT_SECRET="secret-two"):
            second = hash_passport("AB123456")
        self.assertNotEqual(first, second)
