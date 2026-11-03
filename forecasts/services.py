import re

import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .models import Color, MoodEntry

API_URL = 'https://api.api-ninjas.com/v1/horoscope'
FALLBACK_TEXT = 'Сегодня звёзды молчат, но день всё равно будет твоим.'


def _split_text(text, limit=450):
    """Делит текст на части по предложениям (у MyMemory лимит ~500 символов)."""
    parts, current = [], ''
    for sentence in re.split(r'(?<=[.!?])\s+', text):
        if current and len(current) + len(sentence) + 1 > limit:
            parts.append(current)
            current = sentence
        else:
            current = f'{current} {sentence}'.strip()
    if current:
        parts.append(current)
    return parts

ASTRO_FIXES = [
    ('Небесные выравнивания', 'Расположение планет'),
    ('небесные выравнивания', 'расположение планет'),
    ('Небесное выравнивание', 'Расположение планет'),
    ('небесное выравнивание', 'расположение планет'),
    ('выравнивания', 'расположения'),
    ('выравнивание', 'расположение'),
]


def fix_astrology_terms(text):
    """Исправляет дословные переводы астрологических терминов."""
    for wrong, right in ASTRO_FIXES:
        text = text.replace(wrong, right)
    return text


def translate_to_russian(text):
    """Переводит на русский (Google, при отказе MyMemory); при ошибке возвращает None."""
    translators = (
        lambda: GoogleTranslator(source='en', target='ru'),
        lambda: MyMemoryTranslator(source='en-GB', target='ru-RU'),
    )
    for make_translator in translators:
        try:
            translator = make_translator()
            parts = [translator.translate(part) for part in _split_text(text)]
            if all(parts):
                return fix_astrology_terms(' '.join(parts))
        except Exception:
            continue
    return None


def get_horoscope_text(zodiac_sign):
    """Текст гороскопа из API Ninjas на русском; при ошибке запасной текст."""
    if not zodiac_sign:
        return FALLBACK_TEXT
    key = f'horoscope_ru:{zodiac_sign}:{timezone.localdate()}'
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
        text = response.json().get('horoscope')
    except (requests.RequestException, ValueError):
        return FALLBACK_TEXT
    if not text:
        return FALLBACK_TEXT
    translated = translate_to_russian(text)
    if not translated:
        return text
    cache.set(key, translated, 60 * 60 * 6)
    return translated


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