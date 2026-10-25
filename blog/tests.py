from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import Post
from users.models import CustomUser


class BlogTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Создаем автора статей
        self.author = CustomUser.objects.create_user(
            email="author@test.com",
            username="author",
            password="testpass123"
        )
        # Создаем обычного читателя
        self.reader = CustomUser.objects.create_user(
            email="reader@test.com",
            username="reader",
            password="testpass123"
        )

        # Опубликованная статья (владелец author)
        self.post = Post.objects.create(
            title='Опубликованная статья',
            content='Это тестовый контент.',
            owner=self.author,
            is_published=True,
            views_count=0
        )
        # Неопубликованная статья (владелец author, но скрыта от reader)
        self.unpublished_post = Post.objects.create(
            title='Скрытая статья',
            content='Этот контент не должен быть виден.',
            owner=self.author,
            is_published=False
        )

    def test_post_list_shows_only_published(self):
        """Проверка: обычный пользователь видит только опубликованные статьи."""
        self.client.login(email="reader@test.com", password="testpass123")
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Опубликованная статья')
        self.assertNotContains(response, 'Скрытая статья')

    def test_owner_sees_own_unpublished_post(self):
        """Проверка: владелец ВИДИТ свои неопубликованные статьи."""
        self.client.login(email="author@test.com", password="testpass123")
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Опубликованная статья')
        self.assertContains(response, 'Скрытая статья')

    def test_post_detail_increments_views(self):
        self.client.login(email="reader@test.com", password="testpass123")
        url = reverse('post_detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 1)

    def test_post_detail_returns_404_for_non_existent(self):
        self.client.login(email="reader@test.com", password="testpass123")
        url = reverse('post_detail', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_post_create_valid_data(self):
        self.client.login(email="author@test.com", password="testpass123")
        url = reverse('post_create')
        data = {
            'title': 'Новая тестовая статья',
            'content': 'Контент новой статьи',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='Новая тестовая статья').exists())

        new_post = Post.objects.get(title='Новая тестовая статья')
        self.assertEqual(new_post.owner, self.author)
        self.assertFalse(new_post.is_published)

    def test_post_create_invalid_data(self):
        self.client.login(email="author@test.com", password="testpass123")
        url = reverse('post_create')
        data = {
            'title': '',
            'content': 'Контент',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(title='').exists())

    def test_post_update_and_redirect(self):
        self.client.login(email="author@test.com", password="testpass123")
        url = reverse('post_update', kwargs={'pk': self.post.pk})
        data = {
            'title': 'Обновленный заголовок',
            'content': 'Обновленный контент',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('post_detail', kwargs={'pk': self.post.pk}))
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Обновленный заголовок')

    def test_post_delete(self):
        self.client.login(email="author@test.com", password="testpass123")
        url = reverse('post_delete', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('post_list'))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_email_sent_on_100_views(self):
        self.client.login(email="reader@test.com", password="testpass123")
        self.post.views_count = 99
        self.post.save()
        url = reverse('post_detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('100 просмотров', mail.outbox[0].subject)
        self.assertIn('mecheny91@yandex.ru', mail.outbox[0].to)


class BlogPermissionsTests(TestCase):
    """Тесты прав доступа для блога (HW-28)"""

    def setUp(self):
        self.client = Client()

        self.author = CustomUser.objects.create_user(email="author@test.com", username="author", password="testpass123")
        self.regular_user = CustomUser.objects.create_user(email="regular@test.com", username="regular",
                                                           password="testpass123")
        self.content_manager = CustomUser.objects.create_user(email="cm@test.com", username="cm",
                                                              password="testpass123")

        self.post = Post.objects.create(title="Тестовая статья", content="Текст", owner=self.author, is_published=True)

        # ✅ ИСПРАВЛЕНО: используем Group, а не CustomUser!
        self.cm_group = Group.objects.create(name="Контент-менеджер")
        content_type = ContentType.objects.get_for_model(Post)
        perm_change = Permission.objects.get(codename='change_post', content_type=content_type)
        perm_delete = Permission.objects.get(codename='delete_post', content_type=content_type)
        self.cm_group.permissions.add(perm_change, perm_delete)
        self.content_manager.groups.add(self.cm_group)

    def test_author_can_update_own_post(self):
        self.client.login(email="author@test.com", password="testpass123")
        response = self.client.get(reverse('post_update', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_update_others_post(self):
        self.client.login(email="regular@test.com", password="testpass123")
        response = self.client.get(reverse('post_update', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 403)

    def test_content_manager_can_update_any_post(self):
        self.client.login(email="cm@test.com", password="testpass123")
        response = self.client.get(reverse('post_update', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_author_can_delete_own_post(self):
        self.client.login(email="author@test.com", password="testpass123")
        response = self.client.get(reverse('post_delete', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_delete_others_post(self):
        self.client.login(email="regular@test.com", password="testpass123")
        response = self.client.get(reverse('post_delete', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 403)

    def test_content_manager_can_delete_any_post(self):
        self.client.login(email="cm@test.com", password="testpass123")
        response = self.client.get(reverse('post_delete', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)

    def test_publish_post_view(self):
        draft_post = Post.objects.create(title="Черновик", content="Текст", owner=self.author, is_published=False)
        self.client.login(email="cm@test.com", password="testpass123")
        response = self.client.post(reverse('publish_post', kwargs={'pk': draft_post.pk}))
        self.assertEqual(response.status_code, 302)
        draft_post.refresh_from_db()
        self.assertTrue(draft_post.is_published)

    def test_regular_user_cannot_publish_post(self):
        draft_post = Post.objects.create(title="Черновик 2", content="Текст", owner=self.regular_user,
                                         is_published=False)
        self.client.login(email="regular@test.com", password="testpass123")
        response = self.client.post(reverse('publish_post', kwargs={'pk': draft_post.pk}))
        self.assertEqual(response.status_code, 403)

    def test_post_creation_sets_owner_and_unpublished(self):
        self.client.login(email="author@test.com", password="testpass123")
        response = self.client.post(reverse('post_create'), {'title': 'Новая статья', 'content': 'Контент'})
        self.assertEqual(response.status_code, 302)
        new_post = Post.objects.get(title='Новая статья')
        self.assertEqual(new_post.owner, self.author)
        self.assertFalse(new_post.is_published)
