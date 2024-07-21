import redis
from django.conf import settings
from .models import Product

# соединить с redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


class Recommender:
    def get_product_key(self, id):
        """
        Возвращает ключ для хранения данных о товарах,
        купленных вместе с данным товаром.
        """
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        """
        Увеличивает баллы товаров, которые были куплены вместе.
        Для каждого товара увеличивает баллы всех других товаров,
        которые были куплены вместе с ним.
        """
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # получить другие товары, купленные
                # с каждым товаром
                if product_id != with_id:
                    # увеличить бал товара в sorted set
                    # купленного вместе c целевым товаром
                    r.zincrby(self.get_product_key(product_id),
                              1, with_id)

    def suggest_products_for(self, products, max_results=6):
        """
        Рекомендует товары на основе товаров, которые были куплены
        вместе с указанными.
        Если указан один товар, возвращает товары, купленные с ним.
        Если указано несколько товаров, объединяет их баллы и возвращает
        лучшие результаты.
        """
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # Только один товар
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]),
                0, -1, desc=True)[:max_results]
        else:
            # Создание временного ключа
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = f'tmp_{flat_ids}'
            # Объединение всех баллов у всех товаров
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            # Удаление идентификаторов товаров, для которых дается рекомендация
            r.zrem(tmp_key, *product_ids)
            # Получение идентификаторов товаров по их количеству,
            # сортировка по убыванию
            suggestions = r.zrange(tmp_key, 0, -1,
                                   desc=True)[:max_results]
            # Удаление временного ключа
            r.delete(tmp_key)
        suggested_products_ids = [int(id) for id in suggestions]
        # Получение и сортировка предлагаемых товаров по порядку их появления
        suggested_products = list(Product.objects.filter(
            id__in=suggested_products_ids))
        suggested_products.sort(
            key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products

    def clear_purchases(self):
        """
        Очищает все данные о покупках, удаляя ключи для всех товаров.
        """
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))


