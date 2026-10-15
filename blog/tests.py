from django.test import TestCase, Client
from django.urls import reverse
from .models import Post

class BlogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.post = Post.objects.create(
            title='Test Post',
            content='Test Content',
            is_published=True
        )
        self.unpublished = Post.objects.create(
            title='Unpublished',
            content='Hidden',
            is_published=False
        )

    def test_post_list_shows_published(self):
        response = self.client.get(reverse('post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertNotContains(response, 'Unpublished')

    def test_post_detail_increments_views(self):
        response = self.client.get(reverse('post_detail', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, 1)

    def test_post_create(self):
        data = {
            'title': 'New Post',
            'content': 'New Content',
            'is_published': True
        }
        response = self.client.post(reverse('post_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New Post').exists())
