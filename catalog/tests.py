from django.test import TestCase, Client
from catalog.models import Product, Category
from django.urls import reverse

class CatalogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Test Cat')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test Desc',
            price=100.00,
            category=self.category
        )

    def test_catalog_page_status(self):
        """Проверка, что страница каталога открывается."""
        response = self.client.get(reverse('catalog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')

    def test_product_detail_not_found(self):
        """Проверка 404 для несуществующего товара."""
        response = self.client.get(reverse('product_detail', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_add_product_form_valid(self):
        """Проверка успешного добавления товара."""
        data = {
            'name': 'New Product',
            'description': 'New Desc',
            'price': 50.00,
            'category': self.category.pk
        }
        response = self.client.post(reverse('add_product'), data)
        # После успешного сохранения должен быть редирект (302)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name='New Product').exists())
