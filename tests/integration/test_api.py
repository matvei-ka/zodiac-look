from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from forecasts.models import Color


class ForecastApiTests(TestCase):
    def setUp(self):
        patcher = patch('api.views.get_horoscope_text', return_value='Тестовый гороскоп')
        patcher.start()
        self.addCleanup(patcher.stop)
        self.user = User.objects.create_user('anna', password='StrongPass123!', zodiac_sign='leo')
        Color.objects.create(name='Золотой', hex_code='#E0B04A', meaning='Блеск', mood='joy')
        self.url = reverse('api:forecast')

    def test_requires_login(self):
        self.assertEqual(self.client.get(self.url).status_code, 401)

    def test_no_forecast_yet(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 404)

    def test_create_and_get_forecast(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'mood': 'joy'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['color']['name'], 'Золотой')
        self.assertEqual(response.json()['horoscope'], 'Тестовый гороскоп')
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_unknown_mood(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {'mood': 'abc'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)