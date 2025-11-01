from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from .models import Post, Category, Comment
from core.models import SiteSettings


def get_site_settings():
    """Helper para obter configurações do site"""
    settings_obj, created = SiteSettings.objects.get_or_create(pk=1)
    return settings_obj


def post_list(request):
    """Lista de posts do blog com paginação e filtros"""
    site_settings = get_site_settings()
    
    # Filtros
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    
    # Query base
    posts = Post.objects.filter(status='published').order_by('-published_at')
    
    # Filtro por categoria
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Busca por texto
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )
    
    # Paginação
    paginator = Paginator(posts, 9)  # 9 posts por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Posts em destaque (sidebar)
    featured_posts = Post.objects.filter(
        status='published',
        featured=True
    ).exclude(
        id__in=[post.id for post in page_obj]
    )[:5]
    
    # Categorias para o menu
    categories = Category.objects.all()
    
    # Categoria atual
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
    
    context = {
        'site_settings': site_settings,
        'page_obj': page_obj,
        'featured_posts': featured_posts,
        'categories': categories,
        'current_category': current_category,
        'search_query': search_query,
    }
    
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """Detalhe do post com comentários"""
    site_settings = get_site_settings()
    
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Comentários aprovados
    comments = post.comments.filter(approved=True).order_by('created_at')
    
    # Processar novo comentário
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        content = request.POST.get('content')
        
        if name and email and content:
            Comment.objects.create(
                post=post,
                name=name,
                email=email,
                content=content,
                approved=False  # Moderação necessária
            )
            messages.success(request, 'Comentário enviado! Será publicado após moderação.')
            return redirect('blog:post_detail', slug=post.slug)
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')
    
    # Posts relacionados (mesma categoria)
    related_posts = Post.objects.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id)[:3]
    
    # Posts populares (com mais comentários aprovados)
    popular_posts = Post.objects.filter(
        status='published'
    ).exclude(id=post.id)[:5]
    
    # Categorias
    categories = Category.objects.all()
    
    context = {
        'site_settings': site_settings,
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'popular_posts': popular_posts,
        'categories': categories,
    }
    
    return render(request, 'blog/post_detail.html', context)


def category_list(request):
    """Lista de todas as categorias"""
    site_settings = get_site_settings()
    categories = Category.objects.all()
    
    context = {
        'site_settings': site_settings,
        'categories': categories,
    }
    
    return render(request, 'blog/category_list.html', context)
