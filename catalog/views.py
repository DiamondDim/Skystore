import re
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from .forms import ProductAddForm


def home(request):
    """Главная страница: выводим список товаров."""
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'catalog/home.html', context)


def catalog_list(request, category_id=None, product_pk=None):
    """
    Страница каталога.
    - Если передан product_pk -> показывает детальный вид одного товара (как заглушку для категории).
    - Если передан category_id -> фильтрует по категории.
    - Иначе -> показывает все товары или сообщение 'Обратитесь к администратору'.
    """

    # 1. Если кликнули по ссылке, ведущей на конкретный товар (Рассылки/Утилиты)
    if product_pk:
        try:
            product = Product.objects.get(pk=product_pk)
            # Рендерим шаблон детальной страницы, но через общий view каталога
            return render(request, 'catalog/product_detail.html', {'product': product})
        except Product.DoesNotExist:
            pass

            # 2. Стандартная логика каталога
    products = Product.objects.all()

    if category_id:
        products = products.filter(category_id=category_id)

    context = {'products': products}
    return render(request, 'catalog/catalog_list.html', context)


def product_detail(request, pk):
    """Страница конкретного товара (Задание 1)."""
    """ Защита от несуществующего ID: вернет 404 вместо падения"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'catalog/product_detail.html', {'product': product})


def contacts(request):
    """Контроллер для страницы контактов с обработкой POST-запроса."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        # Валидация: имя и сообщение обязательны
        if not name or not message:
            return HttpResponse("Пожалуйста, заполните имя и сообщение.", status=400)

        # Валидация международного номера телефона
        # Принимает форматы: +1 234-567-8900, +44 20 7946 0958, +7 999 123-45-67 и т.д.
        phone_pattern = r'^\+\d{1,3}[\s\-()]{0,3}\d{3,14}$'

        if not phone or not re.match(phone_pattern, phone):
            return HttpResponse(
                "Неверный формат телефона. Пожалуйста, используйте международный формат "
                "(например: +1 234-567-8900 или +44 20 7946 0958).",
                status=400
            )

        # Логируем в консоль для отладки
        print(f"📩 Новое сообщение от {name} ({phone}): {message}")

        # Рендерим страницу успеха
        return render(request, 'catalog/success.html', {'name': name})

    return render(request, 'catalog/contacts.html')


def add_product(request):
    """Форма добавления нового товара с сохранением в БД."""
    if request.method == 'POST':
        form = ProductAddForm(request.POST, request.FILES)  # request.FILES нужен для загрузки картинок
        if form.is_valid():
            form.save()  # Сохраняем в БД
            return redirect('catalog_list')  # Перенаправляем в каталог после успеха
    else:
        form = ProductAddForm()

    return render(request, 'catalog/add_product.html', {'form': form})
