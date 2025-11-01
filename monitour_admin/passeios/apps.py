from django.apps import AppConfig

class PasseiosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'passeios'
    verbose_name = 'Gerenciamento de Passeios' # Adiciona um nome amigável

    def ready(self):
        import passeios.signals # Importa os sinais para que sejam registrados
        import passeios.admin