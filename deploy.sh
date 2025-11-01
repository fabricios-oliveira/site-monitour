#!/bin/bash
# Script de Deploy para MONITOUR no VPS Hostinger

echo "🚀 Iniciando deploy do MONITOUR..."

# Variáveis
PROJECT_DIR="/var/www/monitour"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/seu-usuario/monitour-site.git"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Verificar se é root
if [[ $EUID -eq 0 ]]; then
    error "Este script não deve ser executado como root"
fi

# 1. Backup do banco de dados (se existir)
if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
    log "Fazendo backup do banco de dados..."
    cp "$PROJECT_DIR/db.sqlite3" "$PROJECT_DIR/db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 2. Parar serviços
log "Parando serviços..."
sudo systemctl stop gunicorn || warning "Gunicorn não estava rodando"
sudo systemctl stop nginx || warning "Nginx não estava rodando"

# 3. Atualizar código
log "Atualizando código do repositório..."
cd $PROJECT_DIR

# Se é a primeira vez, fazer clone
if [ ! -d ".git" ]; then
    info "Primeira instalação - clonando repositório..."
    cd /var/www/
    sudo git clone $REPO_URL monitour
    sudo chown -R $USER:www-data monitour
    cd monitour
else
    # Atualizar repositório existente
    git fetch origin
    git reset --hard origin/main
fi

# 4. Configurar virtual environment
log "Configurando ambiente virtual..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

source $VENV_DIR/bin/activate

# 5. Instalar dependências
log "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Coletar arquivos estáticos
log "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 7. Executar migrações
log "Executando migrações..."
python manage.py migrate

# 8. Configurar permissões
log "Configurando permissões..."
sudo chown -R $USER:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR
sudo chmod -R 775 $PROJECT_DIR/media/
sudo chmod -R 775 $PROJECT_DIR/staticfiles/

# 9. Configurar Gunicorn service (se não existir)
if [ ! -f "/etc/systemd/system/gunicorn.service" ]; then
    log "Criando serviço do Gunicorn..."
    sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=Gunicorn instance to serve MONITOUR
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn --config gunicorn.conf.py monitour_site.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable gunicorn
fi

# 10. Configurar Nginx (se não existir)
if [ ! -f "/etc/nginx/sites-available/monitour" ]; then
    log "Configurando Nginx..."
    sudo cp nginx.conf /etc/nginx/sites-available/monitour
    sudo ln -sf /etc/nginx/sites-available/monitour /etc/nginx/sites-enabled/
    sudo nginx -t || error "Erro na configuração do Nginx"
fi

# 11. Certificado SSL (Let's Encrypt)
if [ ! -f "/etc/letsencrypt/live/monitour.com.br/fullchain.pem" ]; then
    warning "Certificado SSL não encontrado. Execute:"
    warning "sudo certbot --nginx -d monitour.com.br -d www.monitour.com.br"
fi

# 12. Iniciar serviços
log "Iniciando serviços..."
sudo systemctl start gunicorn
sudo systemctl start nginx

# 13. Verificar status
log "Verificando status dos serviços..."
if sudo systemctl is-active --quiet gunicorn; then
    log "✅ Gunicorn está rodando"
else
    error "❌ Gunicorn falhou ao iniciar"
fi

if sudo systemctl is-active --quiet nginx; then
    log "✅ Nginx está rodando"
else
    error "❌ Nginx falhou ao iniciar"
fi

# 14. Teste de conectividade
log "Testando conectividade..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200\|302"; then
    log "✅ Aplicação respondendo localmente"
else
    warning "⚠️ Aplicação pode não estar respondendo localmente"
fi

log "🎉 Deploy concluído com sucesso!"
info "Site disponível em: https://monitour.com.br"
info "Admin: https://monitour.com.br/admin/"
info ""
info "Comandos úteis:"
info "- Ver logs: sudo journalctl -u gunicorn -f"
info "- Reiniciar: sudo systemctl restart gunicorn"
info "- Status: sudo systemctl status gunicorn"