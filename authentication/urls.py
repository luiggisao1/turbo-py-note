from django.urls import path
from .views import register, login_view, logout_view, logout_all

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('logout_all/', logout_all, name='logout_all'),
]
