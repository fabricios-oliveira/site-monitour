from django.urls import path, re_path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('documentacao/', views.documentation_view, name='docs'),
    # Serve arquivos da documentação HTML - aceita qualquer caminho seguro
    re_path(r'^documentacao/(?P<filename>.+?)$', 
            views.documentation_view, name='docs_file'),
]