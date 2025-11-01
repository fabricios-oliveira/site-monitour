from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('', views.package_list, name='package_list'),
    path('destinos/', views.destination_list, name='destination_list'),
    path('categorias/', views.category_list, name='category_list'),
    path('<slug:slug>/', views.package_detail, name='package_detail'),
]