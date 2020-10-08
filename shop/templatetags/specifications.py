from django import template
from django.utils.safestring import mark_safe


register = template.Library()

# Шаблоны таблицы характеристик товаров
TABLE_HEAD = """
                <table class="table">
                  <tbody>
             """

TABLE_TAIL = """
                  </tbody>
                </table>
             """

TABLE_CONTENT = """
                    <tr>
                      <td>{name}</td>
                      <td>{value}</td>
                    </tr>
                """

#TODO Сделать для остальных категорий
# Словари с названиями характеристик товаров
PRODUCT_SPEC = {
    'wobblers': {
        'Вес': 'weight',
        'Длинна': 'long',
        'Тип ловли': 'type_of_fishing',
        'Плавучесть': 'deepening',
        'Защита от зацепов': 'snag_protection',
        'Система дальнего заброса': 'long_distance_casting_system',
        'Страна производитель': 'manufacturer_country',
        'Тип плавучести': 'type_of_buoyancy',
        'Тип': 'type',
        'Шумовые эффекты': 'noise_effects',
    },
    'spoons': {
        'Вес': 'weight',
        'Длинна': 'long',
        'Тип ловли': 'type_of_fishing',
        'Защита от зацепов': 'snag_protection',
        'Система дальнего заброса': 'long_distance_casting_system',
        'Страна производитель': 'manufacturer_country',
        'Тип': 'type',
    },
}


def get_product_spec(product, model_name):
    """
    Достаём характеристики товара из PRODUCT_SPEC и записываем их в тело таблицы характеристик TABLE_CONTENT
    :param product: Наименование объекта в models.py
    :param model_name: Наименование товара в БД
    :return: table_content - заполненное тело таблицы характеристик
    """
    table_content = ''
    for name, value in PRODUCT_SPEC[model_name].items():
        table_content += TABLE_CONTENT.format(name=name, value=getattr(product, value))

    return table_content


@register.filter
def product_spec(product):
    """
    Генерируем готовую таблицу характеристик для определенного продукта
    :param product:  Наименование объекта в models.py
    :return: Заполненная таблица ГОЛОВА + ТЕЛО + ХВОСТ (Тело генерируется в функции get_product_spec, хвост и голова
             берутся из шаблонов TABLE_HEAD и TABLE_TAIL)
             Функция mark_safe представляет передаваемый текст как html код. Без неё на странице выведется
             текст с тегами
    """
    model_name = product.__class__._meta.model_name
    return mark_safe(TABLE_HEAD + get_product_spec(product, model_name) + TABLE_TAIL)