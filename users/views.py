from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import CustomUser


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        # Автоматический вход после регистрации
        login(self.request, user)
        # Отправка приветственного письма
        self.send_welcome_email(user)
        return super().form_valid(form)

    def send_welcome_email(self, user):
        subject = 'Добро пожаловать в Skystore!'
        message = f'Привет, {user.username}!\n\nСпасибо за регистрацию в Skystore!\nТеперь вы можете добавлять товары и статьи.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            print(f"✅ Приветственное письмо успешно сформировано для: {user.email}")
        except Exception as e:
            print(f"❌ Ошибка отправки письма: {e}")


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    redirect_field_name = 'next'


class CustomLogoutView(LogoutView):

    pass


class GoodbyeView(TemplateView):
    # Это представление просто отрисовывает красивую страницу прощания
    template_name = 'users/logged_out.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования профиля пользователя"""
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        # Возвращаем текущего пользователя
        return self.request.user
