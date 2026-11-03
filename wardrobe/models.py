from django.conf import settings
from django.db import models

from core.constants import MOOD_CHOICES


class WardrobeItem(models.Model):
    """Вещь из гардероба пользователя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wardrobe_items'
    )
    name = models.CharField('Название', max_length=100)
    category = models.CharField('Категория', max_length=20)
    color = models.ForeignKey('forecasts.Color', on_delete=models.PROTECT)
    season = models.CharField('Сезон', max_length=20)
    style = models.CharField('Стиль', max_length=20)

    class Meta:
        db_table = 'wardrobe_items'
        verbose_name = 'Вещь'
        verbose_name_plural = 'Вещи'

    def __str__(self):
        return self.name


class Look(models.Model):
    """Образ, собранный из вещей пользователя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='looks'
    )
    title = models.CharField('Название', max_length=100)
    occasion = models.CharField('Повод', max_length=30)
    color = models.ForeignKey(
        'forecasts.Color', null=True, blank=True, on_delete=models.PROTECT
    )
    score = models.SmallIntegerField('Оценка', default=0)
    is_saved = models.BooleanField('Сохранён', default=False)
    last_worn_date = models.DateField('Когда надевал', null=True, blank=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    items = models.ManyToManyField(
        WardrobeItem, through='LookItem', related_name='looks'
    )

    class Meta:
        db_table = 'looks'
        ordering = ['-created_at']
        verbose_name = 'Образ'
        verbose_name_plural = 'Образы'

    def __str__(self):
        return self.title


class LookItem(models.Model):
    """Связь образа и вещи (таблица look_items)."""

    look = models.ForeignKey(Look, on_delete=models.CASCADE)
    item = models.ForeignKey(WardrobeItem, on_delete=models.CASCADE)

    class Meta:
        db_table = 'look_items'
        constraints = [
            models.UniqueConstraint(fields=['look', 'item'], name='unique_look_item')
        ]


class Outfit(models.Model):
    """Готовый образ-шаблон для подбора по настроению."""

    title = models.CharField('Название', max_length=100)
    items = models.TextField('Состав')
    mood = models.CharField('Настроение', max_length=20, choices=MOOD_CHOICES)
    color = models.ForeignKey('forecasts.Color', on_delete=models.PROTECT)

    class Meta:
        db_table = 'outfits'
        verbose_name = 'Готовый образ'
        verbose_name_plural = 'Готовые образы'

    def __str__(self):
        return self.title