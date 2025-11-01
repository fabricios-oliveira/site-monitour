"""
Views simplificadas para o Dashboard - Sistema Interno MONITOUR
Versão corrigida sem dependências problemáticas
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

# Views de Pacotes
class PackageListView(LoginRequiredMixin, ListView):
    """Lista todos os pacotes"""
    model = TourPackage
    template_name = 'dashboard/packages/list.html'
    context_object_name = 'packages'
    paginate_by = 20
    login_url = reverse_lazy('dashboard:login')

class PackageDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um pacote"""
    model = TourPackage
    template_name = 'dashboard/packages/detail.html'
    context_object_name = 'package'
    login_url = reverse_lazy('dashboard:login')

class PackageCreateView(LoginRequiredMixin, CreateView):
    """Criar novo pacote"""
    model = TourPackage
    form_class = PackageForm
    template_name = 'dashboard/packages/form.html'
    success_url = reverse_lazy('dashboard:package_list')
    login_url = reverse_lazy('dashboard:login')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Pacote criado com sucesso!')
        return super().form_valid(form)

class PackageUpdateView(LoginRequiredMixin, UpdateView):
    """Editar pacote existente"""
    model = TourPackage
    form_class = PackageForm
    template_name = 'dashboard/packages/form.html'
    success_url = reverse_lazy('dashboard:package_list')
    login_url = reverse_lazy('dashboard:login')
    
    def form_valid(self, form):
        messages.success(self.request, 'Pacote atualizado com sucesso!')
        return super().form_valid(form)

class PackageDeleteView(LoginRequiredMixin, DeleteView):
    """Deletar pacote"""
    model = TourPackage
    template_name = 'dashboard/packages/delete.html'
    success_url = reverse_lazy('dashboard:package_list')
    login_url = reverse_lazy('dashboard:login')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Pacote deletado com sucesso!')
        return super().delete(request, *args, **kwargs)

# Views de Vendas
class SaleListView(LoginRequiredMixin, ListView):
    """Lista todas as vendas"""
    model = Sale
    template_name = 'dashboard/sales/list.html'
    context_object_name = 'sales'
    paginate_by = 20
    login_url = reverse_lazy('dashboard:login')
    
    def get_queryset(self):
        queryset = Sale.objects.order_by('-created_at')
        
        # Filtros
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(payment_status=status_filter)
        
        return queryset

class SaleDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de uma venda"""
    model = Sale
    template_name = 'dashboard/sales/detail.html'
    context_object_name = 'sale'
    login_url = reverse_lazy('dashboard:login')

class SaleStatusUpdateView(LoginRequiredMixin, FormView):
    """Atualizar status de uma venda"""
    form_class = SaleStatusForm
    template_name = 'dashboard/sales/status_update.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_object(self):
        return get_object_or_404(Sale, pk=self.kwargs['pk'])
    
    def get_success_url(self):
        return reverse_lazy('dashboard:sale_detail', kwargs={'pk': self.kwargs['pk']})
    
    def form_valid(self, form):
        sale = self.get_object()
        sale.payment_status = form.cleaned_data['status']
        sale.internal_notes = form.cleaned_data['notes']
        sale.processed_by = self.request.user
        
        if form.cleaned_data['status'] in ['paid', 'completed']:
            sale.payment_date = timezone.now()
        
        sale.save()
        messages.success(self.request, 'Status da venda atualizado!')
        return super().form_valid(form)

# Views de Consultas
class InquiryListView(LoginRequiredMixin, ListView):
    """Lista consultas de clientes"""
    model = CustomerInquiry
    template_name = 'dashboard/inquiries/list.html'
    context_object_name = 'inquiries'
    paginate_by = 20
    login_url = reverse_lazy('dashboard:login')

class InquiryDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de uma consulta"""
    model = CustomerInquiry
    template_name = 'dashboard/inquiries/detail.html'
    context_object_name = 'inquiry'
    login_url = reverse_lazy('dashboard:login')

class InquiryRespondView(LoginRequiredMixin, FormView):
    """Responder consulta de cliente"""
    form_class = InquiryResponseForm
    template_name = 'dashboard/inquiries/respond.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_object(self):
        return get_object_or_404(CustomerInquiry, pk=self.kwargs['pk'])
    
    def get_success_url(self):
        return reverse_lazy('dashboard:inquiry_detail', kwargs={'pk': self.kwargs['pk']})
    
    def form_valid(self, form):
        inquiry = self.get_object()
        inquiry.response = form.cleaned_data['response']
        inquiry.status = 'resolved'
        inquiry.assigned_to = self.request.user
        inquiry.responded_at = timezone.now()
        inquiry.save()
        
        messages.success(self.request, 'Resposta enviada com sucesso!')
        return super().form_valid(form)

# Views de Destinos e Categorias
class DestinationListView(LoginRequiredMixin, ListView):
    """Lista destinos"""
    model = Destination
    template_name = 'dashboard/destinations/list.html'
    context_object_name = 'destinations'
    login_url = reverse_lazy('dashboard:login')

class CategoryListView(LoginRequiredMixin, ListView):
    """Lista categorias"""
    model = TourPackageCategory
    template_name = 'dashboard/categories/list.html'
    context_object_name = 'categories'
    login_url = reverse_lazy('dashboard:login')

# Views de Relatórios
class ReportsView(LoginRequiredMixin, TemplateView):
    """Página principal de relatórios"""
    template_name = 'dashboard/reports/home.html'
    login_url = reverse_lazy('dashboard:login')

class SalesReportView(LoginRequiredMixin, TemplateView):
    """Relatório de vendas"""
    template_name = 'dashboard/reports/sales.html'
    login_url = reverse_lazy('dashboard:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas de vendas
        context.update({
            'sales_by_status': self.get_sales_by_status(),
            'monthly_sales': self.get_monthly_sales(),
            'top_packages': self.get_top_packages(),
        })
        
        return context
    
    def get_sales_by_status(self):
        """Vendas por status"""
        return Sale.objects.values('payment_status').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        )
    
    def get_monthly_sales(self):
        """Vendas dos últimos 12 meses"""
        # Implementar lógica de vendas mensais
        return []
    
    def get_top_packages(self):
        """Pacotes mais vendidos"""
        return Sale.objects.values('package__title').annotate(
            total_sales=Count('id'),
            total_revenue=Sum('total_amount')
        ).order_by('-total_sales')[:10]
