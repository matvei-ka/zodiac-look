from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class LoginTests(TestCase):
    def setUp(self):
        User.objects.create_user('anna', password='StrongPass123!', zodiac_sign='leo')
        self.url = reverse('accounts:login')

    def test_page_opens(self):
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_successful_login(self):
        response = self.client.post(self.url, {'username': 'anna', 'password': 'StrongPass123!'})
        self.assertRedirects(response, reverse('core:home'), fetch_redirect_response=False)

    def test_wrong_password(self):
        response = self.client.post(self.url, {'username': 'anna', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_forecast_requires_login(self):
        response = self.client.get(reverse('forecasts:forecast'))
        expected = f"{reverse('accounts:login')}?next={reverse('forecasts:forecast')}"
        self.assertRedirects(response, expected, fetch_redirect_response=False)