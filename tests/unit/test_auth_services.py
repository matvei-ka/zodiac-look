from django.db import IntegrityError, transaction
from django.test import TestCase

from accounts.services import register_user


class RegisterUserTests(TestCase):
    def test_creates_user_with_zodiac_sign(self):
        user = register_user('anna', 'StrongPass123!', 'leo')
        self.assertEqual(user.username, 'anna')
        self.assertEqual(user.zodiac_sign, 'leo')

    def test_password_is_hashed(self):
        user = register_user('anna', 'StrongPass123!', 'leo')
        self.assertNotEqual(user.password, 'StrongPass123!')
        self.assertTrue(user.check_password('StrongPass123!'))

    def test_duplicate_username_is_rejected(self):
        register_user('anna', 'StrongPass123!', 'leo')
        with self.assertRaises(IntegrityError), transaction.atomic():
            register_user('anna', 'OtherPass456!', 'virgo')