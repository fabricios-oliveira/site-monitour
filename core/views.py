from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage, Newsletter, Testimonial, SiteSettings
from blog.models import Post
from packages.models import TourPackage


def get_site_settings():
    """Helper para obter configurações do site"""
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    return settings_obj


def home(request):
    """Página inicial com destaques"""
    site_settings = get_site_settings()
    
    # Posts em destaque
    featured_posts = Post.objects.filter(
        status='published', 
        featured=True
    ).order_by('-published_at')[:3]
    
    # Pacotes em destaque
    featured_packages = TourPackage.objects.filter(
        status='active', 
        featured=True
    ).order_by('-created_at')[:6]
    
    # Depoimentos
    testimonials = Testimonial.objects.filter(
        active=True, 
        featured=True
    ).order_by('-created_at')[:6]
    
    context = {
        'site_settings': site_settings,
        'featured_posts': featured_posts,
        'featured_packages': featured_packages,
        'testimonials': testimonials,
    }
    
    return render(request, 'core/home.html', context)


def about(request):
    """Página sobre nós"""
    site_settings = get_site_settings()
    
    # Estatísticas da empresa (exemplo)
    stats = {
        'years_experience': 10,
        'happy_clients': 5000,
        'destinations': 50,
        'tours_completed': 1200,
    }
    
    # Depoimentos para a página sobre
    testimonials = Testimonial.objects.filter(active=True)[:8]
    
    context = {
        'site_settings': site_settings,
        'stats': stats,
        'testimonials': testimonials,
    }
    
    return render(request, 'core/about.html', context)


def contact(request):
    """Página e processamento de contato"""
    site_settings = get_site_settings()
    
    if request.method == 'POST':
        # Processar formulário de contato
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            # Salvar no banco
            contact_msg = ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            
            # Enviar email (opcional)
            try:
                send_mail(
                    subject=f'Contato do Site: {subject}',
                    message=f'Nome: {name}\nEmail: {email}\nTelefone: {phone}\n\nMensagem:\n{message}',
                    from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else email,
                    recipient_list=[site_settings.email] if site_settings.email else ['contato@monitour.com.br'],
                    fail_silently=True,
                )
            except:
                pass  # Se falhar no envio de email, não quebrar a aplicação
            
            messages.success(request, 'Mensagem enviada com sucesso! Entraremos em contato em breve.')
            return redirect('core:contact')
        else:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
    
    context = {
        'site_settings': site_settings,
    }
    
    return render(request, 'core/contact.html', context)


@require_http_methods(["POST"])
def newsletter_signup(request):
    """Inscrição na newsletter"""
    email = request.POST.get('email')
    name = request.POST.get('name', '')
    
    if email:
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'name': name, 'active': True}
        )
        
        if created:
            messages.success(request, 'Inscrição realizada com sucesso!')
        else:
            if newsletter.active:
                messages.info(request, 'Este email já está inscrito na nossa newsletter.')
            else:
                newsletter.active = True
                newsletter.save()
                messages.success(request, 'Sua inscrição foi reativada!')
    else:
        messages.error(request, 'Por favor, informe um email válido.')
    
    # Redirecionar de volta para onde veio
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))


def privacy_policy(request):
    """Política de privacidade"""
    site_settings = get_site_settings()
    
    context = {
        'site_settings': site_settings,
    }
    
    return render(request, 'core/privacy_policy.html', context)


def terms_of_use(request):
    """Termos de uso"""
    site_settings = get_site_settings()
    
    context = {
        'site_settings': site_settings,
    }
    
    return render(request, 'core/terms_of_use.html', context)


def search(request):
    """Busca global"""
    site_settings = get_site_settings()
    query = request.GET.get('q', '').strip()
    
    results = {
        'posts': [],
        'packages': [],
        'total': 0
    }
    
    if query and len(query) >= 3:
        # Buscar posts
        posts = Post.objects.filter(
            status='published',
            title__icontains=query
        ) | Post.objects.filter(
            status='published',
            content__icontains=query
        )
        results['posts'] = posts[:10]
        
        # Buscar pacotes
        packages = TourPackage.objects.filter(
            status='active',
            title__icontains=query
        ) | TourPackage.objects.filter(
            status='active',
            description__icontains=query
        )
        results['packages'] = packages[:10]
        
        results['total'] = len(results['posts']) + len(results['packages'])
    
    context = {
        'site_settings': site_settings,
        'query': query,
        'results': results,
    }
    
    return render(request, 'core/search.html', context)
