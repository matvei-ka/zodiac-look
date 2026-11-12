from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from forecasts.models import Color, MoodEntry
from wardrobe.models import IdealLook, Look, WardrobeItem


class PagesBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('anna', password='StrongPass123!', zodiac_sign='leo')
        self.color = Color.objects.create(
            name='Золотой', hex_code='#E0B04A', meaning='Блеск', mood='joy'
        )

    def make_entry(self):
        return MoodEntry.objects.create(
            user=self.user, entry_date=timezone.localdate(), mood='joy', color=self.color
        )

    def make_item(self, name='Красная футболка'):
        return WardrobeItem.objects.create(
            user=self.user, name=name, category='верх',
            color=self.color, season='лето', style='walk',
        )


class AccessTests(PagesBase):
    def test_pages_require_login(self):
        names = [
            'forecasts:forecast', 'forecasts:audit', 'wardrobe:wardrobe_list',
            'wardrobe:item_add', 'wardrobe:stylist', 'wardrobe:look_list',
        ]
        for name in names:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn(reverse('accounts:login'), response.url, name)

    def test_home_redirects(self):
        self.assertIn(reverse('accounts:login'), self.client.get(reverse('core:home')).url)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('core:home')).url, reverse('forecasts:forecast'))

    def test_help_is_public(self):
        self.assertEqual(self.client.get(reverse('core:help')).status_code, 200)


