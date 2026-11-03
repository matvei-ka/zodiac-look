from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import MoodForm
from .services import get_horoscope_text, get_today_entry, save_forecast


@login_required
def forecast(request):
    if request.method == 'POST':
        form = MoodForm(request.POST)
        if form.is_valid():
            entry = save_forecast(request.user, form.cleaned_data['mood'])
            if entry is None:
                messages.error(request, 'Цветов удачи пока нет в базе.')
            return redirect('forecasts:forecast')
    else:
        form = MoodForm()
    entry = get_today_entry(request.user)
    context = {
        'form': form,
        'entry': entry,
        'horoscope_text': get_horoscope_text(request.user.zodiac_sign) if entry else None,
    }
    return render(request, 'forecasts/forecast.html', context)