from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from .forms import RegisterForm
from .services import register_user


def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = register_user(
            form.cleaned_data['username'],
            form.cleaned_data['password1'],
            form.cleaned_data['zodiac_sign'],
        )
        login(request, user)
        return redirect('core:home')
    return render(request, 'accounts/register.html', {'form': form})


class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True