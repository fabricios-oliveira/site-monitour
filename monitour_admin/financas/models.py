from django.db import models
from django.contrib.auth import get_user_model
import hashlib

class Categoria(models.Model):
    """Categorias para classificar transações (Ex: Alimentação, Transporte)."""
    nome = models.CharField(max_length=100, unique=True)
    # Permite criar subcategorias, como Alimentação > Restaurante
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategorias')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Transação"
        verbose_name_plural = "Categorias de Transações"
        ordering = ['nome']

class Conta(models.Model):
    """Representa uma conta bancária a ser monitorada."""
    nome = models.CharField(max_length=100, help_text="Ex: Conta Corrente Itaú")
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='contas_bancarias')
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Conta Bancária"
        verbose_name_plural = "Contas Bancárias"

class Transacao(models.Model):
    """Representa uma única transação (débito ou crédito) em uma conta."""
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='transacoes')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacoes')
    data = models.DateField()
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=12, decimal_places=2, help_text="Positivo para créditos, negativo para débitos")
    # Campo para evitar duplicidade na importação
    hash_transacao = models.CharField(max_length=64, unique=True, editable=False)

    def save(self, *args, **kwargs):
        # Gera o hash único para a transação antes de salvar
        unique_string = f"{self.data.strftime('%Y-%m-%d')}-{self.valor}-{self.descricao}"
        self.hash_transacao = hashlib.sha256(unique_string.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.data} | {self.descricao} | R$ {self.valor}"

    class Meta:
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        ordering = ['-data']

class RegraCategorizacao(models.Model):
    """Regras para categorizar transações automaticamente."""
    palavra_chave = models.CharField(max_length=100, help_text="Termo a ser buscado na descrição da transação (Ex: 'Uber')")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='regras_categorizacao')

    def __str__(self):
        return f"Se contém '{self.palavra_chave}', categorizar como '{self.categoria.nome}'"

    class Meta:
        verbose_name = "Regra de Categorização"
        verbose_name_plural = "Regras de Categorização"