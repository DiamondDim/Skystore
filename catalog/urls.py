from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('catalog/product/<int:product_pk>/', views.catalog_list, name='catalog_product_link'),
    path('catalog/category/<int:category_id>/', views.catalog_list, name='catalog_by_category'),
    path('catalog/', views.catalog_list, name='catalog_list'),
    path('', views.home, name='home'),
    path('contacts/', views.contacts, name='contacts'),
    path('add/', views.add_product, name='add_product'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)