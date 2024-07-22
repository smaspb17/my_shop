from django import template

register = template.Library()


@register.filter
def pluralize_ru(value, arg=''):
    """
    Фильтр для склонения слов во множественном числе в русском языке.
    Использование:
    {{ total_items|pluralize_ru:"товар,товара,товаров" }}
    """
    words = arg.split(',')
    if len(words) != 3:
        raise ValueError(
            'Аргумент фильтра должен содержать 3 слова, разделенных запятыми'
            )
    value = abs(int(value))
    if value % 10 == 1 and value % 100 != 11:
        return f"{value} {words[0]}"
    elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
        return f"{value} {words[1]}"
    else:
        return f"{value} {words[2]}"
