from collections import Counter

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.constants import MOOD_CHOICES

from .forms import MoodForm
from .models import MoodEntry
from .services import get_horoscope_text, get_today_entry, save_forecast


@login_required
def forecast(request):
    """Страница «Сегодня»: выбор настроения и прогноз дня."""
    if request.method == 'POST':
        form = MoodForm(request.POST)
        if form.is_valid():
            entry = save_forecast(request.user, form.cleaned_data['mood'])
            if entry is None:
                messages.error(
                    request,
                    'Цветов удачи пока нет в базе. Выполни: python manage.py seed_data',
                )
            return redirect('forecasts:forecast')
        messages.error(request, 'Выбери настроение из списка.')
    entry = get_today_entry(request.user)
    context = {
        'moods': MOOD_CHOICES,
        'entry': entry,
        'horoscope_text': get_horoscope_text(request.user.zodiac_sign) if entry else None,
    }
    return render(request, 'forecasts/forecast.html', context)


@login_required
def history(request):
    """История прогнозов и простая статистика."""
    entries = list(
        MoodEntry.objects.filter(user=request.user).select_related('color', 'look')
    )
    labels = dict(MOOD_CHOICES)
    moods = Counter(entry.mood for entry in entries)
    colors = Counter(entry.color.name for entry in entries)
    context = {
        'entries': entries,
        'total': len(entries),
        'top_mood': labels.get(moods.most_common(1)[0][0]) if moods else None,
        'top_color': colors.most_common(1)[0][0] if colors else None,
        'mood_stats': [(labels.get(code, code), count) for code, count in moods.most_common()],
    }
    return render(request, 'forecasts/history.html', context)
