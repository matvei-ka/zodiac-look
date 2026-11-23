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
    ('walk', 'Прогулка по городу'),
    ('home', 'Уютный вечер дома'),
    ('work', 'Деловая встреча'),
    ('shopping', 'Шопинг и обновки'),
    ('productive', 'День продуктивности'),
    ('party', 'Выход в свет'),
    ('spontaneous', 'Спонтанная прогулка'),
    ('important', 'Важное событие'),
]


class ItemForm(forms.ModelForm):
    category = forms.ChoiceField(label='Категория', choices=CATEGORY_CHOICES)
    season = forms.ChoiceField(label='Сезон', choices=SEASON_CHOICES)
    style = forms.ChoiceField(label='Стиль (повод)', choices=OCCASION_CHOICES)

    class Meta:
        model = WardrobeItem
        fields = ('name', 'image', 'category', 'color', 'season', 'style')
        labels = {'name': 'Название', 'color': 'Цвет'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['color'].empty_label = 'Выбери цвет'
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs['class'] = css

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError("Название вещи должно быть не короче 2 символов и не может быть пустым.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('category'):
            raise forms.ValidationError("Выберите категорию одежды.")
        if not cleaned_data.get('season'):
            raise forms.ValidationError("Выберите сезон.")
        return cleaned_data