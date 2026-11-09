from django import forms

from .models import WardrobeItem

CATEGORY_CHOICES = [
    ('верх', 'Верх'),
    ('низ', 'Низ'),
    ('обувь', 'Обувь'),
    ('аксессуар', 'Аксессуар'),
]
SEASON_CHOICES = [
    ('лето', 'Лето'),
    ('зима', 'Зима'),
    ('демисезон', 'Демисезон'),
    ('всесезонный', 'Всесезонный'),
]
OCCASION_CHOICES = [
    ('прогулка', 'Прогулка'),
    ('работа', 'Работа или учёба'),
    ('свидание', 'Свидание'),
    ('вечеринка', 'Вечеринка'),
    ('дом', 'Дом'),
]


class ItemForm(forms.ModelForm):
    category = forms.ChoiceField(label='Категория', choices=CATEGORY_CHOICES)
    season = forms.ChoiceField(label='Сезон', choices=SEASON_CHOICES)
    style = forms.ChoiceField(label='Стиль (повод)', choices=OCCASION_CHOICES)

    class Meta:
        model = WardrobeItem
        fields = ('name', 'category', 'color', 'season', 'style')
        labels = {'name': 'Название', 'color': 'Цвет'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].empty_label = 'Выбери цвет'
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs['class'] = css
