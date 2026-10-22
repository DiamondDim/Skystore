from django.db import models
from users.models import CustomUser


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержимое')
    preview = models.ImageField('Превью', upload_to='posts/', blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_published = models.BooleanField('Опубликовано', default=False)
    views_count = models.PositiveIntegerField('Просмотры', default=0)

    # HW-28 (доп. задание): Поле владельца статьи
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name="Автор"
    )

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
