from unittest.mock import patch

import requests
from django.core.cache import cache
from django.test import TestCase

from accounts.models import User
from forecasts.models import Color, MoodEntry
from forecasts.services import (
    FALLBACK_TEXT,
    get_horoscope_text,
    pick_color,
    save_forecast,
)


class PickColorTests(TestCase):
    def test_returns_color_for_mood(self):
        Color.objects.create(name='Мятный', hex_code='#A8E6CF', meaning='Покой', mood='calm')
        Color.objects.create(name='Золотой', hex_code='#E0B04A', meaning='Блеск', mood='joy')
        self.assertEqual(pick_color('calm').name, 'Мятный')

    def test_falls_back_to_any_color(self):
        Color.objects.create(name='Золотой', hex_code='#E0B04A', meaning='Блеск', mood='joy')
        self.assertEqual(pick_color('sadness').name, 'Золотой')

    def test_returns_none_without_colors(self):
        self.assertIsNone(pick_color('joy'))


class SaveForecastTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('anna', password='StrongPass123!', zodiac_sign='leo')
        Color.objects.create(name='Золотой', hex_code='#E0B04A', meaning='Блеск', mood='joy')
        Color.objects.create(name='Мятный', hex_code='#A8E6CF', meaning='Покой', mood='calm')

    def test_creates_entry(self):
        entry = save_forecast(self.user, 'joy')
        self.assertEqual(entry.mood, 'joy')
        self.assertEqual(entry.color.mood, 'joy')

    def test_one_forecast_per_day(self):
        save_forecast(self.user, 'joy')
        save_forecast(self.user, 'calm')
        self.assertEqual(MoodEntry.objects.filter(user=self.user).count(), 1)

    def test_mood_change_updates_entry(self):
        save_forecast(self.user, 'joy')
        entry = save_forecast(self.user, 'calm')
        self.assertEqual(entry.mood, 'calm')
        self.assertEqual(entry.color.mood, 'calm')

    def test_returns_none_without_colors(self):
        Color.objects.all().delete()
        self.assertIsNone(save_forecast(self.user, 'joy'))


class HoroscopeTextTests(TestCase):
    def setUp(self):
        cache.clear()

    @patch('forecasts.services.translate_to_russian', side_effect=lambda text: text)
    @patch('forecasts.services.requests.get')
    def test_returns_text_from_api(self, mock_get, mock_translate):
        mock_get.return_value.json.return_value = {'horoscope': 'Good day'}
        self.assertEqual(get_horoscope_text('leo'), 'Good day')

    @patch('forecasts.services.translate_to_russian', return_value='Хороший день')
    @patch('forecasts.services.requests.get')
    def test_text_is_translated(self, mock_get, mock_translate):
        mock_get.return_value.json.return_value = {'horoscope': 'Good day'}
        self.assertEqual(get_horoscope_text('leo'), 'Хороший день')

    @patch('forecasts.services.requests.get')
    def test_fallback_when_api_fails(self, mock_get):
        mock_get.side_effect = requests.RequestException()
        self.assertEqual(get_horoscope_text('leo'), FALLBACK_TEXT)

    def test_fallback_without_zodiac_sign(self):
        self.assertEqual(get_horoscope_text(''), FALLBACK_TEXT)