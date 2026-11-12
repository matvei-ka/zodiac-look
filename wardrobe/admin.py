from django import forms
from django.contrib import admin

from core.constants import MOOD_CHOICES

from .forms import OCCASION_CHOICES, SEASON_CHOICES
from .models import IdealLook, Look, Outfit, WardrobeItem


class IdealLookAdminForm(forms.ModelForm):
    occasion = forms.ChoiceField(label='Повод', choices=OCCASION_CHOICES)
    mood = forms.ChoiceField(
        label='Настроение', choices=[('', 'Любое')] + MOOD_CHOICES, required=False
    )
    season = forms.ChoiceField(
        label='Сезон', choices=[('', 'Любой')] + SEASON_CHOICES, required=False
    )

    class Meta:
        model = IdealLook
        fields = '__all__'


@admin.register(IdealLook)
class IdealLookAdmin(admin.ModelAdmin):
    form = IdealLookAdminForm
    list_display = ('title', 'occasion', 'mood', 'season', 'image_url')
    list_filter = ('occasion', 'mood', 'season')


admin.site.register(WardrobeItem)
admin.site.register(Look)
admin.site.register(Outfit)
