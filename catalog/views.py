import re
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, FormView, UpdateView, DeleteView
from .models import Product
from .forms import ProductAddForm, ContactForm


# 1. Главная страница
class HomeView(TemplateView):
    template_name = 'catalog/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context


# 2. Каталог товаров
class CatalogListView(ListView):
    model = Product
    template_name = 'catalog/catalog_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        product_pk = self.kwargs.get('product_pk')
        if product_pk:
            try:
                return [Product.objects.get(pk=product_pk)]
            except Product.DoesNotExist:
                return Product.objects.none()
        category_id = self.kwargs.get('category_id')
        queryset = Product.objects.all()
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


# 3. Детальная страница товара
class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


# 4. Форма контактов
class ContactsView(FormView):
    template_name = 'catalog/contacts.html'
    form_class = ContactForm
    success_url = '/contacts/success/'

    def form_valid(self, form):
        name = form.cleaned_data.get('name', '').strip()
        phone = form.cleaned_data.get('phone', '').strip()
        message = form.cleaned_data.get('message', '').strip()
        if not name or not message:
            return HttpResponse("Пожалуйста, заполните имя и сообщение.", status=400)
        phone_pattern = r'^\+\d{1,3}[\s\-()]{0,3}\d{3,14}$'
        if not phone or not re.match(phone_pattern, phone):
            return HttpResponse(
                "Неверный формат телефона. Используйте международный формат.",
                status=400
            )
        print(f"📩 Новое сообщение от {name} ({phone}): {message}")
        return super().form_valid(form)


# 5. Добавление товара
class AddProductView(CreateView):
    model = Product
    form_class = ProductAddForm
    template_name = 'catalog/product_form.html'  # Изменено на product_form.html
    success_url = reverse_lazy('catalog_list')  # ИСПРАВЛЕНО: было '/catalog/'


# 6. Редактирование товара
class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductAddForm
    template_name = 'catalog/product_form.html'  # Изменено на product_form.html
    success_url = reverse_lazy('catalog_list')  # ИСПРАВЛЕНО: было '/catalog/'


# 7. Удаление товара
class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog_list')  # ИСПРАВЛЕНО: было '/catalog/'
