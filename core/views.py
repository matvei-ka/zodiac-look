from django.shortcuts import redirect, render


def home(request):
    """Главная: вошедшего пользователя ведём на «Сегодня», остальных на вход."""
    if request.user.is_authenticated:
        return redirect('forecasts:forecast')
    return redirect('accounts:login')


def help_page(request):
    return render(request, 'help.html')
