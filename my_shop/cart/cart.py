from decimal import Decimal
from django.conf import settings

from shop.models import Product


class Cart:
    """Класс управления корзиной покупок"""
    def __init__(self, request):
        """Инициализация сеанса и корзины внутри него"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # сохранить пустую корзину в сеансе
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """Добавить товар в корзину либо обновить его количество"""
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        """Пометка сеанса как измененного для его сохранения"""
        self.session.modified = True

    def remove(self, product):
        """Удаление товар из корзины"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Прокрутка товарных позиций в цикле и получение товаров
        из базы данных.
        """
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Подсчет количества товарных позиций в корзине"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Подсчет общей стоимости товаров в корзине"""
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def clear(self):
        """Удалить корзину из сеанса"""
        del self.session[settings.CART_SESSION_ID]
        self.save()

