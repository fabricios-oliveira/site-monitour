from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('categorias/', views.category_list, name='category_list'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]