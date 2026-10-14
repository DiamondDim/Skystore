from django.urls import path
from . import views


urlpatterns = [
    path('catalog/product/<int:product_pk>/', views.catalog_list, name='catalog_product_link'),
    path('catalog/category/<int:category_id>/', views.catalog_list, name='catalog_by_category'),
    path('catalog/', views.catalog_list, name='catalog_list'),
    path('', views.home, name='home'),
    path('contacts/', views.contacts, name='contacts'),
    path('catalog/', views.catalog_list, name='catalog_list'),
    path('add/', views.add_product, name='add_product'),
]
