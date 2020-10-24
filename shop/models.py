from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from django.utils import timezone


User = get_user_model()


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]


def get_model_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname=viewname, kwargs={'ct_model': ct_model, 'slug': obj.slug})



class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_categories_count(self):
        models = get_models_for_count('wobblers', 'spoons')
        qs = list(self.get_queryset().annotate(*models))
        data = [
            dict(name=c.name, url=c.get_absolute_url())
            for c in qs
        ]
        return data



class LatestProductsManager:

    @staticmethod
    def get_products_for_main_page(*args, **kwargs):
        with_respect_to = kwargs.get('with_respect_to')
        products = []
        ct_models = ContentType.objects.filter(model__in=args)
        for ct_model in ct_models:
            model_products = ct_model.model_class()._base_manager.all().order_by('-id')[:3]
            products.extend(model_products)
        if with_respect_to:
            ct_model = ContentType.objects.filter(model=with_respect_to)
            if ct_model.exists():
                if with_respect_to in args:
                    return sorted(
                        products,
                        key=lambda x: x.__class__._meta.model_name.startswith(with_respect_to),
                        reverse=True
                    )
        return products


class LatestProducts:

    objects = LatestProductsManager()



# Модели БД

class CartProduct(models.Model):
    """ Товары в корзине
    """
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey(
        'Cart',
        verbose_name='Корзина',
        related_name='related_products',
        on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qty = models.PositiveIntegerField(default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Итоговая цена')

    class Meta:
        verbose_name = '- Товары в корзинах -'
        verbose_name_plural = '- Товары в корзинах -'

    def __str__(self):
        return "Товар {} (для корзины)".format(self.content_object.name)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.content_object.price
        super().save(*args, **kwargs)

    def get_model_name(self):
        return self.__class__._meta.model_name



class Cart(models.Model):
    """ Корзина
    """
    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_card')
    total_product = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Итоговая цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    class Meta:
        verbose_name = '- Корзина -'
        verbose_name_plural = '- Корзины -'

    def __str__(self):
        return str(self.id)




class Customer(models.Model):
    """ Покупатель
    """
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', null=True, blank=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_customer')

    class Meta:
        verbose_name = '- Покупатель -'
        verbose_name_plural = '- Покупатели -'

    def __str__(self):
        return 'Покупатель: {} {}'.format(self.user.first_name, self.user.last_name)



class Order(models.Model):
    """ Заказ
    """
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'in_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = {
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен'),
    }

    BUYING_TYPE_CHOICES = {
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка'),
    }

    customer = models.ForeignKey(
        Customer,
        verbose_name='Покупатель',
        related_name='related_orders',
        on_delete=models.CASCADE
    )
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    phone = models.CharField(max_length=255, verbose_name='Телефон')
    address = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(max_length=100, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(
        max_length=100,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_DELIVERY
    )
    comment = models.TextField(verbose_name='Комментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = '- Заказ -'
        verbose_name_plural = '- Заказы -'

    def __str__(self):
        return str(self.id)


# Модели категорий товаров

class ParentCategory(models.Model):
    """ Общие (родительские) категории товаров
    """
    name = models.CharField(max_length=200, db_index=True, verbose_name='Имя')
    slug = models.SlugField(max_length=200, db_index=True, unique=True, verbose_name='Адрес')
    description = models.TextField(blank=True, verbose_name='Описание')
    objects = CategoryManager()

    class Meta:
        ordering = ('name',)
        verbose_name = '-- Категория --'
        verbose_name_plural = '-- Категории --'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('parent_category', kwargs={'slug': self.slug})



class Category(models.Model):
    """ Категории товаров
    """
    category = models.ForeignKey(
        ParentCategory,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Категория'
    )
    name = models.CharField(max_length=200, db_index=True, verbose_name='Имя')
    slug = models.SlugField(max_length=200, db_index=True, unique=True, verbose_name='Адрес')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='products/images', blank=True, verbose_name='Изображение')
    objects = CategoryManager()

    class Meta:
        ordering = ('name',)
        verbose_name = '-- Подкатегория --'
        verbose_name_plural = '-- Подкатегории --'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


# Модели товаров

class Product(models.Model):
    """ Абстрактный класс продукции с общими полями
    """
    class Meta:
        abstract = True

    product_key = models.PositiveIntegerField(verbose_name='Код товара')
    name = models.CharField(max_length=200, db_index=True, verbose_name='Имя')
    slug = models.SlugField(max_length=200, db_index=True, unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    stock = models.PositiveIntegerField(verbose_name='Остаток')
    available = models.BooleanField(default=True, verbose_name='Доступно')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return self.name

    def get_model_name(self):
        return self.__class__.__name__.lower()



class Wobblers(Product):
    """ Воблеры
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='wobblers',
        verbose_name='Категория'
    )
    weight = models.FloatField(verbose_name='Вес')
    long = models.FloatField(verbose_name='Длинна')
    type_of_fishing = models.CharField(max_length=200, db_index=True, verbose_name='Тип ловли')
    deepening = models.FloatField(verbose_name='Плавучесть')
    snag_protection = models.BooleanField(default=False, verbose_name='Защита от зацепов')
    long_distance_casting_system = models.BooleanField(default=False, verbose_name='Система дальнего заброса')
    manufacturer_country = models.CharField(max_length=200, db_index=True, verbose_name='Страна производитель')
    type_of_buoyancy = models.CharField(max_length=200, db_index=True, verbose_name='Тип плавучести')
    type = models.CharField(max_length=200, db_index=True, verbose_name='Тип')
    noise_effects = models.BooleanField(default=False, verbose_name='Шумовые эффекты')
    image = models.ImageField(upload_to='products/images/wobblers', blank=True, verbose_name='Изображение')


    class Meta:
        ordering = ('name',)
        verbose_name = 'Воблер'
        verbose_name_plural = 'Воблеры'
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return get_model_url(self, 'product_detail')



class Spoons(Product):
    """ Блесны
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='spoons',
        verbose_name='Категория'
    )
    weight = models.FloatField(verbose_name='Вес')
    long = models.PositiveIntegerField(verbose_name='Длинна')
    type_of_fishing = models.CharField(max_length=200, db_index=True, verbose_name='Тип ловли')
    snag_protection = models.BooleanField(default=False, verbose_name='Защита от зацепов')
    long_distance_casting_system = models.BooleanField(default=False, verbose_name='Система дальнего заброса')
    manufacturer_country = models.CharField(max_length=200, db_index=True, verbose_name='Страна производитель')
    type = models.CharField(max_length=200, db_index=True, verbose_name='Тип')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    image = models.ImageField(upload_to='products/images/spoons', blank=True, verbose_name='Изображение')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Блесна'
        verbose_name_plural = 'Блесны'
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return get_model_url(self, 'product_detail')


#TODO Заполнить оставшиеся категории товаров
class SpinningRods(Product):
    """ Спиннинговые удилища
    """
    pass



class WinterFishing(Product):
    """ Аксессуары для зимней рыбалки
    """
    pass



class Libras(Product):
    """ Весы
    """
    pass



class DryAdditives(Product):
    """ Добавки сухие
    """
    pass



class CoilsInertial(models.Model):
    """ Инерционные катушки
    """
    pass



class Hooks(Product):
    """ Крючки
    """
    pass



class LineMonofilament(Product):
    """ Леска монофильная
    """
    pass



class CoilsMulty(Product):
    """ Мультипликаторные катушки
    """
    pass



class Leashes(Product):
    """ Поводки
    """
    pass



class Floats(Product):
    """ Поплавки
    """
    pass



class SlingShots(Product):
    """ Рогатки
    """
    pass