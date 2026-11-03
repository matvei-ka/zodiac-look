from django.conf import settings
from django.db import models

from core.constants import MOOD_CHOICES


class Color(models.Model):
    """Цвет удачи."""

    name = models.CharField('Название', max_length=30, unique=True)
    hex_code = models.CharField('HEX-код', max_length=7)
    meaning = models.CharField('Значение', max_length=255)
    mood = models.CharField('Настроение', max_length=20, choices=MOOD_CHOICES)

    class Meta:
        db_table = 'colors'
        verbose_name = 'Цвет'
        verbose_name_plural = 'Цвета'

    def __str__(self):
        return self.name


class MoodEntry(models.Model):
    """История настроений: настроение дня, цвет удачи и образ дня."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_entries'
    )
    entry_date = models.DateField('Дата')
    mood = models.CharField('Настроение', max_length=20, choices=MOOD_CHOICES)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    look = models.ForeignKey(
        'wardrobe.Look',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='mood_entries',
    )

    class Meta:
        db_table = 'mood_entries'
        ordering = ['-entry_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'entry_date'], name='unique_mood_entry_per_day'
            )
        ]
        verbose_name = 'Запись настроения'
        verbose_name_plural = 'Записи настроения'

    def __str__(self):
        return f'{self.user} — {self.entry_date}'