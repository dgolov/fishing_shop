from django.contrib import admin
from .models import Category, ParentCategory, Customer, Cart, CartProduct, Wobblers, Spoons, Order


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}



class ParentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}



class WobblersAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['type_of_fishing', 'available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}



class SpoonsAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug',  'price', 'stock', 'available', 'created', 'updated']
    list_filter = ['type_of_fishing', 'available', 'created', 'updated']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}



admin.site.register(Category, CategoryAdmin)
admin.site.register(ParentCategory, ParentCategoryAdmin)
admin.site.register(Spoons, SpoonsAdmin)
admin.site.register(Wobblers, WobblersAdmin)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Order)