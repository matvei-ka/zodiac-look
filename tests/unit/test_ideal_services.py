from datetime import date

from django.test import SimpleTestCase, TestCase

from wardrobe.ideal import current_season, pick_ideal_looks
from wardrobe.models import IdealLook


class CurrentSeasonTests(SimpleTestCase):
    def test_winter(self):
        self.assertEqual(current_season(date(2026, 1, 15)), 'зима')
        self.assertEqual(current_season(date(2026, 12, 1)), 'зима')

    def test_summer(self):
        self.assertEqual(current_season(date(2026, 7, 10)), 'лето')

    def test_demi_season(self):
        self.assertEqual(current_season(date(2026, 4, 10)), 'демисезон')
        self.assertEqual(current_season(date(2026, 10, 10)), 'демисезон')


class PickIdealLooksTests(TestCase):
    def make(self, title, mood='', season='', occasion='walk'):
        return IdealLook.objects.create(
            occasion=occasion, title=title, mood=mood, season=season,
            image_url='https://example.com/look.jpg',
        )

    def titles(self, looks):
        return [look.title for look in looks]

    def test_prefers_matching_mood_and_season(self):
        self.make('Универсальный')
        self.make('Точный', mood='joy', season='лето')
        self.make('Не тот', mood='sadness', season='зима')
        result = pick_ideal_looks('walk', 'joy', 'лето')
        self.assertEqual(self.titles(result), ['Точный', 'Универсальный'])

    def test_wrong_season_is_skipped_when_others_fit(self):
        self.make('Зимний', season='зима')
        self.make('Летний', season='лето')
        self.assertEqual(self.titles(pick_ideal_looks('walk', 'joy', 'лето')), ['Летний'])

    def test_fallback_when_nothing_fits(self):
        self.make('Зимний', season='зима')
        self.assertEqual(self.titles(pick_ideal_looks('walk', 'joy', 'лето')), ['Зимний'])

    def test_only_chosen_occasion(self):
        self.make('Прогулка')
        self.make('Работа', occasion='work')
        self.assertEqual(self.titles(pick_ideal_looks('walk', 'joy', 'лето')), ['Прогулка'])

    def test_limit(self):
        for number in range(6):
            self.make(f'Образ {number}')
        self.assertEqual(len(pick_ideal_looks('walk', 'joy', 'лето', limit=4)), 4)

    def test_empty(self):
        self.assertEqual(pick_ideal_looks('walk', 'joy', 'лето'), [])
