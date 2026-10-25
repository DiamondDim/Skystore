from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, FormView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .models import Product, Category
from .forms import ProductAddForm, ContactForm


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
        # Базовый queryset: ВСЕ продукты
        queryset = Product.objects.all()

        # Фильтрация по категории (если передан параметр category_id)
        category_id = self.kwargs.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Фильтрация по статусу публикации и правам пользователя
        if not self.request.user.is_authenticated:
            # Анонимы видят только опубликованные
            return queryset.filter(is_published=True)

        # Проверяем, является ли пользователь модератором
        is_moderator = self.request.user.has_perm('catalog.can_unpublish_product') or self.request.user.is_staff

        if is_moderator:
            # Модераторы и админы видят ВСЕ продукты (включая неопубликованные)
            return queryset

        # Обычные авторизованные пользователи видят:
        # 1. Все опубликованные продукты
        # 2. Свои неопубликованные продукты
        return queryset.filter(
            Q(is_published=True) | Q(owner=self.request.user)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем все категории для отображения в шаблоне
        context['categories'] = Category.objects.all()
        # Добавляем текущую выбранную категорию (если есть)
        category_id = self.kwargs.get('category_id')
        if category_id:
            context['current_category'] = get_object_or_404(Category, pk=category_id)
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


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
        is_moderator = self.request.user.has_perm('catalog.delete_product')
        return is_owner or is_moderator

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
        return redirect('product_detail', pk=product.pk)
