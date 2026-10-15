from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from .models import Post


class BlogTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем опубликованную статью
        self.post = Post.objects.create(
            title='Опубликованная статья',
            content='Это тестовый контент.',
            is_published=True,
            views_count=0
        )
        # Создаем неопубликованную статью
        self.unpublished_post = Post.objects.create(
            title='Скрытая статья',
            content='Этот контент не должен быть виден.',
            is_published=False
        )

    def test_post_list_shows_only_published(self):
        """Проверка: в списке видны только опубликованные статьи."""
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Опубликованная статья')
        self.assertNotContains(response, 'Скрытая статья')

    def test_post_detail_increments_views(self):
        """Проверка: при открытии статьи счетчик просмотров увеличивается."""
        url = reverse('post_detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 1)

    def test_post_detail_returns_404_for_non_existent(self):
        """Проверка: запрос несуществующей статьи возвращает 404."""
        url = reverse('post_detail', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_create_valid_data(self):
        """Проверка: успешное создание новой статьи."""
        url = reverse('post_create')
        data = {
            'title': 'Новая тестовая статья',
            'content': 'Контент новой статьи',
            'is_published': True
        }
        response = self.client.post(url, data)
        # После успеха должен быть редирект (302)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='Новая тестовая статья').exists())

    def test_post_create_invalid_data(self):
        """Проверка: создание статьи с пустым заголовком не проходит."""
        url = reverse('post_create')
        data = {
            'title': '',  # Обязательное поле пустое
            'content': 'Контент',
            'is_published': True
        }
        response = self.client.post(url, data)
        # Форма должна перерендериться с ошибками (200), а не сделать редирект
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title='').exists())

    def test_post_update_and_redirect(self):
        """Проверка: успешное редактирование статьи и редирект на её страницу."""
        url = reverse('post_update', kwargs={'pk': self.post.pk})
        data = {
            'title': 'Обновленный заголовок',
            'content': 'Обновленный контент',
            'is_published': True
        }
        response = self.client.post(url, data)
        # Проверяем редирект на страницу детального просмотра этой же статьи
        self.assertRedirects(response, reverse('post_detail', kwargs={'pk': self.post.pk}))

        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Обновленный заголовок')

    def test_post_delete(self):
        """Проверка: успешное удаление статьи."""
        url = reverse('post_delete', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        # Проверяем редирект на список статей
        self.assertRedirects(response, reverse('post_list'))
        # Проверяем, что статья действительно удалена из БД
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_email_sent_on_100_views(self):
        """Проверка (доп. задание): отправка письма при достижении 100 просмотров."""
        # Устанавливаем счетчик на 99
        self.post.views_count = 99
        self.post.save()

        url = reverse('post_detail', kwargs={'pk': self.post.pk})

        # Делаем запрос, который должен увеличить счетчик до 100 и триггернуть письмо
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Проверяем, что было отправлено ровно 1 письмо
        self.assertEqual(len(mail.outbox), 1)
        # Проверяем тему письма
        self.assertIn('100 просмотров', mail.outbox[0].subject)
        # Проверяем получателя (тот, что указан в views.py)
        self.assertIn('mecheny91@yandex.ru', mail.outbox[0].to)
