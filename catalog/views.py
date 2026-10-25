from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, FormView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .models import Product, Category
from .forms import ProductAddForm, ContactForm
from .services import (
    get_products_by_category,
    get_all_products,
    get_product_by_id,
    invalidate_product_cache
)


class HomeView(TemplateView):
    template_name = 'catalog/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_published=True)[:6]
        return context


class CatalogListView(ListView):
    model = Product
    template_name = 'catalog/catalog_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        # 1. Анонимы видят только опубликованные (берем мгновенно из кэша!)
        if not self.request.user.is_authenticated:
            return get_all_products()

        # 2. Проверяем, является ли пользователь модератором
        is_moderator = self.request.user.has_perm('catalog.can_unpublish_product') or self.request.user.is_staff
        if is_moderator:
            # Модераторам даем свежий QuerySet со всеми продуктами
            return Product.objects.all()

        # 3. Обычные авторизованные пользователи видят:
        # Опубликованные + свои неопубликованные
        return Product.objects.filter(
            Q(is_published=True) | Q(owner=self.request.user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        category_id = self.kwargs.get('category_id')
        if category_id:
            context['current_category'] = get_object_or_404(Category, pk=category_id)
        return context


class ProductDetailView(DetailView):
    """Детальная страница продукта с низкоуровневым кешированием."""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        """Используем сервисный слой с кешированием вместо прямого запроса к БД."""
        product_id = self.kwargs.get('pk')
        product = get_product_by_id(product_id)
        if product is None:
            raise Http404("Продукт не найден")
        return product


class ContactsView(FormView):
    template_name = 'catalog/contacts.html'
    form_class = ContactForm
    success_url = '/contacts/success/'

    def form_valid(self, form):
        return super().form_valid(form)


class AddProductView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductAddForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.is_published = False
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductAddForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog_list')

    def test_func(self):
        product = self.get_object()
        is_owner = (self.request.user == product.owner)
        is_moderator = self.request.user.has_perm('catalog.change_product')
        return is_owner or is_moderator

    def form_valid(self, form):
        """После успешного сохранения — очищаем кеш."""
        response = super().form_valid(form)
        # Очищаем кеш для этого продукта и связанных списков
        invalidate_product_cache(self.object.id, self.object.category_id)
        return response

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет прав для редактирования этого продукта.")


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog_list')

    def test_func(self):
        product = self.get_object()
        is_owner = (self.request.user == product.owner)
        is_moderator = self.request.user.has_perm('catalog.delete_product')
        return is_owner or is_moderator

    def delete(self, request, *args, **kwargs):
        """Перед удалением — сохраняем ID и category_id для очистки кеша."""
        product = self.get_object()
        product_id = product.id
        category_id = product.category_id
        response = super().delete(request, *args, **kwargs)
        invalidate_product_cache(product_id, category_id)
        return response

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет прав для удаления этого продукта.")


class PublishProductView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Представление для публикации продукта (только модераторы и админы)"""

    def test_func(self):
        return self.request.user.has_perm('catalog.can_unpublish_product') or self.request.user.is_staff

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.is_published = True
        product.save()
        # Очищаем кеш после публикации
        invalidate_product_cache(product.id, product.category_id)
        return redirect('product_detail', pk=product.pk)


class CategoryProductsView(TemplateView):
    template_name = 'catalog/category_products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        # Получаем саму категорию для отображения заголовка
        context['category'] = get_object_or_404(Category, pk=category_id)
        # Используем наш сервис (он сам разберется с кешем!)
        context['products'] = get_products_by_category(category_id)
        return context
