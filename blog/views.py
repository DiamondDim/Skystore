from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Post
from .forms import PostForm


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = Post.objects.all()

        if not self.request.user.is_authenticated:
            # Анонимы видят только опубликованные
            return queryset.filter(is_published=True)

        # Проверяем, является ли пользователь контент-менеджером
        is_content_manager = self.request.user.has_perm('blog.change_post') or self.request.user.is_staff

        if is_content_manager:
            # Контент-менеджеры и админы видят ВСЕ статьи (включая неопубликованные)
            return queryset

        # Обычные авторизованные пользователи видят:
        # 1. Все опубликованные статьи
        # 2. Свои неопубликованные статьи
        return queryset.filter(
            Q(is_published=True) | Q(owner=self.request.user)
        ).distinct()


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        if obj.views_count == 100:
            subject = f"Поздравляем! Статья '{obj.title}' набрала 100 просмотров!"
            message = f"Отличные новости!\n\nВаша статья '{obj.title}' только что достигла отметки в 100 просмотров."
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = ['mecheny91@yandex.ru']
            try:
                send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            except Exception:
                pass
        return obj


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.is_published = False
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'

    def test_func(self):
        post = self.get_object()
        is_owner = (self.request.user == post.owner)
        is_content_manager = self.request.user.has_perm('blog.change_post')
        return is_owner or is_content_manager

    def get_success_url(self):
        return reverse_lazy('post_detail', kwargs={'pk': self.object.pk})

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет прав для редактирования этой статьи.")


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post_list')

    def test_func(self):
        post = self.get_object()
        is_owner = (self.request.user == post.owner)
        is_content_manager = self.request.user.has_perm('blog.delete_post')
        return is_owner or is_content_manager

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет прав для удаления этой статьи.")


class PublishPostView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Представление для публикации статьи (контент-менеджеры и админы)"""

    def test_func(self):
        return self.request.user.has_perm('blog.change_post') or self.request.user.is_staff

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        post.is_published = True
        post.save()
        return redirect('post_detail', pk=post.pk)
