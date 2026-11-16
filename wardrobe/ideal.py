from pathlib import Path

from .models import IdealLook

# Файл с идеальными образами, который лежит в репозитории и грузится на любом компьютере
IDEAL_DATA_FILE = Path(__file__).resolve().parent / 'data' / 'ideal_looks.json'


def pick_ideal_looks(occasion, limit=4):
    """Идеальные образы для выбранного повода."""
    return list(IdealLook.objects.filter(occasion=occasion)[:limit])
