from django.urls import path
from . import views

app_name = 'cadastros'

urlpatterns = [
    path('relatorio-clientes-chave/', views.relatorio_clientes_chave, name='relatorio_clientes_chave'),
    path('verificar-cpf/', views.verificar_cpf, name='verificar_cpf'), # Nova URL
]
