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

    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username or len(username.strip()) < 3:
            raise forms.ValidationError("Логин должен быть не менее 3 символов.")
        return username

    def clean_password2(self):
        # Проверка на пустой пароль и длину 
        password = self.cleaned_data.get('password2')
        if not password:
            raise forms.ValidationError("Пароль не может быть пустым.")
        if len(password) < 5:
            raise forms.ValidationError("Пароль должен быть не менее 5 символов.")
        return password