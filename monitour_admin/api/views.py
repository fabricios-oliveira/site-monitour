"""
API Views para Sistema Interno MONITOUR
Endpoints para comunicação com Site Público
"""
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from dashboard.models import (
    TourPackageCategory, 
    Destination, 
    TourPackage, 
    Sale, 
    CustomerInquiry
)
from .serializers import (
    TourPackageCategorySerializer,
    DestinationSerializer,
    TourPackageListSerializer,
    TourPackageDetailSerializer,
    SaleCreateSerializer,
    SaleSerializer,
    CustomerInquiryCreateSerializer,
    CustomerInquirySerializer,
    DashboardStatsSerializer,
    RecentSalesSerializer
)

# Endpoints Públicos (para Site Público)
class TourPackageListAPIView(generics.ListAPIView):
    """Lista pacotes ativos para o site público"""
    serializer_class = TourPackageListSerializer
    permission_classes = [permissions.AllowAny]  # Público
    
    def get_queryset(self):
        queryset = TourPackage.objects.filter(is_active=True)
        
        # Filtros opcionais
        category = self.request.query_params.get('category')
        destination = self.request.query_params.get('destination')
        featured = self.request.query_params.get('featured')
        
        if category:
            queryset = queryset.filter(category__slug=category)
        if destination:
            queryset = queryset.filter(destination__slug=destination)
        if featured:
            queryset = queryset.filter(is_featured=True)
            
        return queryset.order_by('-created_at')

class TourPackageDetailAPIView(generics.RetrieveAPIView):
    """Detalhes de um pacote específico"""
    queryset = TourPackage.objects.filter(is_active=True)
    serializer_class = TourPackageDetailSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]  # Público

class CategoryListAPIView(generics.ListAPIView):
    """Lista categorias ativas"""
    queryset = TourPackageCategory.objects.filter(is_active=True)
    serializer_class = TourPackageCategorySerializer
    permission_classes = [permissions.AllowAny]  # Público

class DestinationListAPIView(generics.ListAPIView):
    """Lista destinos ativos"""
    queryset = Destination.objects.filter(is_active=True)
    serializer_class = DestinationSerializer
    permission_classes = [permissions.AllowAny]  # Público

# Endpoint para Vendas (Site Público -> Sistema Interno)
class SaleCreateAPIView(generics.CreateAPIView):
    """Endpoint para o site público registrar vendas"""
    serializer_class = SaleCreateSerializer
    permission_classes = [permissions.AllowAny]  # Público - mas será protegido por token em produção
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            sale = serializer.save()
            return Response({
                'success': True,
                'order_id': str(sale.order_id),
                'message': 'Venda registrada com sucesso!'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# Endpoint para Consultas (Site Público -> Sistema Interno)
class CustomerInquiryCreateAPIView(generics.CreateAPIView):
    """Endpoint para o site público registrar consultas"""
    serializer_class = CustomerInquiryCreateSerializer
    permission_classes = [permissions.AllowAny]  # Público
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            inquiry = serializer.save()
            return Response({
                'success': True,
                'message': 'Consulta registrada com sucesso!'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# Endpoints Privados (Sistema Interno)
class SaleListAPIView(generics.ListAPIView):
    """Lista vendas - apenas para sistema interno"""
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

class CustomerInquiryListAPIView(generics.ListAPIView):
    """Lista consultas - apenas para sistema interno"""
    queryset = CustomerInquiry.objects.all()
    serializer_class = CustomerInquirySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

# Dashboard e Estatísticas
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_stats(request):
    """Estatísticas para o dashboard do sistema interno"""
    
    # Estatísticas básicas
    total_packages = TourPackage.objects.count()
    active_packages = TourPackage.objects.filter(is_active=True).count()
    total_sales = Sale.objects.count()
    pending_inquiries = CustomerInquiry.objects.filter(status='new').count()
    
    # Receita total
    revenue_data = Sale.objects.filter(
        payment_status__in=['paid', 'completed']
    ).aggregate(
        total=Sum('total_amount')
    )
    total_revenue = revenue_data['total'] or 0
    
    # Vagas disponíveis
    spots_data = TourPackage.objects.filter(
        is_active=True
    ).aggregate(
        total=Sum('available_spots')
    )
    available_spots = spots_data['total'] or 0
    
    stats = {
        'total_packages': total_packages,
        'active_packages': active_packages,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'pending_inquiries': pending_inquiries,
        'available_spots': available_spots,
    }
    
    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_sales(request):
    """Vendas recentes para dashboard"""
    sales = Sale.objects.order_by('-created_at')[:10]
    serializer = RecentSalesSerializer(sales, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_health_check(request):
    """Health check da API"""
    return Response({
        'status': 'OK',
        'message': 'MONITOUR Admin API funcionando',
        'timestamp': timezone.now(),
        'version': '1.0.0'
    })
