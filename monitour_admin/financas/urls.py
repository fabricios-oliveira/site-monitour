from django.urls import path
from . import views

app_name = 'financas'

urlpatterns = [
    path('', views.dashboard_financeiro_view, name='dashboard_financeiro'),
    path('upload-extrato/', views.upload_extrato_view, name='upload_extrato'),
    path('transacoes/', views.lista_transacoes_view, name='lista_transacoes'),
]