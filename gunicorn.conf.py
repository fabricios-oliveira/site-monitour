# Configuração do Gunicorn para MONITOUR

# Bind
bind = "0.0.0.0:8000"

# Workers
workers = 2
worker_class = "sync"
worker_connections = 1000

# Timeouts
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "monitour_gunicorn"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn/monitour.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (para produção com HTTPS)
# keyfile = "/etc/ssl/certs/monitour.key"
# certfile = "/etc/ssl/certs/monitour.crt"

# Performance
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Security
limit_request_line = 0
limit_request_fields = 100
limit_request_field_size = 8190