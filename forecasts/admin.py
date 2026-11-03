from django.contrib import admin

from .models import Color, MoodEntry

admin.site.register(Color)
admin.site.register(MoodEntry)