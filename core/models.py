from django.db import models
from PIL import Image


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'Nova'),
        ('read', 'Lida'),
        ('replied', 'Respondida'),
        ('archived', 'Arquivada'),
    ]
    
    name = models.CharField('Nome', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Telefone', max_length=20, blank=True)
    subject = models.CharField('Assunto', max_length=200)
    message = models.TextField('Mensagem')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Enviado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Mensagem de Contato'
        verbose_name_plural = 'Mensagens de Contato'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"


class Newsletter(models.Model):
    email = models.EmailField('Email', unique=True)
    name = models.CharField('Nome', max_length=100, blank=True)
    active = models.BooleanField('Ativo', default=True)
    created_at = models.DateTimeField('Inscrito em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletter'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.email}" if self.name else self.email


class Testimonial(models.Model):
    name = models.CharField('Nome', max_length=100)
    location = models.CharField('Localização', max_length=100, blank=True)
    testimonial = models.TextField('Depoimento')
    rating = models.IntegerField('Avaliação', choices=[(i, i) for i in range(1, 6)], default=5)
    photo = models.ImageField('Foto', upload_to='testimonials/', blank=True, null=True)
    active = models.BooleanField('Ativo', default=True)
    featured = models.BooleanField('Em Destaque', default=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Depoimento'
        verbose_name_plural = 'Depoimentos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.rating} estrelas"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            self.resize_image()
    
    def resize_image(self):
        if self.photo:
            img = Image.open(self.photo.path)
            if img.height > 400 or img.width > 400:
                img.thumbnail((400, 400))
                img.save(self.photo.path)


class SiteSettings(models.Model):
    # Informações da empresa
    company_name = models.CharField('Nome da Empresa', max_length=200, default='MONITOUR')
    company_description = models.TextField('Descrição da Empresa', blank=True)
    logo = models.ImageField('Logo', upload_to='site/', blank=True, null=True)
    
    # Contato
    phone = models.CharField('Telefone', max_length=20, blank=True)
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    address = models.TextField('Endereço', blank=True)
    
    # Redes sociais
    facebook = models.URLField('Facebook', blank=True)
    instagram = models.URLField('Instagram', blank=True)
    youtube = models.URLField('YouTube', blank=True)
    linkedin = models.URLField('LinkedIn', blank=True)
    
    # SEO
    site_title = models.CharField('Título do Site', max_length=200, default='MONITOUR - Turismo & Viagens')
    meta_description = models.TextField('Meta Descrição', max_length=300, blank=True)
    meta_keywords = models.CharField('Meta Keywords', max_length=500, blank=True)
    
    # Outros
    show_newsletter = models.BooleanField('Mostrar Newsletter', default=True)
    show_testimonials = models.BooleanField('Mostrar Depoimentos', default=True)
    maintenance_mode = models.BooleanField('Modo Manutenção', default=False)
    
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração do Site'
        verbose_name_plural = 'Configurações do Site'
    
    def __str__(self):
        return 'Configurações do Site MONITOUR'
    
    def save(self, *args, **kwargs):
        # Garantir que só existe uma instância
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        pass  # Não permitir deletar as configurações
