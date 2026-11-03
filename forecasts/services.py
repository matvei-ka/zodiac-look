import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .models import Color, MoodEntry

API_URL = 'https://api.api-ninjas.com/v1/horoscope'
FALLBACK_TEXT = 'Сегодня звёзды молчат, но день всё равно будет твоим.'


def get_horoscope_text(zodiac_sign):
    """Текст гороскопа из API Ninjas; при ошибке возвращает запасной текст."""
    if not zodiac_sign:
        return FALLBACK_TEXT
    key = f'horoscope:{zodiac_sign}:{timezone.localdate()}'
    text = cache.get(key)
    if text:
        return text
    try:
        response = requests.get(
            API_URL,
            params={'zodiac': zodiac_sign},
            headers={'X-Api-Key': settings.NINJAS_API_KEY or ''},
            timeout=5,
        )
        response.raise_for_status()
        text = response.json().get('horoscope') or FALLBACK_TEXT
    except (requests.RequestException, ValueError):
        return FALLBACK_TEXT
    cache.set(key, text, 60 * 60 * 6)
    return text


def pick_color(mood):
    """Случайный цвет удачи под настроение (если нет, то любой)."""
    color = Color.objects.filter(mood=mood).order_by('?').first()
    return color or Color.objects.order_by('?').first()


def get_today_entry(user):
    return (
        MoodEntry.objects.filter(user=user, entry_date=timezone.localdate())
        .select_related('color')
        .first()
    )


def save_forecast(user, mood):
    """Один прогноз в сутки: при смене настроения запись обновляется."""
    entry = get_today_entry(user)
    if entry and entry.mood == mood:
        return entry
    color = pick_color(mood)
    if color is None:
        return None
    if entry:
        entry.mood = mood
        entry.color = color
        entry.save()
        return entry
    return MoodEntry.objects.create(
        user=user, entry_date=timezone.localdate(), mood=mood, color=color
    )