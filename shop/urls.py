from django.urls import path
from .views import (
    AboutUsView,
    CategoryView,
    CategoryDetailView,
    ProductDetailView,
    MainView,
    CartView,
    AddToCartView,
    DeleteFromCartView,
    ChangeQTYView,
    CheckoutView,
    MakeOrderView,
    HelpView,
    PayShipView,
    PersonalView,
    PromotionsView,
    NewsView,
)


urlpatterns = [
    path('', MainView.as_view(), name='home'),
    path('about', AboutUsView.as_view(), name='about'),
    path('news', NewsView.as_view(), name='news'),
    path('categories', CategoryView.as_view(), name='categories'),
    path('categories/<str:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('categories/<str:ct_model>/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<str:ct_model>/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('remove-from-cart/<str:ct_model>/<str:slug>/', DeleteFromCartView.as_view(), name='remove_from_cart'),
    path('change-qty/<str:ct_model>/<str:slug>/', ChangeQTYView.as_view(), name='change_qty'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('make-order/', MakeOrderView.as_view(), name='make_order'),
    path('help', HelpView.as_view(), name='help'),
    path('pay-ship', PayShipView.as_view(), name='pay_ship'),
    path('personal', PersonalView.as_view(), name='personal'),
    path('promotions', PromotionsView.as_view(), name='promotions'),
]