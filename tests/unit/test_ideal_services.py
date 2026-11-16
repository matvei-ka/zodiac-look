from django.test import TestCase

from wardrobe.ideal import pick_ideal_looks
from wardrobe.models import IdealLook


class PickIdealLooksTests(TestCase):
    def make(self, title, occasion='walk'):
        return IdealLook.objects.create(
            occasion=occasion, title=title, image_url='https://example.com/look.jpg',
        )

    def titles(self, looks):
        return [look.title for look in looks]

    def test_only_chosen_occasion(self):
        self.make('Прогулка')
        self.make('Работа', occasion='work')
        self.assertEqual(self.titles(pick_ideal_looks('walk')), ['Прогулка'])

    def test_limit(self):
        for number in range(6):
            self.make(f'Образ {number}')
        self.assertEqual(len(pick_ideal_looks('walk', limit=4)), 4)

    def test_empty(self):
        self.assertEqual(pick_ideal_looks('walk'), [])


class IdealLookSrcTests(TestCase):
    def test_url_is_used_without_file(self):
        look = IdealLook(title='Образ', image_url='https://example.com/look.jpg')
        self.assertEqual(look.src, 'https://example.com/look.jpg')

    def test_file_wins_over_url(self):
        look = IdealLook(
            title='Образ', image='ideal_looks/a.jpg', image_url='https://example.com/look.jpg'
        )
        self.assertTrue(look.src.endswith('ideal_looks/a.jpg'))
