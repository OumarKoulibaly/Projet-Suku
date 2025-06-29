from django.urls import path, include
from django.contrib import admin
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("dj_rest_auth.urls")),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
]