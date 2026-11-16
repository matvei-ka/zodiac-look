import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from wardrobe.models import IdealLook


class IdealDataTests(TestCase):
    def test_export_and_load_roundtrip(self):
        IdealLook.objects.create(
            occasion='walk', title='Городской образ',
            image='ideal_looks/city.jpg', description='Лёгкий лук',
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ideal_looks.json'
            with patch('wardrobe.management.commands.export_ideal_looks.IDEAL_DATA_FILE', path), \
                    patch('wardrobe.management.commands.load_ideal_looks.IDEAL_DATA_FILE', path):
                call_command('export_ideal_looks', stdout=StringIO())
                IdealLook.objects.all().delete()
                call_command('load_ideal_looks', stdout=StringIO())
                call_command('load_ideal_looks', stdout=StringIO())

        look = IdealLook.objects.get()
        self.assertEqual(look.title, 'Городской образ')
        self.assertEqual(look.image.name, 'ideal_looks/city.jpg')
        self.assertEqual(look.description, 'Лёгкий лук')
