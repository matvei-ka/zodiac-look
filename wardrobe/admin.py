from django import forms
from django.contrib import admin

from .forms import OCCASION_CHOICES
from .models import IdealLook, Look, Outfit, WardrobeItem


class IdealLookAdminForm(forms.ModelForm):
    occasion = forms.ChoiceField(label='Повод', choices=OCCASION_CHOICES)

    class Meta:
        model = IdealLook
        fields = ('occasion', 'title', 'image', 'image_url', 'description')

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('image') and not cleaned.get('image_url'):
            raise forms.ValidationError('Загрузи файл или укажи ссылку на картинку.')
        return cleaned


@admin.register(IdealLook)
class IdealLookAdmin(admin.ModelAdmin):
    form = IdealLookAdminForm
    list_display = ('title', 'occasion')
    list_filter = ('occasion',)


admin.site.register(WardrobeItem)
admin.site.register(Look)
admin.site.register(Outfit)
