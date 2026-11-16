import json

from django.core.management.base import BaseCommand, CommandError

from wardrobe.ideal import IDEAL_DATA_FILE
from wardrobe.models import IdealLook


class Command(BaseCommand):
    help = 'Загружает идеальные образы из файла wardrobe/data/ideal_looks.json'

    def handle(self, *args, **options):
        if not IDEAL_DATA_FILE.exists():
            raise CommandError(f'Файл не найден: {IDEAL_DATA_FILE}')
        rows = json.loads(IDEAL_DATA_FILE.read_text(encoding='utf-8'))
        for row in rows:
            look = IdealLook.objects.filter(
                occasion=row['occasion'], title=row['title']
            ).first() or IdealLook(occasion=row['occasion'], title=row['title'])
            look.image = row.get('image', '')
            look.image_url = row.get('image_url', '')
            look.description = row.get('description', '')
            look.save()
        self.stdout.write(self.style.SUCCESS(f'Загружено образов: {len(rows)}'))
