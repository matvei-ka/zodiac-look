from django import forms

from core.constants import MOOD_CHOICES


class MoodForm(forms.Form):
    mood = forms.ChoiceField(
        label='Твоё настроение', choices=MOOD_CHOICES, widget=forms.RadioSelect
    )