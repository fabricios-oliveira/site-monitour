"""
Models para o Sistema Interno MONITOUR
Espelha e gerencia os dados do site público
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
import uuid

class TourPackageCategory(models.Model):
    """Categorias de Pacotes Turísticos"""
    name = models.CharField("Nome", max_length=100)
    description = models.TextField("Descrição", blank=True)
    slug = models.SlugField("URL Amigável", unique=True)
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Categoria de Pacote"
        verbose_name_plural = "Categorias de Pacotes"
        ordering = ['name']

    def __str__(self):
        return self.name

class Destination(models.Model):
    """Destinos Turísticos"""
    name = models.CharField("Nome", max_length=200)
    country = models.CharField("País", max_length=100)
    state = models.CharField("Estado/Província", max_length=100, blank=True)
    city = models.CharField("Cidade", max_length=100, blank=True)
    description = models.TextField("Descrição", blank=True)
    featured_image = models.ImageField("Imagem Principal", upload_to='destinations/', blank=True, null=True)
    slug = models.SlugField("URL Amigável", unique=True)
    is_featured = models.BooleanField("Destaque", default=False)
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.country}"

class TourPackage(models.Model):
    """Pacotes Turísticos - Modelo Principal"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Fácil'),
        ('medium', 'Médio'),
        ('hard', 'Difícil'),
        ('expert', 'Expert'),
    ]

    # Informações Básicas
    title = models.CharField("Título", max_length=200)
    slug = models.SlugField("URL Amigável", unique=True)
    description = models.TextField("Descrição")
    short_description = models.CharField("Descrição Curta", max_length=300)
    
    # Relacionamentos
    category = models.ForeignKey(TourPackageCategory, on_delete=models.CASCADE, verbose_name="Categoria")
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, verbose_name="Destino")
    
    # Detalhes do Pacote
    duration_days = models.PositiveIntegerField("Duração (dias)")
    duration_nights = models.PositiveIntegerField("Duração (noites)")
    max_participants = models.PositiveIntegerField("Máximo de Participantes", default=20)
    min_participants = models.PositiveIntegerField("Mínimo de Participantes", default=2)
    difficulty = models.CharField("Dificuldade", max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    
    # Preços e Disponibilidade
    price_per_person = models.DecimalField("Preço por Pessoa", max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField("Desconto (%)", max_digits=5, decimal_places=2, default=0)
    available_spots = models.PositiveIntegerField("Vagas Disponíveis", default=0)
    
    # Datas
    start_date = models.DateField("Data de Início", null=True, blank=True)
    end_date = models.DateField("Data de Término", null=True, blank=True)
    booking_deadline = models.DateField("Prazo para Reserva", null=True, blank=True)
    
    # Inclusões
    includes = models.TextField("O que está incluído", blank=True)
    excludes = models.TextField("O que não está incluído", blank=True)
    
    # Imagens
    featured_image = models.ImageField("Imagem Principal", upload_to='packages/', blank=True, null=True)
    
    # Status e Controle
    is_active = models.BooleanField("Ativo", default=True)
    is_featured = models.BooleanField("Destaque", default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Criado por")
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Pacote Turístico"
        verbose_name_plural = "Pacotes Turísticos"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('package_detail', kwargs={'slug': self.slug})

    @property
    def final_price(self):
        """Calcula o preço final com desconto"""
        if self.discount_percentage > 0:
            discount_amount = (self.price_per_person * self.discount_percentage) / 100
            return self.price_per_person - discount_amount
        return self.price_per_person

    @property
    def is_available(self):
        """Verifica se o pacote está disponível para reserva"""
        return self.is_active and self.available_spots > 0

class Sale(models.Model):
    """Vendas realizadas pelo site público"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmada'),
        ('paid', 'Paga'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Concluída'),
    ]

    PAYMENT_CHOICES = [
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('pix', 'PIX'),
        ('bank_transfer', 'Transferência Bancária'),
        ('installments', 'Parcelamento'),
    ]

    # Identificação
    order_id = models.UUIDField("ID do Pedido", default=uuid.uuid4, unique=True)
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, verbose_name="Pacote")
    
    # Dados do Cliente
    customer_name = models.CharField("Nome do Cliente", max_length=200)
    customer_email = models.EmailField("Email do Cliente")
    customer_phone = models.CharField("Telefone", max_length=20)
    customer_cpf = models.CharField("CPF", max_length=14, blank=True)
    customer_address = models.TextField("Endereço", blank=True)
    
    # Detalhes da Venda
    quantity = models.PositiveIntegerField("Quantidade de Pessoas", default=1)
    unit_price = models.DecimalField("Preço Unitário", max_digits=10, decimal_places=2)
    total_amount = models.DecimalField("Valor Total", max_digits=10, decimal_places=2)
    discount_applied = models.DecimalField("Desconto Aplicado", max_digits=10, decimal_places=2, default=0)
    
    # Pagamento
    payment_method = models.CharField("Método de Pagamento", max_length=20, choices=PAYMENT_CHOICES)
    payment_status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField("Data do Pagamento", null=True, blank=True)
    
    # Observações
    notes = models.TextField("Observações", blank=True)
    internal_notes = models.TextField("Notas Internas", blank=True)
    
    # Controle
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Processado por")

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"
        ordering = ['-created_at']

    def __str__(self):
        return f"Venda #{self.order_id} - {self.customer_name}"

    @property
    def final_amount(self):
        """Valor final após desconto"""
        return self.total_amount - self.discount_applied

class CustomerInquiry(models.Model):
    """Consultas de clientes vindas do site público"""
    INQUIRY_TYPES = [
        ('general', 'Informações Gerais'),
        ('booking', 'Reserva'),
        ('support', 'Suporte'),
        ('complaint', 'Reclamação'),
        ('suggestion', 'Sugestão'),
    ]

    STATUS_CHOICES = [
        ('new', 'Nova'),
        ('in_progress', 'Em Andamento'),
        ('resolved', 'Resolvida'),
        ('closed', 'Fechada'),
    ]

    # Identificação
    name = models.CharField("Nome", max_length=200)
    email = models.EmailField("Email")
    phone = models.CharField("Telefone", max_length=20, blank=True)
    
    # Conteúdo
    inquiry_type = models.CharField("Tipo", max_length=20, choices=INQUIRY_TYPES, default='general')
    subject = models.CharField("Assunto", max_length=200)
    message = models.TextField("Mensagem")
    package = models.ForeignKey(TourPackage, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Pacote Relacionado")
    
    # Status e Controle
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default='new')
    response = models.TextField("Resposta", blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Atribuído para")
    
    # Timestamps
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    responded_at = models.DateTimeField("Respondido em", null=True, blank=True)

    class Meta:
        verbose_name = "Consulta de Cliente"
        verbose_name_plural = "Consultas de Clientes"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
