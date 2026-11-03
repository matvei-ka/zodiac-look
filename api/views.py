import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from core.constants import MOOD_CHOICES
from forecasts.services import get_horoscope_text, get_today_entry, save_forecast

from .serializers import entry_to_dict

VALID_MOODS = {code for code, _ in MOOD_CHOICES}


def _json(data, status=200):
    return JsonResponse(data, status=status, json_dumps_params={'ensure_ascii': False})


@require_http_methods(['GET', 'POST'])
def forecast(request):
    """GET: прогноз на сегодня. POST {"mood": "joy"}: создать или обновить прогноз."""
    if not request.user.is_authenticated:
        return _json({'error': 'Требуется вход'}, 401)

    if request.method == 'POST':
        try:
            mood = json.loads(request.body or '{}').get('mood')
        except ValueError:
            return _json({'error': 'Неверный JSON'}, 400)
        if mood not in VALID_MOODS:
            return _json(
                {'error': 'Неизвестное настроение', 'allowed': sorted(VALID_MOODS)}, 400
            )
        entry = save_forecast(request.user, mood)
        if entry is None:
            return _json({'error': 'В базе нет цветов удачи'}, 503)
    else:
        entry = get_today_entry(request.user)
        if entry is None:
            return _json({'error': 'Прогноз на сегодня ещё не создан'}, 404)

    text = get_horoscope_text(request.user.zodiac_sign)
    return _json(entry_to_dict(entry, text))