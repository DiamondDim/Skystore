import re
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Product


def home(request):
    """Главная страница: выводим список товаров."""
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'catalog/home.html', context)


def catalog_list(request, category_id=None):
    """Страница каталога с возможностью фильтрации по категории."""
    products = Product.objects.all()

    # Если передан ID категории, фильтруем товары
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
