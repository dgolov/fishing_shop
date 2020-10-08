from django.db import transaction
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

from .mixins import CategoryDetailMixin, CartMixin, CategoryMixin
from .forms import OrderForm
from .utils import recalc_cart
from .models import (
    Category, LatestProducts, Customer, CartProduct, Wobblers, Spoons, WinterFishing, SpinningRods, Libras,
    DryAdditives, CoilsInertial, LineMonofilament, CoilsMulty, Leashes, Floats, SlingShots, Hooks,
)



class BaseView(CategoryMixin, CartMixin, View):
    """ Базовый класс представлений
    """
    title = 'Sniper Fish интернет магазин'
    url = 'shop/index.html'

    def get(self, request, *args, **kwargs):
        context = {
                'parent_category': self.parent_category,
                'category': self.category,
                'title': self.title,
                'cart': self.cart,
                'user': self.user
        }
        return render(request, self.url, context)



class AboutUsView(BaseView):
    """ Представление главной Контакты (О нас)
    """
    def __init__(self):
        self.title = 'O нас'
        self.url = 'shop/about_us.html'
        super(AboutUsView, self).__init__()



class HelpView(BaseView):
    """ Представление страницы Помощи
    """
    def __init__(self):
        self.title = 'Помощь'
        self.url = 'shop/dev.html'
        super(HelpView, self).__init__()



class NewsView(BaseView):
    """ Представление страницы Помощи
    """
    def __init__(self):
        self.title = 'Новости'
        self.url = 'shop/dev.html'
        super(NewsView, self).__init__()



class PayShipView(BaseView):
    """ Представление страницы Оплыта и доставка
    """
    def __init__(self):
        self.title = 'Оплата и доставка'
        self.url = 'shop/dev.html'
        super(PayShipView, self).__init__()



class PromotionsView(BaseView):
    """ Представление страницы Акции
    """
    def __init__(self):
        self.title = 'Акции'
        self.url = 'shop/dev.html'
        super(PromotionsView, self).__init__()



class PersonalView(CategoryMixin, CartMixin, View):
    """ Представление страницы Личный кабинет
    """
    def __init__(self):
        self.title = 'Личный кабинет'
        self.url = 'shop/dev.html'
        super(PersonalView, self).__init__()



class MainView(CategoryMixin, CartMixin, View):
    """ Представление главной страницы
    """
    def get(self, request, *args, **kwargs):
        products = LatestProducts.objects.get_products_for_main_page('wobblers', 'spoons')
        context = {
                'parent_category': self.parent_category,
                'category': self.category,
                'products': products,
                'title': "Sniper Fish интернет магазин",
                'cart': self.cart,
                'user': self.user
        }
        return render(request, 'shop/index.html', context)



class CategoryView(BaseView):
    """ Представление общего раздела категорий (Каталог)
    """
    def __init__(self):
        self.title = 'Каталог товаров'
        self.url = 'shop/categories.html'
        super(CategoryView, self).__init__()



class CartView(BaseView):
    """ Представление корзины
    """
    def __init__(self):
        self.title = 'Корзина'
        self.url = 'shop/cart.html'
        super(CartView, self).__init__()



class CheckoutView(CategoryMixin, CartMixin, View):
    """ Представление оформления заказа
    """
    def get(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        context = {
            'parent_category': self.parent_category,
            'cart': self.cart,
            "category": self.category,
            'title': "Оформление заказа",
            'form': form,
            'user': self.user
        }
        return render(request, 'shop/checkout.html', context)



class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(
                request,
                messages.INFO,
                'Спасибо за заказ! В близжайшее время с вами свяжется менеджер'
            )
            return  HttpResponseRedirect('/')
        return  HttpResponseRedirect('/checkout/')


class AddToCartView(CartMixin, View):
    """ Добавление товара в корзину
    """

    def get(self, request, *args, **kwargs):
        path = request.META['HTTP_REFERER']
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product, created = CartProduct.objects.get_or_create(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id,
        )
        if created:
            self.cart.products.add(cart_product)

        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно добавлен')

        return HttpResponseRedirect(path)



class ChangeQTYView(CartMixin, View):
    """ Изменение колличества товара в корзине
    """
    def post(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id,
        )
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Колличество успешно изменено')

        return HttpResponseRedirect('/cart')



class DeleteFromCartView(CartMixin, View):
    """ Удаление товара из корзины
    """
    def get(self, request, *args, **kwargs):
        ct_model, product_slug = kwargs.get('ct_model'), kwargs.get('slug')
        content_type = ContentType.objects.get(model=ct_model)
        product = content_type.model_class().objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, content_type=content_type, object_id=product.id,
        )
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно удален')

        return HttpResponseRedirect('/cart')



class CategoryDetailView(CartMixin, CategoryDetailMixin, DetailView):
    """ Представление раздела конкретной категории
    """
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'categories'
    template_name = 'shop/category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        context['user'] = self.user
        return context



class ProductDetailView(CartMixin, DetailView):
    """ Представление раздела конкретного товара
    """
    CT_MODEL_MODEL_CLASS = {
        'voblery': Wobblers,
        'blesny': Spoons,
        'aksessuary-dlya-zimnej-rybalki': WinterFishing,
        'spinningovye-udilisha': SpinningRods,
        'vesy': Libras,
        'dobavki-suhie': DryAdditives,
        'inercionnye-katushki': CoilsInertial,
        'kryuchki': Hooks,
        'leska-monofilnaya': LineMonofilament,
        'multiplikatornye-katushki': CoilsMulty,
        'povodki': Leashes,
        'poplavki': Floats,
        'rogatki': SlingShots
    }

    context_object_name = 'product'
    template_name = 'shop/product_detail.html'
    slug_url_kwarg = 'slug'


    def dispatch(self, request, *args, **kwargs):
        self.model = self.CT_MODEL_MODEL_CLASS[kwargs['ct_model']]
        self.queryset = self.model._base_manager.all()
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ct_model'] = self.model._meta.model_name
        context['cart'] = self.cart
        context['user'] = self.user
        context['category'] = Category.objects.order_by('name')
        return context