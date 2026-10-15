from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Главная
    path('', views.HomeView.as_view(), name='home'),

    # Контакты
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('contacts/success/', TemplateView.as_view(template_name='catalog/success.html'), name='success'),

    # Каталог с фильтрацией
    path('catalog/product/<int:product_pk>/', views.CatalogListView.as_view(), name='catalog_product_link'),
    path('catalog/category/<int:category_id>/', views.CatalogListView.as_view(), name='catalog_by_category'),
    path('catalog/', views.CatalogListView.as_view(), name='catalog_list'),

    # Детальная страница товара
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),

    # Добавление товара
    path('add/', views.AddProductView.as_view(), name='add_product'),
]
