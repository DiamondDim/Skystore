from django.core.cache import cache
from .models import Product


def get_products_by_category(category_id: int):
    """
    Возвращает список опубликованных продуктов указанной категории.
    Реализует низкоуровневое кеширование с ключом category_{id} и TTL 15 минут.
    """
    cache_key = f'category_{category_id}'
    products = cache.get(cache_key)

    if products is None:
        print(f"🔴 [БАЗА ДАННЫХ] Выполняем запрос к БД для категории {category_id}")
        products = list(Product.objects.filter(category_id=category_id, is_published=True))
        cache.set(cache_key, products, 60 * 15)
    else:
        print(f"🟢 [КЕШ] Данные для категории {category_id} успешно получены из Redis!")

    return products


def get_all_products():
    """
    Возвращает список всех опубликованных продуктов.
    Реализует низкоуровневое кеширование с ключом 'all_products_list' и TTL 15 минут.
    """
    cache_key = 'all_products_list'
    products = cache.get(cache_key)

    if products is None:
        print("🔴 [БАЗА ДАННЫХ] Выполняем запрос к БД для всех опубликованных продуктов")
        products = list(Product.objects.filter(is_published=True).select_related('category'))
        cache.set(cache_key, products, 60 * 15)
    else:
        print(" 🟢[КЕШ] Список всех продуктов успешно получен из Redis!")

    return products


def get_product_by_id(product_id: int):
    """
    Возвращает один продукт по ID.
    Реализует низкоуровневое кеширование с ключом product_{id} и TTL 15 минут.
    """
    cache_key = f'product_{product_id}'
    product = cache.get(cache_key)

    if product is None:
        print(f"🔴 [БАЗА ДАННЫХ] Выполняем запрос к БД для продукта {product_id}")
        try:
            product = Product.objects.select_related('category').get(id=product_id)
            cache.set(cache_key, product, 60 * 15)
        except Product.DoesNotExist:
            product = None
    else:
        print(f"🟢 [КЕШ] Продукт {product_id} успешно получен из Redis!")

    return product


def invalidate_product_cache(product_id: int, category_id: int = None):
    """
    Очищает кеш для продукта, списка всех продуктов и категории (если передана).
    Вызывается при изменении, удалении или публикации продукта.
    """
    # Очищаем кеш конкретного продукта
    cache.delete(f'product_{product_id}')
    print(f"🗑️ [КЕШ] Очищен кеш для продукта {product_id}")

    # Очищаем кеш общего списка (он мог измениться)
    cache.delete('all_products_list')
    print("️ 🗑️ [КЕШ] Очищен кеш списка всех продуктов")

    # Очищаем кеш категории, если продукт принадлежит категории
    if category_id:
        cache.delete(f'category_{category_id}')
        print(f"🗑️ [КЕШ] Очищен кеш для категории {category_id}")
