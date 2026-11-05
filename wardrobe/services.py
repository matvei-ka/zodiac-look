from .models import WardrobeItem, Look, LookItem
from forecasts.models import MoodEntry # Убедись, что модель MoodEntry лежит здесь!
from django.utils import timezone


def calculate_item_score(item, lucky_color_id, mood, occasion):
    """Считает баллы для одной вещи"""
    score = 0
    reasons = []

    # 1. Совпадение с цветом удачи (40 баллов)
    if item.color_id == lucky_color_id:
        score += 40
        reasons.append("совпадает с цветом удачи")

    # 2. Совпадение с поводом (30 баллов)
    if item.style == occasion:
        score += 30
        reasons.append("подходит под повод")

    # 3. Совпадение с настроением (15 баллов)
    # Сравниваем настроение вещи (если есть) или просто даём балл за универсальность
    # (Предполагаем, что у модели Color есть поле mood)
    if item.color and item.color.mood == mood:
        score += 15
        reasons.append("соответствует настроению")

    # 4. Сезон (15 баллов)
    if item.season in ['всесезонный', 'лето']: # Упрощённо
        score += 15
        reasons.append("подходит по сезону")

    return score, reasons


def pick_outfit(user, occasion, mood_entry):
    """Подбирает лучший образ из вещей пользователя"""
    items = WardrobeItem.objects.filter(user=user)
    lucky_color_id = mood_entry.color_id if mood_entry else None
    mood = mood_entry.mood if mood_entry else None

    scored_items = []
    for item in items:
        score, reasons = calculate_item_score(item, lucky_color_id, mood, occasion)
        scored_items.append({
            'item': item,
            'score': score,
            'reasons': reasons
        })

    # Сортируем по убыванию баллов
    scored_items.sort(key=lambda x: x['score'], reverse=True)

    # Собираем образ по категориям
    categories = ['верх', 'низ', 'обувь', 'аксессуар']
    selected = []
    used_ids = set()

    for cat in categories:
        for entry in scored_items:
            if entry['item'].category == cat and entry['item'].id not in used_ids:
                selected.append(entry)
                used_ids.add(entry['item'].id)
                break

    # Считаем процент
    total_score = sum([entry['score'] for entry in selected])
    max_possible = len(categories) * 100 
    percentage = int((total_score / max_possible) * 100) if max_possible > 0 else 0

    # Пояснение
    explanation = []
    for entry in selected:
        reason_text = ", ".join(entry['reasons']) if entry['reasons'] else "подходит по категории"
        explanation.append(f"{entry['item'].name} ({reason_text})")

    return selected, percentage, explanation