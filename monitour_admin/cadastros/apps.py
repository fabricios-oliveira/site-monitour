from django.apps import AppConfig


class CadastrosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cadastros'
    verbose_name = 'Cadastros Gerais' # Este é o nome que aparecerá no admin

    def ready(self):
        import cadastros.admin # Garante que o admin seja carregado
        import cadastros.signals # Importa os sinais para registrá-los