from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import WardrobeItem, Look, LookItem
from forecasts.models import MoodEntry  # Если ошибка импорта — мы это исправим
from .services import pick_outfit

@login_required
def wardrobe_list(request):
    """Страница со списком вещей пользователя"""
    items = WardrobeItem.objects.filter(user=request.user)
    return render(request, 'wardrobe/wardrobe_list.html', {'items': items})

@login_required
def stylist(request):
    """Страница умного стилиста"""
    today = timezone.now().date()
    # Пытаемся найти настроение на сегодня
    mood_entry = MoodEntry.objects.filter(user=request.user, entry_date=today).first()
    
    # Если настроения нет, отправляем на главную (Участник 1 должен был настроить этот маршрут)
    # Если маршрут называется иначе, мы поменяем 'forecasts:today' на нужный
    if not mood_entry:
        return redirect('forecasts:today') 

    if request.method == 'POST':
        occasion = request.POST.get('occasion')
        
        # Подбираем образ
        selected, percentage, explanation = pick_outfit(request.user, occasion, mood_entry)
        
        # Сохраняем образ в БД (черновик)
        new_look = Look.objects.create(
            user=request.user,
            title=f"Образ для {occasion}",
            occasion=occasion,
            color=mood_entry.color,
            score=percentage,
            is_saved=False
        )
        
        # Привязываем вещи к образу
        for entry in selected:
            LookItem.objects.create(look=new_look, item=entry['item'])
        
        return render(request, 'wardrobe/stylist_result.html', {
            'look': new_look,
            'items': selected,
            'percentage': percentage,
            'explanation': explanation,
            'occasion': occasion,
        })
    
    return render(request, 'wardrobe/stylist.html')