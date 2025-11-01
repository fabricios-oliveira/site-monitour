"""
Serializers para API do Sistema Interno MONITOUR
Converte models em JSON para comunicação com Site Público
"""
from rest_framework import serializers
from dashboard.models import (
    TourPackageCategory, 
    Destination, 
    TourPackage, 
    Sale, 
    CustomerInquiry
)

class TourPackageCategorySerializer(serializers.ModelSerializer):
    """Serializer para categorias de pacotes"""
    class Meta:
        model = TourPackageCategory
        fields = ['id', 'name', 'description', 'slug', 'is_active']

class DestinationSerializer(serializers.ModelSerializer):
    """Serializer para destinos"""
    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'country', 'state', 'city', 
            'description', 'featured_image', 'slug', 
            'is_featured', 'is_active'
        ]

class TourPackageListSerializer(serializers.ModelSerializer):
    """Serializer para lista de pacotes (resumido)"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    destination_name = serializers.CharField(source='destination.name', read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = TourPackage
        fields = [
            'id', 'title', 'slug', 'short_description',
            'category_name', 'destination_name', 'duration_days',
            'duration_nights', 'price_per_person', 'discount_percentage',
            'final_price', 'available_spots', 'featured_image',
            'is_active', 'is_featured', 'start_date', 'end_date'
        ]

class TourPackageDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalhes completos do pacote"""
    category = TourPackageCategorySerializer(read_only=True)
    destination = DestinationSerializer(read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = TourPackage
        fields = '__all__'

class SaleCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de vendas vindas do site público"""
    
    class Meta:
        model = Sale
        fields = [
            'package', 'customer_name', 'customer_email', 'customer_phone',
            'customer_cpf', 'customer_address', 'quantity', 'unit_price',
            'total_amount', 'discount_applied', 'payment_method', 'notes'
        ]
    
    def create(self, validated_data):
        # Calcula automaticamente alguns campos
        package = validated_data['package']
        quantity = validated_data['quantity']
        
        # Verifica disponibilidade
        if package.available_spots < quantity:
            raise serializers.ValidationError("Não há vagas suficientes disponíveis")
        
        # Atualiza vagas disponíveis
        package.available_spots -= quantity
        package.save()
        
        return Sale.objects.create(**validated_data)

class SaleSerializer(serializers.ModelSerializer):
    """Serializer para leitura de vendas"""
    package_title = serializers.CharField(source='package.title', read_only=True)
    final_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Sale
        fields = '__all__'

class CustomerInquiryCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de consultas vindas do site público"""
    
    class Meta:
        model = CustomerInquiry
        fields = [
            'name', 'email', 'phone', 'inquiry_type', 
            'subject', 'message', 'package'
        ]

class CustomerInquirySerializer(serializers.ModelSerializer):
    """Serializer para leitura de consultas"""
    package_title = serializers.CharField(source='package.title', read_only=True)
    
    class Meta:
        model = CustomerInquiry
        fields = '__all__'

# Serializers para estatísticas e dashboards
class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas do dashboard"""
    total_packages = serializers.IntegerField()
    active_packages = serializers.IntegerField()
    total_sales = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_inquiries = serializers.IntegerField()
    available_spots = serializers.IntegerField()
    
class RecentSalesSerializer(serializers.ModelSerializer):
    """Serializer para vendas recentes"""
    package_title = serializers.CharField(source='package.title', read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id', 'order_id', 'package_title', 'customer_name',
            'total_amount', 'payment_status', 'created_at'
        ]