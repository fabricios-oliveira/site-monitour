# 🌎 MONITOUR - Turismo & Viagens

![MONITOUR Logo](https://img.shields.io/badge/MONITOUR-Turismo%20%26%20Viagens-E34A8E?style=for-the-badge&logo=airplane&logoColor=white)

Site oficial da **MONITOUR Turismo & Viagens** - Sua agência especializada em experiências únicas e inesquecíveis.

## 📋 Sobre o Projeto

O site da MONITOUR foi desenvolvido em Django com foco em:

- ✈️ **Apresentação de pacotes turísticos** (fotos, descrições, preços e datas)
- 📝 **Blog para comunicação** e acolhimento de clientes
- 🛒 **E-commerce básico** para venda de pacotes
- 🎨 **Visual moderno e responsivo** inspirado no Canva
- 📱 **Design mobile-first** com TailwindCSS

## 🎨 Identidade Visual

### Paleta de Cores
- **Rosa Choque/Magenta**: `#E34A8E` - Destaques e botões de ação
- **Azul Marinho**: `#1D3787` - Títulos e textos principais  
- **Azul Claro**: `#F0F8FF` - Fundos suaves
- **Branco**: `#FFFFFF` - Fundo principal (estilo Canva)

### Tipografia
- **Font Principal**: Poppins (Google Fonts)
- **Pesos**: 300, 400, 500, 600, 700, 800

## 🚀 Tecnologias Utilizadas

### Backend
- **Django 4.2+** - Framework web Python
- **PostgreSQL** - Banco de dados (produção)
- **SQLite** - Banco de dados (desenvolvimento)
- **Pillow** - Processamento de imagens
- **python-decouple** - Gerenciamento de configurações

### Frontend
- **TailwindCSS** - Framework CSS utilitário
- **Font Awesome** - Ícones
- **JavaScript Vanilla** - Interações do cliente

### Deploy
- **Gunicorn** - Servidor WSGI
- **Nginx** - Servidor web e proxy reverso
- **WhiteNoise** - Servir arquivos estáticos
- **Let's Encrypt** - Certificados SSL

### Desenvolvimento
- **Django Debug Toolbar** - Debugging
- **Git** - Controle de versão
- **GitHub** - Repositório remoto

## 📁 Estrutura do Projeto

```
Site_MoniTour/
├── .github/
│   └── copilot-instructions.md
├── .venv/                      # Ambiente virtual
├── blog/                       # App do blog
│   ├── migrations/
│   ├── admin.py               # Admin do blog
│   ├── models.py              # Post, Category, Comment
│   ├── views.py               # Views do blog
│   └── urls.py                # URLs do blog
├── core/                       # App principal
│   ├── migrations/
│   ├── admin.py               # Admin geral
│   ├── models.py              # ContactMessage, Newsletter, etc
│   ├── views.py               # Home, About, Contact
│   └── urls.py                # URLs principais
├── packages/                   # App dos pacotes
│   ├── migrations/
│   ├── admin.py               # Admin dos pacotes
│   ├── models.py              # TourPackage, Booking, etc
│   ├── views.py               # Views dos pacotes
│   └── urls.py                # URLs dos pacotes
├── monitour_site/             # Configurações Django
│   ├── settings.py            # Configurações principais
│   ├── urls.py                # URLs do projeto
│   └── wsgi.py                # Configuração WSGI
├── templates/                  # Templates HTML
│   ├── partials/
│   │   ├── header.html        # Cabeçalho
│   │   └── footer.html        # Rodapé
│   ├── core/
│   │   └── home.html          # Página inicial
│   └── base.html              # Template base
├── static/                     # Arquivos estáticos
├── media/                      # Uploads de imagem
├── .env.example               # Exemplo de configurações
├── .gitignore                 # Arquivos ignorados pelo Git
├── requirements.txt           # Dependências Python
├── manage.py                  # Comando Django
├── gunicorn.conf.py          # Configuração Gunicorn
├── nginx.conf                # Configuração Nginx
├── deploy.sh                 # Script de deploy
└── README.md                 # Esta documentação
```

## ⚙️ Instalação e Configuração

### 1. Pré-requisitos

- Python 3.8+ 
- pip (gerenciador de pacotes Python)
- Git

### 2. Clone do Repositório

```bash
git clone https://github.com/seu-usuario/monitour-site.git
cd monitour-site
```

### 3. Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 4. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configuração do Ambiente

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar .env com suas configurações
# Gerar SECRET_KEY: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Banco de Dados

```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

### 7. Executar Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Acesse: `http://127.0.0.1:8000/`

## 🔧 Configuração de Produção

### 1. Variáveis de Ambiente (.env)

```bash
# Django Settings
SECRET_KEY=sua_chave_secreta_super_segura
DEBUG=False
ALLOWED_HOSTS=monitour.com.br,www.monitour.com.br

# Database (PostgreSQL)
USE_POSTGRESQL=True
DB_NAME=monitour_db
DB_USER=monitour_user
DB_PASSWORD=senha_super_segura
DB_HOST=localhost
DB_PORT=5432

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=contato@monitour.com.br
EMAIL_HOST_PASSWORD=senha_do_email
EMAIL_USE_TLS=True
```

### 2. PostgreSQL

```bash
# Instalar PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Criar banco e usuário
sudo -u postgres psql
CREATE DATABASE monitour_db;
CREATE USER monitour_user WITH PASSWORD 'senha_super_segura';
GRANT ALL PRIVILEGES ON DATABASE monitour_db TO monitour_user;
\q
```

### 3. Deploy no VPS

```bash
# Fazer upload dos arquivos para /var/www/monitour/
# Executar script de deploy
chmod +x deploy.sh
./deploy.sh
```

### 4. SSL (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot --nginx -d monitour.com.br -d www.monitour.com.br
```

## 📊 Funcionalidades Principais

### 🏠 Core (Aplicação Principal)
- **Home Page**: Hero section, estatísticas, destaques
- **Sobre Nós**: História da empresa, missão, valores
- **Contato**: Formulário de contato, informações
- **Newsletter**: Sistema de inscrição
- **Busca**: Busca global no site

### 📝 Blog
- **Posts**: Sistema completo de blog
- **Categorias**: Organização por categorias
- **Comentários**: Sistema de comentários com moderação
- **SEO**: Meta tags otimizadas

### ✈️ Pacotes Turísticos
- **Catálogo**: Lista de pacotes com filtros
- **Detalhes**: Página completa do pacote
- **Reservas**: Sistema de solicitação de reservas
- **Avaliações**: Sistema de reviews dos clientes
- **Categorias**: Tipos de pacotes (praia, montanha, etc)
- **Destinos**: Organização por destinos

### 🔧 Admin Dashboard
- **Gerenciamento de Conteúdo**: Posts, pacotes, categorias
- **Controle de Reservas**: Acompanhamento de solicitações
- **Newsletter**: Gestão de inscritos
- **Comentários e Reviews**: Moderação
- **Configurações**: Dados da empresa, redes sociais

## 🎯 SEO e Performance

### SEO Otimizado
- Meta tags dinâmicas
- URLs amigáveis (slugs)
- Open Graph tags
- Sitemap XML automático
- Robots.txt

### Performance
- Imagens otimizadas automaticamente
- Compressão Gzip
- Cache de arquivos estáticos
- CDN ready (WhiteNoise)
- Lazy loading

## 📱 Recursos Mobile

- Design 100% responsivo
- Menu mobile otimizado
- Botão WhatsApp flutuante
- Performance mobile otimizada
- Touch-friendly interfaces

## 🔐 Segurança

### Implementações
- HTTPS obrigatório (produção)
- Headers de segurança
- Proteção CSRF
- Sanitização de inputs
- Rate limiting pronto

### Backup
- Backup automático do banco
- Versionamento com Git
- Logs estruturados

## 📞 Suporte e Contato

### Contato da Agência
- **Site**: [www.monitour.com.br](https://www.monitour.com.br)
- **Email**: contato@monitour.com.br
- **WhatsApp**: +55 (11) 99999-9999

### Desenvolvimento
Para questões técnicas do site, abra uma [issue no GitHub](https://github.com/seu-usuario/monitour-site/issues).

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🤝 Contribuição

1. Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📈 Roadmap

### Próximas Funcionalidades
- [ ] Sistema de pagamento online (PIX/Cartão)
- [ ] Chat ao vivo
- [ ] App mobile (React Native)
- [ ] Sistema de fidelidade
- [ ] Integração com APIs de reservas
- [ ] Dashboard analytics
- [ ] Multi-idiomas (EN/ES)

### Melhorias Técnicas
- [ ] API REST (Django REST Framework)
- [ ] Testes automatizados
- [ ] CI/CD com GitHub Actions
- [ ] Docker containers
- [ ] Cache com Redis
- [ ] Monitoramento (Sentry)

---

## 🎉 Status do Projeto

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-4.2+-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0+-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

**Desenvolvido com ❤️ para a MONITOUR Turismo & Viagens**

---

### 📝 Changelog

#### v1.0.0 (2025-11-01)
- ✨ Lançamento inicial
- 🏠 Página inicial completa
- 📝 Sistema de blog
- ✈️ Catálogo de pacotes
- 🔧 Admin dashboard
- 📱 Design responsivo
- 🔐 Sistema de segurança
- 🚀 Scripts de deploy