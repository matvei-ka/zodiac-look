from collections import Counter

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.constants import MOOD_CHOICES

from .forms import MoodForm
from wardrobe.models import WardrobeItem

from .models import MoodEntry
from .services import get_horoscope_text, get_today_entry, save_forecast
from .stats import build_gradient, top_tied


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
def audit(request):
    """Аудит настроения и гардероба: лидеры, палитра дней, пробелы в гардеробе."""
    entries = list(
        MoodEntry.objects.filter(user=request.user)
        .select_related('color', 'look')
        .order_by('entry_date')
    )
    labels = dict(MOOD_CHOICES)
    total = len(entries)

    mood_counter = Counter(entry.mood for entry in entries)
    top_mood_codes, _ = top_tied(mood_counter)
    top_moods = [labels.get(code, code) for code in top_mood_codes]

    colors_by_id = {entry.color_id: entry.color for entry in entries}
    color_counter = Counter(entry.color_id for entry in entries)
    top_color_ids, top_color_count = top_tied(color_counter)
    top_colors = [colors_by_id[color_id] for color_id in top_color_ids]
    gradient = build_gradient([color.hex_code for color in top_colors])

    mood_bars = [
        {
            'label': labels.get(code, code),
            'count': count,
            'percent': round(count * 100 / total) if total else 0,
        }
        for code, count in mood_counter.most_common()
    ]

    wardrobe = WardrobeItem.objects.filter(user=request.user)
    color_coverage = [
        {'color': color, 'count': wardrobe.filter(color=color).count()}
        for color in top_colors
    ]
    unused_items = list(wardrobe.filter(looks__isnull=True).select_related('color')[:6])

    context = {
        'total': total,
        'top_moods': top_moods,
        'top_colors': top_colors,
        'top_color_count': top_color_count,
        'is_tie': len(top_colors) > 1,
        'gradient': gradient,
        'mood_bars': mood_bars,
        'ribbon': entries[-30:],
        'recent': list(reversed(entries[-8:])),
        'color_coverage': color_coverage,
        'wardrobe_total': wardrobe.count(),
        'unused_items': unused_items,
    }
    return render(request, 'forecasts/audit.html', context)
