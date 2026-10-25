from django.urls import path
from django.views.generic import TemplateView
from . import views
from .views import ProductUpdateView, ProductDeleteView, CategoryProductsView

urlpatterns = [
    # Главная
    path('', views.HomeView.as_view(), name='home'),

    # Контакты
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('contacts/success/', TemplateView.as_view(template_name='catalog/success.html'), name='success'),

    # Каталог с фильтрацией
    path('catalog/product/<int:product_pk>/', views.CatalogListView.as_view(), name='catalog_product_link'),

    # ВАЖНО: Используем CategoryProductsView (с кешированием), но сохраняем имя 'catalog_by_category' для base.html!
    path('catalog/category/<int:category_id>/', CategoryProductsView.as_view(), name='catalog_by_category'),

    path('catalog/', views.CatalogListView.as_view(), name='catalog_list'),

    # Детальная страница товара
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Добавление товара
    path('add/', views.AddProductView.as_view(), name='add_product'),

    # Редактирование и удаление товара
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('product/<int:pk>/publish/', views.PublishProductView.as_view(), name='publish_product'),
]
