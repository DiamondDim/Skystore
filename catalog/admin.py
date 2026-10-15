from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Выводим id и name в списке
    list_display = ('id', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Выводим id, name, price и category
    list_display = ('id', 'name', 'price', 'category')
    # Настраиваем фильтрацию по категории
    list_filter = ('category',)
    # Настраиваем поиск по имени и описанию
    search_fields = ('name', 'description')
