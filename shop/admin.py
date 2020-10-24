from django.contrib import admin
from .models import Category, ParentCategory, Customer, Cart, CartProduct, Wobblers, Spoons, Order



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}



@admin.register(ParentCategory)
class ParentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}



@admin.register(Wobblers)
class WobblersAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'available']
    list_filter = ['type_of_fishing', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}



@admin.register(Spoons)
class SpoonsAdmin(admin.ModelAdmin):
    list_display = ['name',  'price', 'stock', 'available']
    list_filter = ['type_of_fishing', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}



admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Order)