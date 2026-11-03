from .models import User


def register_user(username, password, zodiac_sign):
    """Создаёт пользователя с хешированным паролем."""
    return User.objects.create_user(
        username=username, password=password, zodiac_sign=zodiac_sign
    )