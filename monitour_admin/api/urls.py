"""
URLs da API do Sistema Interno MONITOUR
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Health Check
    path('health/', views.api_health_check, name='health_check'),
    
    # Endpoints Públicos (para Site Público)
    path('packages/', views.TourPackageListAPIView.as_view(), name='package_list'),
    path('packages/<slug:slug>/', views.TourPackageDetailAPIView.as_view(), name='package_detail'),
    path('categories/', views.CategoryListAPIView.as_view(), name='category_list'),
    path('destinations/', views.DestinationListAPIView.as_view(), name='destination_list'),
    
    # Endpoints para Registro de Vendas e Consultas
    path('sales/create/', views.SaleCreateAPIView.as_view(), name='sale_create'),
    path('inquiries/create/', views.CustomerInquiryCreateAPIView.as_view(), name='inquiry_create'),
    
    # Endpoints Privados (Sistema Interno)
    path('admin/sales/', views.SaleListAPIView.as_view(), name='admin_sale_list'),
    path('admin/inquiries/', views.CustomerInquiryListAPIView.as_view(), name='admin_inquiry_list'),
    
    # Dashboard e Estatísticas
    path('admin/dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('admin/dashboard/recent-sales/', views.recent_sales, name='recent_sales'),
]