from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class RegistrationTests(TestCase):
    def setUp(self):
        self.url = reverse('accounts:register')

    def test_page_opens(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_successful_registration(self):
        response = self.client.post(self.url, {
            'username': 'anna',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'zodiac_sign': 'leo',
        })
        self.assertRedirects(response, reverse('core:home'), fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(username='anna', zodiac_sign='leo').exists())

    def test_passwords_do_not_match(self):
        response = self.client.post(self.url, {
            'username': 'anna',
            'password1': 'StrongPass123!',
            'password2': 'Another456!',
            'zodiac_sign': 'leo',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='anna').exists())