from django.urls import path
from .views import RegisterView, ProfileView, PromoteUserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('promote-user/', PromoteUserView.as_view(), name='promote-user'),
]