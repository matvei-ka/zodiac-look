from django.utils import timezone

from .models import IdealLook


def current_season(today=None):
    """Текущий сезон по дате: зима, лето или демисезон."""
    month = (today or timezone.localdate()).month
    if month in (12, 1, 2):
        return 'зима'
    if month in (6, 7, 8):
        return 'лето'
    return 'демисезон'


def pick_ideal_looks(occasion, mood, season=None, limit=4):
    """Идеальные образы повода, подходящие под настроение и сезон.

    Пустое настроение или сезон у образа значит «подходит всегда».
    Если подходящих нет, показываем то, что есть для повода.
    """
    season = season or current_season()
    scored = []
    for look in IdealLook.objects.filter(occasion=occasion):
        if not look.mood:
            mood_score = 1
        else:
            mood_score = 2 if look.mood == mood else 0
        if not look.season or look.season == 'всесезонный':
            season_score = 1
        else:
            season_score = 2 if look.season == season else 0
        scored.append((mood_score, season_score, look))

    fitting = [row for row in scored if row[0] and row[1]]
    rows = fitting or scored
    rows.sort(key=lambda row: (-(row[0] + row[1]), row[2].id))
    return [row[2] for row in rows[:limit]]
