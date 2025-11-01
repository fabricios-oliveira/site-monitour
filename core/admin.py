from django.contrib import admin
from .models import ContactMessage, Newsletter, Testimonial, SiteSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'email', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['created_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Informações do Contato', {
            'fields': ('name', 'email', 'phone', 'subject')
        }),
        ('Mensagem', {
            'fields': ('message',)
        }),
        ('Controle', {
            'fields': ('status', 'created_at')
        }),
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'active', 'created_at']
    list_filter = ['active', 'created_at']
    search_fields = ['email', 'name']
    readonly_fields = ['created_at']
    list_editable = ['active']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'active', 'featured', 'created_at']
    list_filter = ['rating', 'active', 'featured', 'created_at']
    search_fields = ['name', 'location', 'testimonial']
    readonly_fields = ['created_at']
    list_editable = ['active', 'featured']
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('name', 'location', 'photo')
        }),
        ('Depoimento', {
            'fields': ('testimonial', 'rating')
        }),
        ('Controle', {
            'fields': ('active', 'featured', 'created_at')
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informações da Empresa', {
            'fields': ('company_name', 'company_description', 'logo')
        }),
        ('Contato', {
            'fields': ('phone', 'whatsapp', 'email', 'address')
        }),
        ('Redes Sociais', {
            'fields': ('facebook', 'instagram', 'youtube', 'linkedin')
        }),
        ('SEO', {
            'fields': ('site_title', 'meta_description', 'meta_keywords')
        }),
        ('Configurações do Site', {
            'fields': ('show_newsletter', 'show_testimonials', 'maintenance_mode')
        }),
    )
    
    def has_add_permission(self, request):
        # Só permite uma instância
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
