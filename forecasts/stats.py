"""Расчёты для страницы «Аудит»."""


def top_tied(counter):
    """Лидеры счётчика и их число. При равенстве возвращает всех лидеров."""
    if not counter:
        return [], 0
    best = max(counter.values())
    leaders = sorted(key for key, count in counter.items() if count == best)
    return leaders, best


def build_gradient(hex_codes):
    """CSS-фон: один цвет или градиент из нескольких цветов."""
    if not hex_codes:
        return '#eeeeee'
    if len(hex_codes) == 1:
        return hex_codes[0]
    return 'linear-gradient(90deg, ' + ', '.join(hex_codes) + ')'
