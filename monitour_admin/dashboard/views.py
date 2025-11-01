"""
Views simplificadas para o Dashboard - Sistema Interno MONITOUR
Versão limpa e funcional
"""
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required

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
        
        # Dados mockados para demonstração
        context.update({
            'total_packages': 15,
            'active_packages': 12,
            'total_sales': 45,
            'pending_inquiries': 8,
            'monthly_revenue': 85000.00,
            'recent_activities': [
                'Nova venda: Pacote Paris Romântico',
                'Consulta respondida: Rio de Janeiro',
                'Pacote atualizado: Amazônia Adventure',
            ]
        })
        return context

# Views simplificadas usando function-based views
@login_required(login_url='/login/')
def packages_view(request):
    """Página de pacotes - em desenvolvimento"""
    return render(request, 'dashboard/simple_page.html', {
        'page_title': 'Pacotes Turísticos',
        'content': 'Gestão de pacotes turísticos em desenvolvimento.'
    })

@login_required(login_url='/login/')
def sales_view(request):
    """Página de vendas - em desenvolvimento"""
    return render(request, 'dashboard/simple_page.html', {
        'page_title': 'Vendas',
        'content': 'Gestão de vendas em desenvolvimento.'
    })

@login_required(login_url='/login/')
def inquiries_view(request):
    """Página de consultas - em desenvolvimento"""
    return render(request, 'dashboard/simple_page.html', {
        'page_title': 'Consultas de Clientes',
        'content': 'Gestão de consultas em desenvolvimento.'
    })

@login_required(login_url='/login/')
def categories_view(request):
    """Página de categorias - em desenvolvimento"""
    return render(request, 'dashboard/simple_page.html', {
        'page_title': 'Categorias',
        'content': 'Gestão de categorias em desenvolvimento.'
    })

@login_required(login_url='/login/')
def destinations_view(request):
    """Página de destinos - em desenvolvimento"""
    return render(request, 'dashboard/simple_page.html', {
        'page_title': 'Destinos',
        'content': 'Gestão de destinos em desenvolvimento.'
    })

@login_required(login_url='/login/')
def reports_view(request):
    """Página de relatórios - em desenvolvimento"""
    return render(request, 'dashboard/simple_page.html', {
        'page_title': 'Relatórios',
        'content': 'Dashboard de relatórios em desenvolvimento.'
    })

@login_required(login_url='/login/')
def users_view(request):
    """Página de usuários - em desenvolvimento"""
    return render(request, 'dashboard/simple_page.html', {
        'page_title': 'Usuários do Sistema',
        'content': 'Gestão de usuários em desenvolvimento.'
    })

@login_required(login_url='/login/')
def settings_view(request):
    """Página de configurações - em desenvolvimento"""
    return render(request, 'dashboard/simple_page.html', {
        'page_title': 'Configurações',
        'content': 'Página de configurações do sistema em desenvolvimento.'
    })