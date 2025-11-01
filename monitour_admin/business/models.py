from django.db import models

class AcaoRapida(models.Model):
    """
    Representa um link de atalho (Ação Rápida) para ser exibido no dashboard.
    """
    label = models.CharField("Rótulo do Botão", max_length=100)
    url = models.CharField("URL ou Nome da Rota", max_length=200, help_text="Ex: /gerencia/passeios/passeio/add/ ou admin:passeios_passeio_add")
    ordem = models.PositiveIntegerField("Ordem", default=0, help_text="Números menores aparecem primeiro.")
    ativo = models.BooleanField("Ativo", default=True, help_text="Desmarque para ocultar este botão do dashboard.")

    class Meta:
        verbose_name = "Ação Rápida"
        verbose_name_plural = "Ações Rápidas"
        ordering = ['ordem']

    def __str__(self):
        return self.label