from django.test import TestCase
from django.contrib.auth import get_user_model
from forecasts.models import MoodEntry, Color
from .models import WardrobeItem
from .services import calculate_item_score, pick_outfit
import datetime

User = get_user_model()

class WardrobeServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.color = Color.objects.create(name='Красный', hex_code='#FF0000', mood='радость')
        self.mood_entry = MoodEntry.objects.create(
            user=self.user, 
            entry_date=datetime.date.today(), 
            mood='радость', 
            color=self.color
        )
        self.item = WardrobeItem.objects.create(
            user=self.user, 
            name='Красная футболка', 
            category='верх', 
            color=self.color, 
            season='лето', 
            style='walk'
        )

    def test_calculate_item_score(self):
        score, reasons = calculate_item_score(self.item, self.color.id, 'радость', 'walk')
        # 40 (цвет) + 30 (повод) + 15 (настроение) + 15 (сезон) = 100
        self.assertEqual(score, 100)
        self.assertIn('совпадает с цветом удачи', reasons)

    def test_pick_outfit(self):
        selected, percentage, explanation = pick_outfit(self.user, 'walk', self.mood_entry)
        self.assertEqual(len(selected), 1) 
        self.assertEqual(selected[0]['item'].name, 'Красная футболка')