import json

from django.core.management.base import BaseCommand

from wardrobe.ideal import IDEAL_DATA_FILE
from wardrobe.models import IdealLook


class Command(BaseCommand):
    help = 'Сохраняет идеальные образы в файл wardrobe/data/ideal_looks.json'

    def handle(self, *args, **options):
        rows = [
            {
                'occasion': look.occasion,
                'title': look.title,
                'image': look.image.name if look.image else '',
                'image_url': look.image_url,
                'description': look.description,
            }
            for look in IdealLook.objects.all()
        ]
        IDEAL_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        IDEAL_DATA_FILE.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        self.stdout.write(self.style.SUCCESS(f'Сохранено образов: {len(rows)}'))
