from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import random

from core.models import SiteSettings, Testimonial, Newsletter
from blog.models import Category, Post, Comment
from packages.models import Destination, TourPackage, BookingInquiry, Review


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo para desenvolvimento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa os dados existentes antes de popular',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Limpando dados existentes...')
            self.clear_data()

        self.stdout.write('Criando dados de exemplo...')
        
        # Criar usuário admin se não existir
        self.create_admin_user()
        
        # Configurações do site
        self.create_site_settings()
        
        # Categorias do blog
        self.create_blog_categories()
        
        # Destinos turísticos
        self.create_destinations()
        
        # Posts do blog
        self.create_blog_posts()
        
        # Pacotes turísticos
        self.create_tour_packages()
        
        # Depoimentos
        self.create_testimonials()
        
        # Newsletter
        self.create_newsletter_subscribers()
        
        # Comentários nos posts
        self.create_comments()
        
        # Reservas e avaliações
        self.create_bookings_and_reviews()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Dados de exemplo criados com sucesso!')
        )

    def clear_data(self):
        """Limpa os dados de exemplo"""
        Comment.objects.all().delete()
        Review.objects.all().delete()
        BookingInquiry.objects.all().delete()
        TourPackage.objects.all().delete()
        Post.objects.all().delete()
        Destination.objects.all().delete()
        Category.objects.all().delete()
        Testimonial.objects.all().delete()
        Newsletter.objects.all().delete()
        
        # Não limpar SiteSettings pois é singleton
        
        self.stdout.write('Dados limpos!')

    def create_admin_user(self):
        """Cria usuário administrador"""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@monitour.com.br',
                password='admin123',
                first_name='MONITOUR',
                last_name='Admin'
            )
            self.stdout.write('👤 Usuário admin criado (admin/admin123)')

    def create_site_settings(self):
        """Configura as definições do site"""
        settings, created = SiteSettings.objects.get_or_create(pk=1)
        settings.site_name = 'MONITOUR'
        settings.tagline = 'Sua próxima aventura começa aqui!'
        settings.description = 'A MONITOUR é especializada em criar experiências únicas de viagem, oferecendo pacotes turísticos personalizados para os mais diversos destinos.'
        settings.email = 'contato@monitour.com.br'
        settings.phone = '(11) 99999-9999'
        settings.whatsapp = '5511999999999'
        settings.address = 'Rua das Viagens, 123 - Centro - São Paulo - SP'
        settings.facebook_url = 'https://facebook.com/monitour'
        settings.instagram_url = 'https://instagram.com/monitour'
        settings.twitter_url = 'https://twitter.com/monitour'
        settings.youtube_url = 'https://youtube.com/monitour'
        settings.website_url = 'https://www.monitour.com.br'
        settings.save()
        
        self.stdout.write('⚙️  Configurações do site atualizadas')

    def create_blog_categories(self):
        """Cria categorias para o blog"""
        categories_data = [
            {'name': 'Dicas de Viagem', 'slug': 'dicas-viagem', 'description': 'Dicas essenciais para uma viagem perfeita'},
            {'name': 'Destinos Nacionais', 'slug': 'destinos-nacionais', 'description': 'Explore as belezas do Brasil'},
            {'name': 'Destinos Internacionais', 'slug': 'destinos-internacionais', 'description': 'Aventuras pelo mundo'},
            {'name': 'Gastronomia', 'slug': 'gastronomia', 'description': 'Sabores únicos de cada destino'},
            {'name': 'Aventura', 'slug': 'aventura', 'description': 'Para os amantes da adrenalina'},
            {'name': 'Cultura', 'slug': 'cultura', 'description': 'Tradições e costumes locais'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'📂 Categoria criada: {category.name}')

    def create_destinations(self):
        """Cria destinos turísticos"""
        destinations_data = [
            {
                'name': 'Rio de Janeiro - RJ',
                'slug': 'rio-de-janeiro',
                'description': 'A Cidade Maravilhosa com suas praias icônicas, Cristo Redentor e Pão de Açúcar.',
                'country': 'Brasil'
            },
            {
                'name': 'Fernando de Noronha - PE',
                'slug': 'fernando-noronha',
                'description': 'Paraíso ecológico com praias paradisíacas e vida marinha exuberante.',
                'country': 'Brasil'
            },
            {
                'name': 'Gramado - RS',
                'slug': 'gramado',
                'description': 'Charme europeu no coração da Serra Gaúcha.',
                'country': 'Brasil'
            },
            {
                'name': 'Paris - França',
                'slug': 'paris-franca',
                'description': 'A Cidade Luz com sua arte, cultura e romantismo únicos.',
                'country': 'França'
            },
            {
                'name': 'Maldivas',
                'slug': 'maldivas',
                'description': 'Ilhas paradisíacas com águas cristalinas e resorts de luxo.',
                'country': 'Maldivas'
            },
            {
                'name': 'Tokyo - Japão',
                'slug': 'tokyo-japao',
                'description': 'Metrópole futurista que mescla tradição e modernidade.',
                'country': 'Japão'
            },
        ]
        
        for dest_data in destinations_data:
            destination, created = Destination.objects.get_or_create(
                slug=dest_data['slug'],
                defaults=dest_data
            )
            if created:
                self.stdout.write(f'🗺️  Destino criado: {destination.name}')

    def create_blog_posts(self):
        """Cria posts para o blog"""
        admin_user = User.objects.get(username='admin')
        categories = Category.objects.all()
        
        posts_data = [
            {
                'title': '10 Dicas Essenciais para sua Primeira Viagem Internacional',
                'slug': '10-dicas-primeira-viagem-internacional',
                'excerpt': 'Está planejando sua primeira viagem para fora do país? Confira nossas dicas essenciais para uma experiência inesquecível.',
                'content': '''
Fazer a primeira viagem internacional é um marco na vida de qualquer pessoa. A expectativa, o nervosismo e a alegria se misturam criando uma experiência única. Para te ajudar a aproveitar ao máximo essa aventura, preparamos 10 dicas essenciais.

## 1. Documentação em Ordem

Antes de mais nada, verifique se seu passaporte está válido e se você precisa de visto para o destino escolhido. Alguns países exigem que o passaporte tenha pelo menos 6 meses de validade.

## 2. Seguro Viagem

Nunca, jamais, viaje sem seguro! Além de ser obrigatório em muitos países, ele pode te salvar de grandes prejuízos financeiros em caso de emergência médica ou outros problemas.

## 3. Pesquise sobre o Destino

Conheça a cultura local, costumes, moeda, clima e atrações principais. Isso te ajudará a planejar melhor o roteiro e evitar situações constrangedoras.

## 4. Planeje o Orçamento

Calcule todos os custos: passagens, hospedagem, alimentação, transporte local, atrações e compras. Sempre reserve um dinheiro extra para emergências.

## 5. Escolha a Hospedagem Adequada

Pesquise bem a localização, leia avaliações e considere suas necessidades. Hotéis no centro podem ser mais caros, mas economizam tempo e dinheiro com transporte.

## 6. Aprenda o Básico do Idioma

Mesmo que seja apenas "obrigado", "por favor" e "onde fica o banheiro?", conhecer algumas palavras básicas pode fazer toda a diferença.

## 7. Organize as Malas Inteligentemente

Leve roupas adequadas ao clima e ocasiões. Não esqueça dos medicamentos pessoais e adaptadores de tomada.

## 8. Mantenha Contato com Casa

Informe familiares sobre seu itinerário e mantenha formas de comunicação ativas. WhatsApp internacional é uma ótima opção.

## 9. Tenha Sempre um Plano B

Voos atrasam, hotéis podem ter problemas. Sempre tenha alternativas e mantenha a calma quando algo não sair como planejado.

## 10. Aproveite Cada Momento

Por último e mais importante: desconecte-se das preocupações e viva intensamente cada momento dessa experiência única!

Lembre-se: a primeira viagem internacional é sempre especial, mas certamente não será a última! 🌍✈️
                ''',
                'category': 'dicas-viagem',
                'featured': True,
                'status': 'published'
            },
            {
                'title': 'Fernando de Noronha: Guia Completo do Paraíso Brasileiro',
                'slug': 'fernando-noronha-guia-completo',
                'excerpt': 'Descubra tudo sobre Fernando de Noronha: quando ir, o que fazer, onde ficar e dicas essenciais para aproveitar este paraíso.',
                'content': '''
Fernando de Noronha é, sem dúvida, um dos destinos mais desejados do Brasil. Este arquipélago vulcânico oferece algumas das praias mais bonitas do mundo, vida marinha exuberante e paisagens de tirar o fôlego.

## Quando Ir

A melhor época para visitar Fernando de Noronha é durante a estação seca, de setembro a março. Neste período, as águas estão mais calmas e cristalinas, ideais para mergulho e snorkeling.

### Estação Seca (Set-Mar)
- Mar mais calmo
- Melhor visibilidade subaquática
- Ideal para mergulho

### Estação Chuvosa (Abr-Ago)
- Ondas maiores (ideal para surf)
- Menos turistas
- Preços mais baixos

## O Que Fazer

### Praias Imperdíveis
- **Baía do Sancho**: Eleita várias vezes a praia mais bonita do mundo
- **Praia do Leão**: Ideal para ver o nascer do sol
- **Baía dos Porcos**: Piscinas naturais incríveis
- **Praia da Conceição**: Perfeita para o pôr do sol

### Atividades
- Mergulho livre e autônomo
- Trilhas ecológicas
- Observação de golfinhos
- Passeio de barco
- Surf (na época certa)

## Onde Ficar

A ilha oferece opções para todos os orçamentos:
- **Pousadas de luxo**: Para quem quer conforto total
- **Pousadas econômicas**: Boa opção custo-benefício
- **Casas de aluguel**: Ideal para grupos

## Dicas Importantes

### Taxa de Preservação
É obrigatório pagar a Taxa de Preservação Ambiental (TPA) diariamente. O valor varia conforme os dias de permanência.

### Limite de Visitantes
A ilha tem limite diário de visitantes, então reserve com antecedência, especialmente na alta temporada.

### O Que Levar
- Protetor solar biodegradável
- Equipamento de snorkeling próprio
- Roupas leves e confortáveis
- Câmera à prova d'água

### Respeite a Natureza
- Não toque nos corais
- Não alimente os peixes
- Mantenha distância dos golfinhos
- Leve todo o lixo com você

Fernando de Noronha é realmente um paraíso que deve ser preservado. Visite com consciência e leve apenas fotos, deixando apenas pegadas! 🐬🏝️
                ''',
                'category': 'destinos-nacionais',
                'featured': True,
                'status': 'published'
            },
            {
                'title': 'Paris: Roteiro de 5 Dias na Cidade Luz',
                'slug': 'paris-roteiro-5-dias',
                'excerpt': 'Um roteiro completo para aproveitar o melhor de Paris em 5 dias, incluindo atrações principais, dicas de restaurantes e transporte.',
                'content': '''
Paris, a Cidade Luz, é um destino que encanta visitantes do mundo inteiro. Com sua arquitetura deslumbrante, museus mundialmente famosos e gastronomia excepcional, 5 dias é o tempo ideal para conhecer o essencial da capital francesa.

## Dia 1: Centro Histórico e Île de la Cité

### Manhã
- **Notre-Dame** (externa, devido à restauração)
- **Sainte-Chapelle**: Vitrais espetaculares
- **Conciergerie**: História da Revolução Francesa

### Tarde
- **Museu do Louvre**: Reserve pelo menos 3 horas
- **Jardim das Tulherias**: Perfeito para um passeio relaxante

### Noite
- Jantar no **Quartier Latin**
- Caminhada pela **Pont Neuf** iluminada

## Dia 2: Torre Eiffel e Trocadéro

### Manhã
- **Torre Eiffel**: Suba cedo para evitar filas
- **Jardins do Trocadéro**: Melhores fotos da Torre Eiffel

### Tarde
- **Musée d'Orsay**: Impressionistas imperdíveis
- **Passeio pelo Sena**: Batobus ou cruzeiro

### Noite
- **Bairro Saint-Germain-des-Prés**
- Jantar em bistrô típico parisiense

## Dia 3: Montmartre e Sacré-Cœur

### Manhã
- **Basílica de Sacré-Cœur**
- **Place du Tertre**: Artistas de rua
- **Moulin Rouge** (externa)

### Tarde
- **Marais**: Bairro histórico charmoso
- **Place des Vosges**: Praça mais antiga de Paris
- Shopping nas **Galeries Lafayette**

### Noite
- **Cruzeiro noturno no Sena**

## Dia 4: Versailles (Bate e Volta)

### Dia Todo
- **Palácio de Versailles**: Apartamentos reais
- **Jardins de Versailles**: Imperdíveis na primavera/verão
- **Petit Trianon**: Refúgio de Maria Antonieta

**Dica**: Compre o passe completo e vá cedo!

## Dia 5: Champs-Élysées e Relaxamento

### Manhã
- **Arc de Triomphe**: Vista panorâmica de Paris
- **Champs-Élysées**: Compras e cafés

### Tarde
- **Jardim de Luxemburgo**: Perfeito para relaxar
- **Panthéon**: Túmulos de personalidades francesas

### Noite
- **Quartier Latin**: Última noite parisiense
- **Shakespeare and Company**: Livraria histórica

## Dicas Essenciais

### Transporte
- **Metro**: Compre o passe semanal Navigo
- **Vélib'**: Bicicletas públicas
- **A pé**: Paris é uma cidade para caminhar

### Gastronomia
- **Café da manhã**: Croissant e café au lait
- **Almoço**: Croque-monsieur em bistrô
- **Jantar**: Experimente o menu degustação

### Compras
- **Souvenirs**: Evite áreas turísticas
- **Moda**: Rue de Rivoli e Marais
- **Gourmet**: Mercados locais

### Economia
- **Museus gratuitos**: Primeiro domingo do mês
- **Happy hour**: Muitos bares têm preços especiais
- **Picnic**: Compre no supermercado e faça picnic nos parques

Paris é uma cidade que merece ser saboreada com calma. Não tente ver tudo de uma vez - deixe espaço para se perder nas ruas e descobrir seus próprios cantinhos especiais! 🥐🗼
                ''',
                'category': 'destinos-internacionais',
                'featured': True,
                'status': 'published'
            },
        ]
        
        for i, post_data in enumerate(posts_data):
            category = Category.objects.get(slug=post_data['category'])
            
            post, created = Post.objects.get_or_create(
                slug=post_data['slug'],
                defaults={
                    'title': post_data['title'],
                    'excerpt': post_data['excerpt'],
                    'content': post_data['content'],
                    'author': admin_user,
                    'category': category,
                    'featured': post_data['featured'],
                    'status': post_data['status'],
                    'published_at': timezone.now() - timedelta(days=i*2)
                }
            )
            if created:
                self.stdout.write(f'📝 Post criado: {post.title}')

    def create_tour_packages(self):
        """Cria pacotes turísticos"""
        from datetime import date, timedelta
        
        # Primeiro criar categorias
        categories_data = [
            {'name': 'Pacotes Nacionais', 'slug': 'nacionais', 'description': 'Destinos dentro do Brasil'},
            {'name': 'Pacotes Internacionais', 'slug': 'internacionais', 'description': 'Destinos ao redor do mundo'},
            {'name': 'Lua de Mel', 'slug': 'lua-de-mel', 'description': 'Pacotes românticos para casais'},
        ]
        
        for cat_data in categories_data:
            from packages.models import PackageCategory
            category, created = PackageCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'📦 Categoria criada: {category.name}')
        
        # Agora criar pacotes
        packages_data = [
            {
                'title': 'Rio de Janeiro Completo - 4 Dias',
                'slug': 'rio-janeiro-completo-4-dias',
                'short_description': 'Explore o melhor do Rio de Janeiro em 4 dias inesquecíveis!',
                'description': 'Explore o melhor do Rio de Janeiro em 4 dias inesquecíveis! Inclui hospedagem, city tour, Cristo Redentor, Pão de Açúcar e muito mais.',
                'highlights': 'Cristo Redentor, Pão de Açúcar, Copacabana, Ipanema, Centro Histórico',
                'includes': 'Hospedagem, café da manhã, transfers, ingressos para atrações',
                'destination_slug': 'rio-de-janeiro',
                'category_slug': 'nacionais',
                'duration_days': 4,
                'duration_nights': 3,
                'price': Decimal('1299.00'),
                'discount_percentage': 15,
                'max_people': 20,
                'featured': True,
                'status': 'active'
            },
            {
                'title': 'Fernando de Noronha - Pacote Ecológico 5 Dias',
                'slug': 'fernando-noronha-ecologico-5-dias',
                'short_description': 'Viva uma experiência única no paraíso brasileiro!',
                'description': 'Viva uma experiência única no paraíso brasileiro! Inclui pousada, mergulho, trilhas e observação de golfinhos.',
                'highlights': 'Baía do Sancho, Mergulho com golfinhos, Trilhas ecológicas, Praias paradisíacas',
                'includes': 'Hospedagem, café da manhã, passeios ecológicos, equipamentos de mergulho',
                'destination_slug': 'fernando-noronha',
                'category_slug': 'nacionais',
                'duration_days': 5,
                'duration_nights': 4,
                'price': Decimal('2899.00'),
                'discount_percentage': 10,
                'max_people': 12,
                'featured': True,
                'status': 'active'
            },
            {
                'title': 'Paris Romântico - Lua de Mel 7 Dias',
                'slug': 'paris-romantico-lua-mel-7-dias',
                'short_description': 'O pacote perfeito para sua lua de mel na Cidade Luz!',
                'description': 'O pacote perfeito para sua lua de mel na Cidade Luz! Inclui hotel boutique, jantar romântico na Torre Eiffel e cruzeiro pelo Sena.',
                'highlights': 'Torre Eiffel, Louvre, Cruzeiro no Sena, Versailles, Hotel boutique',
                'includes': 'Hotel boutique, café da manhã, jantar romântico, ingressos para museus, cruzeiro',
                'destination_slug': 'paris-franca',
                'category_slug': 'lua-de-mel',
                'duration_days': 7,
                'duration_nights': 6,
                'price': Decimal('4599.00'),
                'discount_percentage': 20,
                'max_people': 2,
                'featured': True,
                'status': 'active'
            },
        ]
        
        for pack_data in packages_data:
            try:
                destination = Destination.objects.get(slug=pack_data['destination_slug'])
                category = PackageCategory.objects.get(slug=pack_data['category_slug'])
                
                # Calcular datas de disponibilidade
                today = date.today()
                available_from = today
                available_until = today + timedelta(days=365)
                
                package_data = {
                    'title': pack_data['title'],
                    'short_description': pack_data['short_description'],
                    'description': pack_data['description'],
                    'highlights': pack_data['highlights'],
                    'includes': pack_data['includes'],
                    'excludes': 'Passagens aéreas, refeições não mencionadas, despesas pessoais',
                    'destination': destination,
                    'category': category,
                    'duration_days': pack_data['duration_days'],
                    'duration_nights': pack_data['duration_nights'],
                    'price': pack_data['price'],
                    'discount_percentage': pack_data['discount_percentage'],
                    'max_people': pack_data['max_people'],
                    'min_people': 1,
                    'available_from': available_from,
                    'available_until': available_until,
                    'featured': pack_data['featured'],
                    'status': pack_data['status'],
                }
                
                package, created = TourPackage.objects.get_or_create(
                    slug=pack_data['slug'],
                    defaults=package_data
                )
                if created:
                    self.stdout.write(f'🎒 Pacote criado: {package.title}')
            except Exception as e:
                self.stdout.write(f'Erro ao criar pacote {pack_data["title"]}: {e}')

    def create_testimonials(self):
        """Cria depoimentos de clientes"""
        testimonials_data = [
            {
                'name': 'Maria Silva Santos',
                'location': 'São Paulo - SP',
                'testimonial': 'Experiência incrível com a MONITOUR! O atendimento foi excepcional desde o primeiro contato. A viagem para Fernando de Noronha superou todas as expectativas. Guias atenciosos, hospedagem perfeita e roteiro bem planejado. Já estou planejando a próxima viagem com eles!',
                'rating': 5,
                'featured': True,
                'active': True
            },
            {
                'name': 'João Carlos Oliveira',
                'location': 'Rio de Janeiro - RJ',
                'testimonial': 'Paris foi um sonho realizado! A MONITOUR cuidou de cada detalhe da nossa lua de mel. O hotel era perfeito, os passeios organizados e o jantar na Torre Eiffel inesquecível. Obrigado por tornarem nossa viagem tão especial!',
                'rating': 5,
                'featured': True,
                'active': True
            },
            {
                'name': 'Ana Paula Costa',
                'location': 'Belo Horizonte - MG',
                'testimonial': 'Que viagem maravilhosa para o Rio! Mesmo sendo minha primeira vez, me senti segura e bem cuidada. Os guias conheciam cada cantinho da cidade e nos levaram para lugares incríveis. Recomendo de olhos fechados!',
                'rating': 5,
                'featured': True,
                'active': True
            },
            {
                'name': 'Roberto e Carla Mendes',
                'location': 'Porto Alegre - RS',
                'testimonial': 'As Maldivas foram ainda mais bonitas do que imaginávamos! O resort all-inclusive era perfeito e o atendimento da MONITOUR impecável. Valeu cada centavo investido nesse paraíso na terra!',
                'rating': 5,
                'featured': True,
                'active': True
            },
            {
                'name': 'Fernanda Rodrigues',
                'location': 'Brasília - DF',
                'testimonial': 'Gramado com a família foi perfeito! As crianças adoraram o Snowland e nós aproveitamos muito os passeios românticos. Hotel aconchegante e roteiro bem pensado para todos os gostos.',
                'rating': 4,
                'featured': False,
                'active': True
            },
        ]
        
        for i, test_data in enumerate(testimonials_data):
            testimonial, created = Testimonial.objects.get_or_create(
                name=test_data['name'],
                defaults=test_data
            )
            if created:
                self.stdout.write(f'💬 Depoimento criado: {testimonial.name}')

    def create_newsletter_subscribers(self):
        """Cria alguns assinantes da newsletter"""
        emails = [
            'cliente1@email.com',
            'cliente2@email.com',
            'cliente3@email.com',
            'viajante@email.com',
            'turista@email.com',
        ]
        
        for email in emails:
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults={
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 30)),
                    'active': True
                }
            )
            if created:
                self.stdout.write(f'📧 Newsletter: {newsletter.email}')

    def create_comments(self):
        """Cria comentários nos posts do blog"""
        posts = Post.objects.filter(status='published')
        
        comments_data = [
            {
                'name': 'Viajante Curioso',
                'email': 'viajante@email.com',
                'content': 'Excelente post! Essas dicas vão me ajudar muito na minha primeira viagem internacional. Obrigado por compartilhar essas informações valiosas!'
            },
            {
                'name': 'Maria Aventureira',
                'email': 'maria@email.com',
                'content': 'Já estive em Fernando de Noronha e posso confirmar: é realmente um paraíso! Suas dicas são precisas e muito úteis.'
            },
            {
                'name': 'Paulo Turista',
                'email': 'paulo@email.com',
                'content': 'Paris é mesmo incrível! Usei um roteiro parecido e aproveitei muito. A dica do Navigo realmente vale a pena!'
            }
        ]
        
        for post in posts:
            # Adicionar 1-2 comentários por post
            for i in range(random.randint(1, 2)):
                comment_data = random.choice(comments_data)
                
                comment, created = Comment.objects.get_or_create(
                    post=post,
                    name=comment_data['name'],
                    email=comment_data['email'],
                    defaults={
                        'content': comment_data['content'],
                        'approved': True,
                        'created_at': timezone.now() - timedelta(hours=random.randint(1, 48))
                    }
                )
                if created:
                    self.stdout.write(f'💬 Comentário: {post.title[:30]}...')

    def create_bookings_and_reviews(self):
        """Cria reservas e avaliações"""
        packages = TourPackage.objects.filter(status='active')
        
        bookings_data = [
            {
                'full_name': 'Carlos Eduardo Silva',
                'email': 'carlos@email.com',
                'phone': '(11) 99999-0001',
                'number_of_people': 2,
                'special_requests': 'Gostaria de mais informações sobre datas disponíveis para lua de mel.'
            },
            {
                'full_name': 'Patricia Santos',
                'email': 'patricia@email.com',
                'phone': '(21) 99999-0002',
                'number_of_people': 4,
                'special_requests': 'Viagem em família com duas crianças. Têm atividades adequadas?'
            },
        ]
        
        reviews_data = [
            {
                'customer_name': 'Marina Costa',
                'customer_email': 'marina@email.com',
                'rating': 5,
                'review_text': 'Viagem perfeita! Tudo muito bem organizado e com ótimo custo-benefício. Recomendo!'
            },
            {
                'customer_name': 'Ricardo Mendes',
                'customer_email': 'ricardo@email.com',
                'rating': 4,
                'review_text': 'Muito boa experiência. Apenas algumas sugestões de melhorias no roteiro, mas no geral excelente!'
            },
        ]
        
        for package in packages:
            # Criar algumas reservas
            for booking_data in random.sample(bookings_data, random.randint(1, 2)):
                booking, created = BookingInquiry.objects.get_or_create(
                    package=package,
                    email=booking_data['email'],
                    defaults={
                        **booking_data,
                        'preferred_date': timezone.now().date() + timedelta(days=random.randint(30, 90)),
                        'status': random.choice(['pending', 'confirmed', 'cancelled'])
                    }
                )
                if created:
                    self.stdout.write(f'📅 Reserva: {package.title[:30]}...')
            
            # Criar algumas avaliações
            for review_data in random.sample(reviews_data, random.randint(1, 2)):
                review, created = Review.objects.get_or_create(
                    package=package,
                    email=review_data['customer_email'],
                    defaults={
                        'name': review_data['customer_name'],
                        'rating': review_data['rating'],
                        'comment': review_data['review_text'],
                        'approved': True
                    }
                )
                if created:
                    self.stdout.write(f'⭐ Avaliação: {package.title[:30]}...')

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Todos os dados de exemplo foram criados com sucesso!')
        )
        self.stdout.write('🔗 Acesse o admin em: http://127.0.0.1:8000/admin/')
        self.stdout.write('👤 Login: admin / Senha: admin123')