from django.contrib import admin

from .models import Look, Outfit, WardrobeItem

admin.site.register(WardrobeItem)
admin.site.register(Look)
admin.site.register(Outfit)