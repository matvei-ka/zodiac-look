from django import forms
from django.contrib import admin

from .forms import OCCASION_CHOICES
from .models import IdealLook, Look, Outfit, WardrobeItem


class IdealLookAdminForm(forms.ModelForm):
    occasion = forms.ChoiceField(label='Повод', choices=OCCASION_CHOICES)

    class Meta:
        model = IdealLook
        fields = '__all__'


@admin.register(IdealLook)
class IdealLookAdmin(admin.ModelAdmin):
    form = IdealLookAdminForm
    list_display = ('title', 'occasion', 'image_url')
    list_filter = ('occasion',)


admin.site.register(WardrobeItem)
admin.site.register(Look)
admin.site.register(Outfit)
