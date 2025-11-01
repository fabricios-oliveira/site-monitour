from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Avg, Count
from .models import TourPackage, PackageCategory, Destination, BookingInquiry, Review
from core.models import SiteSettings


def get_site_settings():
    """Helper para obter configurações do site"""
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    return settings_obj


def package_list(request):
    """Lista de pacotes com filtros e paginação"""
    site_settings = get_site_settings()
    
    # Filtros
    category_slug = request.GET.get('category')
    destination_slug = request.GET.get('destination')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    duration = request.GET.get('duration')
    search_query = request.GET.get('q')
    
    # Query base - apenas pacotes ativos
    packages = TourPackage.objects.filter(status='active').order_by('-created_at')
    
    # Aplicar filtros
    if category_slug:
        packages = packages.filter(category__slug=category_slug)
    
    if destination_slug:
        packages = packages.filter(destination__slug=destination_slug)
    
    if min_price:
        try:
            packages = packages.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            packages = packages.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    if duration:
        try:
            packages = packages.filter(duration_days=int(duration))
        except ValueError:
            pass
    
    if search_query:
        packages = packages.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(destination__name__icontains=search_query)
        )
    
    # Paginação
    paginator = Paginator(packages, 12)  # 12 pacotes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Dados para filtros
    categories = PackageCategory.objects.all()
    destinations = Destination.objects.all()
    
    # Pacotes em destaque
    featured_packages = TourPackage.objects.filter(
        status='active',
        featured=True
    )[:6]
    
    context = {
        'site_settings': site_settings,
        'page_obj': page_obj,
        'categories': categories,
        'destinations': destinations,
        'featured_packages': featured_packages,
        'current_filters': {
            'category': category_slug,
            'destination': destination_slug,
            'min_price': min_price,
            'max_price': max_price,
            'duration': duration,
            'search': search_query,
        }
    }
    
    return render(request, 'packages/package_list.html', context)


def package_detail(request, slug):
    """Detalhe do pacote com formulário de reserva"""
    site_settings = get_site_settings()
    
    package = get_object_or_404(TourPackage, slug=slug, status='active')
    
    # Avaliações aprovadas
    reviews = package.reviews.filter(approved=True).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Processar formulário de reserva
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'booking':
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            preferred_date = request.POST.get('preferred_date')
            number_of_people = request.POST.get('number_of_people')
            special_requests = request.POST.get('special_requests', '')
            
            if all([full_name, email, phone, preferred_date, number_of_people]):
                BookingInquiry.objects.create(
                    package=package,
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    preferred_date=preferred_date,
                    number_of_people=int(number_of_people),
                    special_requests=special_requests
                )
                messages.success(request, 'Solicitação enviada! Entraremos em contato em breve.')
                return redirect('packages:package_detail', slug=package.slug)
            else:
                messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
        
        elif action == 'review':
            name = request.POST.get('name')
            email = request.POST.get('email')
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            
            if all([name, email, rating, comment]):
                Review.objects.create(
                    package=package,
                    name=name,
                    email=email,
                    rating=int(rating),
                    comment=comment,
                    approved=False  # Moderação necessária
                )
                messages.success(request, 'Avaliação enviada! Será publicada após moderação.')
                return redirect('packages:package_detail', slug=package.slug)
            else:
                messages.error(request, 'Por favor, preencha todos os campos da avaliação.')
    
    # Pacotes relacionados (mesma categoria ou destino)
    related_packages = TourPackage.objects.filter(
        status='active'
    ).filter(
        Q(category=package.category) | Q(destination=package.destination)
    ).exclude(id=package.id)[:4]
    
    # Galeria de imagens
    gallery_images = []
    for i in range(1, 4):
        image_field = getattr(package, f'gallery_image_{i}')
        if image_field:
            gallery_images.append(image_field)
    
    context = {
        'site_settings': site_settings,
        'package': package,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_packages': related_packages,
        'gallery_images': gallery_images,
    }
    
    return render(request, 'packages/package_detail.html', context)


def destination_list(request):
    """Lista de destinos"""
    site_settings = get_site_settings()
    destinations = Destination.objects.all().order_by('name')
    
    context = {
        'site_settings': site_settings,
        'destinations': destinations,
    }
    
    return render(request, 'packages/destination_list.html', context)


def category_list(request):
    """Lista de categorias de pacotes"""
    site_settings = get_site_settings()
    categories = PackageCategory.objects.all()
    
    context = {
        'site_settings': site_settings,
        'categories': categories,
    }
    
    return render(request, 'packages/category_list.html', context)
