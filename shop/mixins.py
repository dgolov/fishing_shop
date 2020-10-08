from django.views.generic.detail import SingleObjectMixin
from django.views.generic import View

from .models import (
    Category, ParentCategory,
    Cart, Customer,
    Wobblers, Spoons, WinterFishing, SpinningRods, Libras, DryAdditives, CoilsInertial, Hooks,
    LineMonofilament, CoilsMulty, Leashes, Floats, SlingShots,
)


class CategoryDetailMixin(SingleObjectMixin):

    CATEGORY_SLUG2PRODUCT_MODEL = {
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


    def get_context_data(self, **kwargs):
        if isinstance(self.get_object(), Category):
            model = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
            context = super().get_context_data(**kwargs)
            context['category'] = Category.objects.order_by('name')
            context['product'] = model.objects.all()
            return context

        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.order_by('name')
        return context



class CartMixin(View):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            customer = Customer.objects.filter(user=request.user).first()
            if not customer:
                customer = Customer.objects.create(user=request.user)

            cart = Cart.objects.filter(owner=customer, in_order=False).first()
            if not cart:
                cart = Cart.objects.create(owner=customer)

        else:
            cart = Cart.objects.filter(for_anonymous_user=True).first()
            if not cart:
                cart = Cart.objects.create(for_anonymous_user=True)

        self.cart = cart
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)



class CategoryMixin(View):

    def dispatch(self, request, *args, **kwargs):
        self.category = Category.objects.order_by('name')
        self.parent_category =  ParentCategory.objects.order_by('name')
        return super().dispatch(request, *args, **kwargs)



class ParentCategoryDetailMixin(SingleObjectMixin):

    CATEGORY_SLUG2PRODUCT_MODEL = {
        'aksessuary': [Spoons, Wobblers],
        'katushki': [Spoons, Wobblers],
        'primanki': [Spoons, Wobblers],
        'leski-i-shnury': [Spoons, Wobblers],
        'ostnastka': [Spoons, Wobblers],
        'prikormki-i-nasadki': [Spoons, Wobblers],
        'udilisha': [Spoons, Wobblers],
        'hranenie': [Spoons, Wobblers],
        'ekipirovka': [Spoons, Wobblers],
        'elektronika': [Spoons, Wobblers],
    }


    def get_context_data(self, **kwargs):
        if isinstance(self.get_object(), ParentCategory):
            models = self.CATEGORY_SLUG2PRODUCT_MODEL[self.get_object().slug]
            context = super().get_context_data(**kwargs)
            context['parent_category'] = ParentCategory.objects.order_by('name')
            for model in models:
                context[model.slug] = model.objects.all()
            return context

        context = super().get_context_data(**kwargs)
        context['parent_category'] = ParentCategory.objects.order_by('name')
        return context