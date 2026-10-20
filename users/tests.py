from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser


class CustomUserModelTest(TestCase):
    """Тесты для кастомной модели пользователя"""

    def test_create_user_with_email(self):
        """Проверка создания пользователя с email как основным полем"""
        user = CustomUser.objects.create_user(
            email='testmodel@test.com',
            username='testmodeluser',
            password='TestPass123!'
        )
        self.assertEqual(user.email, 'testmodel@test.com')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertEqual(str(user), 'testmodel@test.com')


class UserViewsTest(TestCase):
    """Тесты для представлений аутентификации"""

    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            email='testview@test.com',
            username='testviewuser',
            password='TestPass123!'
        )

    def test_register_view_get(self):
        """GET-запрос к странице регистрации возвращает 200"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_view_post_success(self):
        """Успешная регистрация создает пользователя и редиректит"""
        response = self.client.post(reverse('register'), {
            'email': 'newuser@test.com',
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!'
        })
        self.assertEqual(response.status_code, 302)  # Редирект на home
        self.assertTrue(CustomUser.objects.filter(email='newuser@test.com').exists())

    def test_login_view_get(self):
        """GET-запрос к странице входа возвращает 200"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_view_post_success(self):
        """Успешный вход редиректит на главную"""
        response = self.client.post(reverse('login'), {
            'username': 'testview@test.com',  # Так как USERNAME_FIELD = 'email'
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_view_post_fail(self):
        """Неверный пароль возвращает форму с ошибками (200)"""
        response = self.client.post(reverse('login'), {
            'username': 'testview@test.com',
            'password': 'WrongPassword!'
        })
        self.assertEqual(response.status_code, 200)

        # Более надежный способ проверки non_field_errors в новых версиях Django
        form = response.context['form']
        self.assertTrue(form.non_field_errors())  # Проверяем, что общие ошибки есть
        self.assertContains(response, 'correct email and password')  # Проверяем текст ошибки

    def test_logout_view(self):
        """POST-запрос на выход разлогинивает и редиректит на страницу прощания"""
        self.client.login(username='testview@test.com', password='TestPass123!')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Редирект на logged_out

    def test_profile_edit_unauthenticated(self):
        """Неавторизованный пользователь не может редактировать профиль"""
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 302)  # Редирект на login
        self.assertIn('/users/login/', response.url)

    def test_profile_edit_authenticated(self):
        """Авторизованный пользователь имеет доступ к редактированию профиля"""
        self.client.login(username='testview@test.com', password='TestPass123!')
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_edit.html')
