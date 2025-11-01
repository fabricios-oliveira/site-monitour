"""
URLs do Dashboard - Sistema Interno MONITOUR
Versão simplificada usando function-based views
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Login/Logout
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Dashboard Principal
    path('', views.DashboardView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    
    # Páginas Simplificadas - Em desenvolvimento
    path('packages/', views.packages_view, name='packages'),
    path('sales/', views.sales_view, name='sales'), 
    path('inquiries/', views.inquiries_view, name='inquiries'),
    path('categories/', views.categories_view, name='categories'),
    path('destinations/', views.destinations_view, name='destinations'),
    path('reports/', views.reports_view, name='reports'),
    path('users/', views.users_view, name='users'),
    path('settings/', views.settings_view, name='settings'),
]