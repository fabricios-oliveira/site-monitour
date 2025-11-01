from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
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
    from packages.models import Destination
    
    site_settings = get_site_settings()
    query = request.GET.get('q', '').strip()
    
    results = {
        'posts': [],
        'packages': [],
        'total': 0
    }
    
    # Destinos populares para a página inicial
    popular_destinations = Destination.objects.all()[:6]
    
    if query and len(query) >= 3:
        # Buscar posts
        posts = Post.objects.filter(
            status='published'
        ).filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct().order_by('-published_at')
        results['posts'] = posts[:10]
        
        # Buscar pacotes
        packages = TourPackage.objects.filter(
            status='active'
        ).filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(destination__name__icontains=query) |
            Q(destination__country__icontains=query)
        ).distinct().order_by('-created_at')
        results['packages'] = packages[:10]
        
        results['total'] = len(results['posts']) + len(results['packages'])
    
    context = {
        'site_settings': site_settings,
        'query': query,
        'results': results,
        'popular_destinations': popular_destinations,
    }
    
    return render(request, 'core/search.html', context)


@csrf_protect
@require_http_methods(["POST"])
def newsletter_subscribe(request):
    """Processar inscrição na newsletter"""
    email = request.POST.get('email', '').strip()
    
    if not email:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Email é obrigatório.'})
        messages.error(request, 'Email é obrigatório.')
        return redirect('core:home')
    
    # Verificar se o email já está cadastrado
    if Newsletter.objects.filter(email=email).exists():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Este email já está cadastrado em nossa newsletter!'})
        messages.warning(request, 'Este email já está cadastrado em nossa newsletter!')
        return redirect(request.META.get('HTTP_REFERER', 'core:home'))
    
    try:
        # Criar inscrição
        newsletter = Newsletter.objects.create(
            email=email,
            subscribed_at=timezone.now(),
            is_active=True
        )
        
        # Enviar email de boas-vindas (opcional)
        try:
            site_settings = get_site_settings()
            send_mail(
                subject=f'Bem-vindo(a) à Newsletter {site_settings.site_name}!',
                message=f'''
Olá!

Obrigado por se inscrever em nossa newsletter! 

Você receberá em primeira mão:
• Ofertas exclusivas de pacotes turísticos
• Dicas de viagem e destinos incríveis
• Novidades do blog MONITOUR
• Promoções especiais para assinantes

Estamos muito felizes em tê-lo(a) conosco!

Equipe MONITOUR
{site_settings.website_url}
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Erro ao enviar email de boas-vindas: {e}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Inscrição realizada com sucesso! Verifique seu email.'
            })
        
        messages.success(request, 'Inscrição realizada com sucesso! Obrigado por se juntar à nossa newsletter.')
        
    except Exception as e:
        print(f"Erro ao inscrever na newsletter: {e}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False, 
                'message': 'Erro ao processar inscrição. Tente novamente.'
            })
        
        messages.error(request, 'Erro ao processar inscrição. Tente novamente.')
    
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))
