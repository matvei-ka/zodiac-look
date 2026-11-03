from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.constants import ZODIAC_CHOICES

from .models import User


class RegisterForm(UserCreationForm):
    zodiac_sign = forms.ChoiceField(label='Знак зодиака', choices=ZODIAC_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'zodiac_sign')
        labels = {'username': 'Логин'}