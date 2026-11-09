from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from forecasts.services import get_today_entry

from .forms import CATEGORY_CHOICES, OCCASION_CHOICES, SEASON_CHOICES, ItemForm
from .models import Look, LookItem, WardrobeItem
from .services import pick_outfit

OCCASIONS = dict(OCCASION_CHOICES)


@login_required
def wardrobe_list(request):
    """Список вещей пользователя с фильтрами по категории и сезону."""
    items = WardrobeItem.objects.filter(user=request.user).select_related('color')
    category = request.GET.get('category', '')
    season = request.GET.get('season', '')
    if category:
        items = items.filter(category=category)
    if season:
        items = items.filter(season=season)
    context = {
        'items': items,
        'category_choices': CATEGORY_CHOICES,
        'season_choices': SEASON_CHOICES,
        'selected_category': category,
        'selected_season': season,
    }
    return render(request, 'wardrobe/item_list.html', context)


@login_required
def item_add(request):
    form = ItemForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.save()
        messages.success(request, 'Вещь добавлена в гардероб.')
        return redirect('wardrobe:wardrobe_list')
    return render(request, 'wardrobe/item_form.html', {'form': form, 'title': 'Новая вещь'})


@login_required
def item_edit(request, pk):
    item = get_object_or_404(WardrobeItem, pk=pk, user=request.user)
    form = ItemForm(request.POST or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Изменения сохранены.')
        return redirect('wardrobe:wardrobe_list')
    return render(request, 'wardrobe/item_form.html', {'form': form, 'title': 'Изменить вещь'})


@login_required
@require_POST
def item_delete(request, pk):
    item = get_object_or_404(WardrobeItem, pk=pk, user=request.user)
    item.delete()
    messages.success(request, 'Вещь удалена.')
    return redirect('wardrobe:wardrobe_list')


@login_required
def stylist(request):
    """Умный стилист: подбор образа под цвет удачи, настроение и повод."""
    entry = get_today_entry(request.user)
    if entry is None:
        messages.info(request, 'Сначала выбери настроение, чтобы узнать цвет удачи.')
        return redirect('forecasts:forecast')

    if request.method == 'POST':
        occasion = request.POST.get('occasion')
        if occasion not in OCCASIONS:
            messages.error(request, 'Выбери повод из списка.')
            return redirect('wardrobe:stylist')

        selected, percentage, explanation = pick_outfit(request.user, occasion, entry)
        if not selected:
            messages.warning(request, 'В гардеробе нет вещей для подбора. Добавь хотя бы одну.')
            return redirect('wardrobe:wardrobe_list')

        # Несохранённые черновики прошлых подборов не копим
        Look.objects.filter(user=request.user, is_saved=False).delete()
        look = Look.objects.create(
            user=request.user,
            title=f'Образ: {OCCASIONS[occasion]}',
            occasion=occasion,
            color=entry.color,
            score=percentage,
            is_saved=False,
        )
        for row in selected:
            LookItem.objects.create(look=look, item=row['item'])
        entry.look = look
        entry.save(update_fields=['look'])

        return render(request, 'wardrobe/stylist_result.html', {
            'look': look,
            'rows': selected,
            'percentage': percentage,
            'occasion': OCCASIONS[occasion],
            'entry': entry,
        })

    return render(request, 'wardrobe/stylist.html', {'entry': entry, 'occasions': OCCASION_CHOICES})


@login_required
@require_POST
def look_save(request, pk):
    look = get_object_or_404(Look, pk=pk, user=request.user)
    look.is_saved = True
    look.save(update_fields=['is_saved'])
    messages.success(request, 'Образ сохранён ✨')
    return redirect('wardrobe:look_list')


@login_required
def look_list(request):
    """Сохранённые образы пользователя."""
    looks = Look.objects.filter(user=request.user, is_saved=True).prefetch_related('items')
    rows = [
        {
            'look': look,
            'occasion': OCCASIONS.get(look.occasion, look.occasion),
            'items': ', '.join(item.name for item in look.items.all()),
        }
        for look in looks
    ]
    return render(request, 'wardrobe/look_list.html', {'rows': rows})


@login_required
@require_POST
def look_delete(request, pk):
    look = get_object_or_404(Look, pk=pk, user=request.user)
    look.delete()
    messages.success(request, 'Образ удалён.')
    return redirect('wardrobe:look_list')
