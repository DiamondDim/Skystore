from django.urls import path
from .views import RegisterView, CustomLoginView, CustomLogoutView, GoodbyeView, ProfileUpdateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('logged_out/', GoodbyeView.as_view(), name='logged_out'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
]
