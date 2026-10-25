from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product, Category
from users.models import CustomUser


class ProductPermissionsTests(TestCase):
    """Тесты прав доступа для продуктов (HW-28)"""

    def setUp(self):
        self.client = Client()

        # Создаем категорию
        self.category = Category.objects.create(name="Тестовая категория")

        # Создаем пользователей (ВАЖНО: email используется для логина!)
        self.owner = CustomUser.objects.create_user(
            email="owner@test.com",
            username="owner",
            password="testpass123"
        )
        self.regular_user = CustomUser.objects.create_user(
            email="regular@test.com",
            username="regular",
            password="testpass123"
        )
        self.moderator = CustomUser.objects.create_user(
            email="mod@test.com",
            username="moderator",
            password="testpass123"
        )

        # Создаем продукты
        self.product_owner = Product.objects.create(
            name="Мой продукт",
            category=self.category,
            price=100,
            owner=self.owner,
            is_published=True
        )
        self.product_other = Product.objects.create(
            name="Чужой продукт",
            category=self.category,
            price=200,
            owner=self.owner,
            is_published=True
        )

        # Настраиваем группу модератора и выдаем права
        self.mod_group = Group.objects.create(name="Модератор продуктов")
        content_type = ContentType.objects.get_for_model(Product)
        perm_delete = Permission.objects.get(codename='delete_product', content_type=content_type)
        perm_unpublish = Permission.objects.get(codename='can_unpublish_product', content_type=content_type)
        self.mod_group.permissions.add(perm_delete, perm_unpublish)
        self.moderator.groups.add(self.mod_group)

    def test_product_creation_sets_owner_and_unpublished(self):
        """Тест: при создании продукта владелец назначается автоматически, статус - не опубликован"""
        # ИСПРАВЛЕНО: используем email для логина
        self.client.login(email="owner@test.com", password="testpass123")
        url = reverse('add_product')
        data = {
            'name': 'Новый тестовый продукт',
            'category': self.category.id,
            'price': 50,
            'description': 'Тестовое описание'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Редирект после успеха

        new_product = Product.objects.get(name='Новый тестовый продукт')
        self.assertEqual(new_product.owner, self.owner)
        self.assertFalse(new_product.is_published)

    def test_owner_can_update_own_product(self):
        """Тест: владелец может редактировать свой продукт"""
        self.client.login(email="owner@test.com", password="testpass123")
        url = reverse('product_update', kwargs={'pk': self.product_owner.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_update_others_product(self):
        """Тест: обычный юзер НЕ может редактировать чужой продукт (403)"""
        self.client.login(email="regular@test.com", password="testpass123")
        url = reverse('product_update', kwargs={'pk': self.product_owner.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_moderator_can_update_others_product(self):
        """Тест: модератор МОЖЕТ редактировать чужой продукт"""
        self.client.login(email="mod@test.com", password="testpass123")
        url = reverse('product_update', kwargs={'pk': self.product_owner.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_publish_product_view(self):
        """Тест: модератор может опубликовать продукт через кнопку"""
        draft_product = Product.objects.create(
            name="Черновик",
            category=self.category,
            price=10,
            owner=self.owner,
            is_published=False
        )

        self.client.login(email="mod@test.com", password="testpass123")
        url = reverse('publish_product', kwargs={'pk': draft_product.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        draft_product.refresh_from_db()
        self.assertTrue(draft_product.is_published)

    def test_regular_user_cannot_publish_product(self):
        """Тест: обычный юзер НЕ может опубликовать продукт (403)"""
        draft_product = Product.objects.create(
            name="Черновик 2",
            category=self.category,
            price=10,
            owner=self.regular_user,
            is_published=False
        )

        self.client.login(email="regular@test.com", password="testpass123")
        url = reverse('publish_product', kwargs={'pk': draft_product.pk})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)

    def test_catalog_shows_only_published_for_anonymous(self):
        """Тест: анонимный пользователь видит только опубликованные продукты"""
        Product.objects.create(
            name="Скрытый продукт",
            category=self.category,
            price=5,
            owner=self.owner,
            is_published=False
        )

        url = reverse('catalog_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Мой продукт")
        self.assertNotContains(response, "Скрытый продукт")

    def test_owner_sees_own_unpublished_product(self):
        """Тест: владелец видит свои неопубликованные продукты в каталоге"""
        draft_product = Product.objects.create(
            name="Мой черновик",
            category=self.category,
            price=15,
            owner=self.owner,
            is_published=False
        )

        self.client.login(email="owner@test.com", password="testpass123")
        url = reverse('catalog_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Мой черновик")