class ForecastPageTests(PagesBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_page_opens_without_entry(self):
        self.assertEqual(self.client.get(reverse('forecasts:forecast')).status_code, 200)

    @patch('forecasts.views.get_horoscope_text', return_value='Тестовый гороскоп')
    def test_choose_mood_shows_forecast(self, mock_text):
        response = self.client.post(reverse('forecasts:forecast'), {'mood': 'joy'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый гороскоп')
        self.assertContains(response, 'Золотой')

    def test_unknown_mood_is_rejected(self):
        self.client.post(reverse('forecasts:forecast'), {'mood': 'abc'})
        self.assertFalse(MoodEntry.objects.exists())

    def test_audit_page(self):
        self.make_entry()
        response = self.client.get(reverse('forecasts:audit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Золотой')
        self.assertNotContains(response, 'linear-gradient(90deg, #E0B04A')

    def test_audit_empty(self):
        self.assertEqual(self.client.get(reverse('forecasts:audit')).status_code, 200)

    def test_audit_tie_makes_gradient(self):
        second = Color.objects.create(
            name='Мятный', hex_code='#A8E6CF', meaning='Покой', mood='calm'
        )
        today = timezone.localdate()
        MoodEntry.objects.create(user=self.user, entry_date=today, mood='joy', color=self.color)
        MoodEntry.objects.create(
            user=self.user, entry_date=today - timedelta(days=1),
            mood='calm', color=second,
        )
        response = self.client.get(reverse('forecasts:audit'))
        self.assertContains(response, 'Твоя палитра')
        self.assertContains(response, 'linear-gradient(90deg, #E0B04A, #A8E6CF)')


class WardrobePagesTests(PagesBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_pages_open(self):
        for name in ['wardrobe:wardrobe_list', 'wardrobe:item_add', 'wardrobe:look_list']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_add_item(self):
        response = self.client.post(reverse('wardrobe:item_add'), {
            'name': 'Синие джинсы', 'category': 'низ', 'color': self.color.id,
            'season': 'всесезонный', 'style': 'walk',
        })
        self.assertRedirects(response, reverse('wardrobe:wardrobe_list'))
        self.assertTrue(WardrobeItem.objects.filter(user=self.user, name='Синие джинсы').exists())

    def test_edit_item(self):
        item = self.make_item()
        self.client.post(reverse('wardrobe:item_edit', args=[item.pk]), {
            'name': 'Белая футболка', 'category': 'верх', 'color': self.color.id,
            'season': 'лето', 'style': 'walk',
        })
        item.refresh_from_db()
        self.assertEqual(item.name, 'Белая футболка')

    def test_delete_item(self):
        item = self.make_item()
        self.client.post(reverse('wardrobe:item_delete', args=[item.pk]))
        self.assertFalse(WardrobeItem.objects.filter(pk=item.pk).exists())

    def test_cannot_touch_foreign_item(self):
        other = User.objects.create_user('boris', password='StrongPass123!', zodiac_sign='leo')
        item = WardrobeItem.objects.create(
            user=other, name='Чужая вещь', category='верх',
            color=self.color, season='лето', style='walk',
        )
        response = self.client.post(reverse('wardrobe:item_delete', args=[item.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(WardrobeItem.objects.filter(pk=item.pk).exists())

    def test_style_is_shown_in_russian(self):
        self.make_item()
        response = self.client.get(reverse('wardrobe:wardrobe_list'))
        self.assertContains(response, 'Прогулка по городу')
        self.assertNotContains(response, '>Walk<')

    def test_filter_by_category(self):
        self.make_item('Красная футболка')
        response = self.client.get(reverse('wardrobe:wardrobe_list'), {'category': 'низ'})
        self.assertNotContains(response, 'Красная футболка')


class StylistTests(PagesBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    def test_redirects_without_mood(self):
        response = self.client.get(reverse('wardrobe:stylist'))
        self.assertRedirects(response, reverse('forecasts:forecast'), fetch_redirect_response=False)

    def test_page_opens_with_mood(self):
        self.make_entry()
        self.assertEqual(self.client.get(reverse('wardrobe:stylist')).status_code, 200)

    def test_no_items_redirects_to_wardrobe(self):
        self.make_entry()
        response = self.client.post(reverse('wardrobe:stylist'), {'occasion': 'walk'})
        self.assertRedirects(response, reverse('wardrobe:wardrobe_list'), fetch_redirect_response=False)

    def test_pick_and_save_look(self):
        entry = self.make_entry()
        self.make_item()
        response = self.client.post(reverse('wardrobe:stylist'), {'occasion': 'walk'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Красная футболка')
        look = Look.objects.get(user=self.user)
        self.assertFalse(look.is_saved)
        entry.refresh_from_db()
        self.assertEqual(entry.look_id, look.id)

        response = self.client.post(reverse('wardrobe:look_save', args=[look.pk]))
        self.assertRedirects(response, reverse('wardrobe:look_list'))
        look.refresh_from_db()
        self.assertTrue(look.is_saved)
        self.assertContains(self.client.get(reverse('wardrobe:look_list')), look.title)

    def test_unknown_occasion_is_rejected(self):
        self.make_entry()
        self.make_item()
        self.client.post(reverse('wardrobe:stylist'), {'occasion': 'abc'})
        self.assertFalse(Look.objects.exists())

    def test_delete_saved_look(self):
        self.make_entry()
        self.make_item()
        self.client.post(reverse('wardrobe:stylist'), {'occasion': 'walk'})
        look = Look.objects.get(user=self.user)
        self.client.post(reverse('wardrobe:look_save', args=[look.pk]))
        self.client.post(reverse('wardrobe:look_delete', args=[look.pk]))
        self.assertFalse(Look.objects.filter(pk=look.pk).exists())


class IdealLooksTests(PagesBase):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)
        IdealLook.objects.create(
            occasion='walk', title='Городской образ',
            image_url='https://example.com/look.jpg',
        )

    def test_ideal_in_stylist_result(self):
        self.make_entry()
        self.make_item()
        response = self.client.post(reverse('wardrobe:stylist'), {'occasion': 'walk'})
        self.assertContains(response, 'Городской образ')

    def test_ideal_only_for_chosen_occasion(self):
        IdealLook.objects.create(
            occasion='work', title='Деловой образ', image_url='https://example.com/work.jpg',
        )
        self.make_entry()
        self.make_item()
        response = self.client.post(reverse('wardrobe:stylist'), {'occasion': 'walk'})
        self.assertContains(response, 'Городской образ')
        self.assertNotContains(response, 'Деловой образ')

    def test_ideal_adapts_to_mood(self):
        IdealLook.objects.create(
            occasion='walk', title='Грустный образ', mood='sadness',
            image_url='https://example.com/sad.jpg',
        )
        self.make_entry()
        self.make_item()
        response = self.client.post(reverse('wardrobe:stylist'), {'occasion': 'walk'})
        self.assertContains(response, 'Городской образ')
        self.assertNotContains(response, 'Грустный образ')
