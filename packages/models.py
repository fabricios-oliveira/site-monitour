from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
from decimal import Decimal


class Destination(models.Model):
    name = models.CharField('Nome do Destino', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    country = models.CharField('País', max_length=100)
    description = models.TextField('Descrição', blank=True)
    image = models.ImageField('Imagem', upload_to='destinations/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Destino'
        verbose_name_plural = 'Destinos'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.country}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class PackageCategory(models.Model):
    name = models.CharField('Nome', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Descrição', blank=True)
    icon = models.CharField('Ícone (Font Awesome)', max_length=50, default='fa-solid fa-map-location-dot')
    
    class Meta:
        verbose_name = 'Categoria de Pacote'
        verbose_name_plural = 'Categorias de Pacotes'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class TourPackage(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('sold_out', 'Esgotado'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Fácil'),
        ('moderate', 'Moderado'),
        ('challenging', 'Desafiador'),
    ]
    
    title = models.CharField('Título do Pacote', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    category = models.ForeignKey(PackageCategory, on_delete=models.CASCADE, verbose_name='Categoria')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, verbose_name='Destino')
    
    # Descrições
    short_description = models.TextField('Descrição Curta', max_length=300)
    description = models.TextField('Descrição Completa')
    highlights = models.TextField('Destaques do Pacote', help_text='Principais pontos turísticos e atrações')
    
    # Preços
    price = models.DecimalField('Preço', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    original_price = models.DecimalField('Preço Original', max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.IntegerField('Desconto (%)', default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Detalhes do pacote
    duration_days = models.PositiveIntegerField('Duração (dias)')
    duration_nights = models.PositiveIntegerField('Duração (noites)', default=0)
    max_people = models.PositiveIntegerField('Máximo de Pessoas', default=20)
    min_people = models.PositiveIntegerField('Mínimo de Pessoas', default=2)
    difficulty = models.CharField('Dificuldade', max_length=20, choices=DIFFICULTY_CHOICES, default='easy')
    
    # Inclusos
    includes = models.TextField('O que está incluso', help_text='Liste tudo que está incluído no pacote')
    excludes = models.TextField('O que não está incluso', blank=True, help_text='Liste o que não está incluído')
    
    # Datas e disponibilidade
    available_from = models.DateField('Disponível a partir de')
    available_until = models.DateField('Disponível até')
    
    # Imagens
    featured_image = models.ImageField('Imagem Principal', upload_to='packages/featured/')
    gallery_image_1 = models.ImageField('Galeria 1', upload_to='packages/gallery/', blank=True, null=True)
    gallery_image_2 = models.ImageField('Galeria 2', upload_to='packages/gallery/', blank=True, null=True)
    gallery_image_3 = models.ImageField('Galeria 3', upload_to='packages/gallery/', blank=True, null=True)
    
    # Status e controle
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    featured = models.BooleanField('Pacote em Destaque', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Pacote Turístico'
        verbose_name_plural = 'Pacotes Turísticos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
        # Redimensionar imagens se necessário
        self.resize_images()
    
    def resize_images(self):
        images = [self.featured_image, self.gallery_image_1, self.gallery_image_2, self.gallery_image_3]
        for image in images:
            if image:
                img = Image.open(image.path)
                if img.height > 800 or img.width > 1200:
                    img.thumbnail((1200, 800))
                    img.save(image.path)
    
    def get_absolute_url(self):
        return reverse('packages:package_detail', kwargs={'slug': self.slug})
    
    def get_discounted_price(self):
        if self.discount_percentage > 0 and self.original_price:
            return self.original_price * (1 - self.discount_percentage / 100)
        return self.price
    
    def has_discount(self):
        return self.discount_percentage > 0 and self.original_price and self.original_price > self.price
    
    def get_duration_text(self):
        if self.duration_nights > 0:
            return f"{self.duration_days} dias / {self.duration_nights} noites"
        return f"{self.duration_days} dias"


class BookingInquiry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('contacted', 'Contatado'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
    ]
    
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, verbose_name='Pacote')
    
    # Dados do cliente
    full_name = models.CharField('Nome Completo', max_length=200)
    email = models.EmailField('Email')
    phone = models.CharField('Telefone', max_length=20)
    
    # Detalhes da viagem
    preferred_date = models.DateField('Data Preferida')
    number_of_people = models.PositiveIntegerField('Número de Pessoas')
    special_requests = models.TextField('Solicitações Especiais', blank=True)
    
    # Controle
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Solicitação de Reserva'
        verbose_name_plural = 'Solicitações de Reservas'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reserva: {self.full_name} - {self.package.title}"


class Review(models.Model):
    package = models.ForeignKey(TourPackage, on_delete=models.CASCADE, related_name='reviews', verbose_name='Pacote')
    name = models.CharField('Nome', max_length=100)
    email = models.EmailField('Email')
    rating = models.IntegerField('Avaliação', validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField('Comentário')
    approved = models.BooleanField('Aprovado', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Avaliação de {self.name} - {self.package.title} ({self.rating}/5)"
