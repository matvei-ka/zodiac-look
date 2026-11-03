def entry_to_dict(entry, horoscope_text):
    """Преобразует запись настроения в словарь для JSON."""
    return {
        'date': entry.entry_date.isoformat(),
        'mood': entry.mood,
        'mood_label': entry.get_mood_display(),
        'color': {
            'name': entry.color.name,
            'hex_code': entry.color.hex_code,
            'meaning': entry.color.meaning,
        },
        'horoscope': horoscope_text,
        'look_id': entry.look_id,
    }