"""
Views simplificadas para o Dashboard - Sistema Interno MONITOUR
"""
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib import messages

class LoginView(auth_views.LoginView):
    """Login personalizado para sistema interno"""
    template_name = 'dashboard/auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:dashboard')

class LogoutView(auth_views.LogoutView):
    """Logout do sistema"""
    next_page = reverse_lazy('dashboard:login')

class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard principal com estatísticas"""
    template_name = 'dashboard/home.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dados fictícios para demonstração
        context.update({
            'total_packages': 10,
            'active_packages': 8,
            'total_sales': 25,
            'pending_inquiries': 3,
            'monthly_revenue': 15500.00,
            'recent_sales': [],
            'recent_inquiries': [],
        })
        
        return context

# Views temporárias simples
class PackageListView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/simple_page.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Lista de Pacotes'
        context['message'] = 'Funcionalidade em desenvolvimento'
        return context

class SaleListView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/simple_page.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Lista de Vendas'
        context['message'] = 'Funcionalidade em desenvolvimento'
        return context

class InquiryListView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/simple_page.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Lista de Consultas'
        context['message'] = 'Funcionalidade em desenvolvimento'
        return context

class DestinationListView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/simple_page.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Lista de Destinos'
        context['message'] = 'Funcionalidade em desenvolvimento'
        return context

class CategoryListView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/simple_page.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Lista de Categorias'
        context['message'] = 'Funcionalidade em desenvolvimento'
        return context

class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/simple_page.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Relatórios'
        context['message'] = 'Relatórios em desenvolvimento'
        return context

# Views que não existem ainda - criar como placeholders
PackageDetailView = PackageListView
PackageCreateView = PackageListView
PackageUpdateView = PackageListView
PackageDeleteView = PackageListView
SaleDetailView = SaleListView
SaleStatusUpdateView = SaleListView
InquiryDetailView = InquiryListView
InquiryRespondView = InquiryListView
SalesReportView = ReportsView