from django.db import models

class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержимое')
    preview = models.ImageField('Превью', upload_to='posts/', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_published = models.BooleanField('Опубликовано', default=False)
    views_count = models.PositiveIntegerField('Просмотры', default=0)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
