from django.contrib import admin
from .models import AcaoRapida

@admin.register(AcaoRapida)
class AcaoRapidaAdmin(admin.ModelAdmin):
    """
    Configura a interface de administração para o modelo AcaoRapida.
    """
    list_display = ('label', 'url', 'ordem', 'ativo')
    list_editable = ('ordem', 'ativo')
    list_filter = ('ativo',)