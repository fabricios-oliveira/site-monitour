from django.contrib import admin
from .models import Destination, PackageCategory, TourPackage, BookingInquiry, Review


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'country', 'description']


@admin.register(PackageCategory)
class PackageCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(TourPackage)
class TourPackageAdmin(admin.ModelAdmin):
    list_display = ['title', 'destination', 'category', 'price', 'duration_days', 'status', 'featured', 'created_at']
    list_filter = ['status', 'featured', 'category', 'destination', 'difficulty', 'created_at']
    search_fields = ['title', 'description', 'destination__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'featured']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'slug', 'category', 'destination')
        }),
        ('Descrições', {
            'fields': ('short_description', 'description', 'highlights')
        }),
        ('Preços', {
            'fields': ('price', 'original_price', 'discount_percentage')
        }),
        ('Detalhes do Pacote', {
            'fields': ('duration_days', 'duration_nights', 'max_people', 'min_people', 'difficulty')
        }),
        ('Inclusos/Excludos', {
            'fields': ('includes', 'excludes')
        }),
        ('Disponibilidade', {
            'fields': ('available_from', 'available_until')
        }),
        ('Imagens', {
            'fields': ('featured_image', 'gallery_image_1', 'gallery_image_2', 'gallery_image_3')
        }),
        ('Controle', {
            'fields': ('status', 'featured')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('destination', 'category')


@admin.register(BookingInquiry)
class BookingInquiryAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'package', 'preferred_date', 'number_of_people', 'status', 'created_at']
    list_filter = ['status', 'preferred_date', 'created_at']
    search_fields = ['full_name', 'email', 'package__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Dados do Cliente', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Detalhes da Reserva', {
            'fields': ('package', 'preferred_date', 'number_of_people', 'special_requests')
        }),
        ('Controle', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('package')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'package', 'rating', 'approved', 'created_at']
    list_filter = ['rating', 'approved', 'created_at']
    search_fields = ['name', 'email', 'comment', 'package__title']
    readonly_fields = ['created_at']
    list_editable = ['approved']
    
    fieldsets = (
        ('Avaliação', {
            'fields': ('package', 'name', 'email', 'rating', 'comment')
        }),
        ('Moderação', {
            'fields': ('approved', 'created_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('package')
