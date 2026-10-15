from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from .models import Post


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(is_published=True)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])

        if obj.views_count == 100:
            subject = f"🎉 Поздравляем! Статья '{obj.title}' набрала 100 просмотров!"
            message = f"Отличные новости!\n\nВаша статья '{obj.title}' только что достигла отметки в 100 просмотров.\nПродолжайте создавать качественный контент!"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = ['mecheny91@yandex.ru']

            try:
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                print("✅ Письмо о 100 просмотрах успешно отправлено!")
            except Exception as e:
                print(f"❌ Ошибка отправки письма: {e}")

        return obj


class PostCreateView(CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'preview', 'is_published']
    success_url = reverse_lazy('post_list')


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'preview', 'is_published']

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')
