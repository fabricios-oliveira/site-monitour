from django.db import models
from django.db.models import Count, Sum
from django.db.models import Count, Sum
from phonenumber_field.modelfields import PhoneNumberField
import secrets
import string


def limpar_cpf(cpf):
    """
    Remove formatação do CPF (pontos e hífens).
    Aceita: 123.456.789-00 ou 12345678900
    Retorna: 12345678900
    """
    if not cpf:
        return cpf
    return ''.join(filter(str.isdigit, str(cpf)))


def gerar_matricula_aleatoria():
    """
    Gera um número aleatório de matrícula com 6 dígitos.
    Exemplo: 847293, 123456, etc.
    """
    return ''.join(secrets.choice(string.digits) for _ in range(6))


class MatriculaCliente(models.Model):
    """
    Cria um vínculo permanente entre um CPF e uma matrícula única.
    A matrícula é um número aleatório de 6 dígitos para privacidade
    (não mostra quantos clientes estão cadastrados).
    """
    # ID customizado: número aleatório de 6 dígitos
    id = models.CharField(
        primary_key=True,
        max_length=6,
        default=gerar_matricula_aleatoria,
        editable=False,
        help_text="Número de matrícula aleatório (6 dígitos)"
    )
    cpf = models.CharField(max_length=11, unique=True, help_text="CPF do cliente (apenas números)")

    def __str__(self):
        # O ID é a própria matrícula
        return f"{self.id}"
    
    class Meta:
        verbose_name = "Matrícula Cliente"
        verbose_name_plural = "Matrículas Cliente"

class Cliente(models.Model):
    """
    Representa um cliente da agência de turismo com dados pessoais completos.
    """
    # Campos de Identificação
    nome = models.CharField(max_length=100, help_text="Nome completo do cliente")
    cpf = models.CharField(
        max_length=14, 
        unique=True, 
        help_text="CPF (aceita formatação: 123.456.789-00 ou 12345678900)"
    )
    rg = models.CharField("RG", max_length=20, blank=True, help_text="Número do RG/CNH")
    
    # Campos Pessoais
    data_nascimento = models.DateField(blank=True, null=True, help_text="Data de nascimento do cliente")
    genero = models.CharField(
        max_length=10,
        choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')],
        blank=True,
        help_text="Gênero do cliente"
    )
    nacionalidade = models.CharField(max_length=50, default="Brasileira", help_text="Nacionalidade do cliente")
    estado_civil = models.CharField(
        max_length=20,
        choices=[
            ('solteiro', 'Solteiro(a)'),
            ('casado', 'Casado(a)'),
            ('divorciado', 'Divorciado(a)'),
            ('viuvo', 'Viúvo(a)'),
            ('uniao_estavel', 'União Estável'),
        ],
        blank=True,
        help_text="Estado civil do cliente"
    )
    profissao = models.CharField(max_length=100, blank=True, help_text="Profissão do cliente")
    
    # Contato
    email = models.EmailField(max_length=254, unique=True, blank=True, null=True, help_text="E-mail do cliente")
    telefone = PhoneNumberField(region="BR", blank=True, help_text="Número de telefone com DDD")
    telefone_adicional = PhoneNumberField(region="BR", blank=True, help_text="Número de telefone adicional (para contato emergencial)")
    
    # Endereço
    endereco = models.CharField(max_length=200, blank=True, help_text="Rua e número do endereço")
    numero = models.CharField(max_length=10, blank=True, help_text="Número do imóvel")
    complemento = models.CharField(max_length=100, blank=True, help_text="Complemento (apto, bloco, etc)")
    bairro = models.CharField(max_length=100, blank=True, help_text="Bairro")
    cep = models.CharField("CEP", max_length=9, blank=True, help_text="CEP no formato XXXXX-XXX")
    cidade = models.CharField(max_length=100, blank=True, help_text="Cidade")
    estado = models.CharField("UF", max_length=2, blank=True, help_text="Estado (UF)")
    ponto_referencia = models.CharField(max_length=200, blank=True, help_text="Ponto de referência do endereço")
    
    # Matrícula (gerada automaticamente)
    matricula = models.OneToOneField(
        MatriculaCliente,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="Matrícula",
        help_text="Número de matrícula único (gerado automaticamente)"
    )
    
    # Dados Adicionais
    observacoes = models.TextField(blank=True, help_text="Anotações internas sobre o cliente (preferências, restrições, etc.)")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Retorna o nome do cliente como representação em string do objeto.
        """
        return self.nome

    def clean(self):
        """
        Valida e limpa os dados antes de salvar.
        Remove formatação do CPF, mantendo apenas dígitos.
        """
        # Limpar CPF: aceita 123.456.789-00 e converte para 12345678900
        if self.cpf:
            self.cpf = limpar_cpf(self.cpf)
        super().clean()

    def save(self, *args, **kwargs):
        """
        Sobrescreve o save para chamar clean() automaticamente.
        """
        self.clean()
        super().save(*args, **kwargs)

    @property
    def endereco_completo(self):
        """Retorna o endereço completo formatado."""
        partes = [self.endereco]
        if self.numero:
            partes.append(self.numero)
        if self.complemento:
            partes.append(f"({self.complemento})")
        if self.bairro:
            partes.append(self.bairro)
        if self.cidade:
            partes.append(self.cidade)
        if self.estado:
            partes.append(self.estado)
        if self.cep:
            partes.append(self.cep)
        return ", ".join(filter(None, partes))

    @property
    def matricula_numero(self):
        """Retorna o número da matrícula ou 'N/A'."""
        return self.matricula.id if self.matricula else "N/A"

    @property
    def nivel_fidelidade(self):
        """Define um nível de fidelidade com base no número de viagens."""
        # Para ser eficiente, este método deve ser usado em objetos que já foram anotados com 'num_viagens'
        viagens = getattr(self, '_total_viagens', 0)
        if viagens >= 10:
            return "💎 Diamante"
        if viagens >= 5:
            return "🥇 Ouro"
        if viagens >= 2:
            return "🥈 Prata"
        return "🥉 Bronze"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class Fornecedor(models.Model):
    """
    Representa um fornecedor de serviços, como empresas de ônibus, hotéis, etc.
    """
    TIPO_CHOICES = [
        ('transporte', 'Transporte'),
        ('hospedagem', 'Hospedagem'),
        ('atracao', 'Atração'),
        ('restaurante', 'Restaurante'),
        ('outro', 'Outro'),
    ]

    nome_fantasia = models.CharField(max_length=100, help_text="Nome comercial do fornecedor")
    razao_social = models.CharField(max_length=100, blank=True, help_text="Razão Social (se aplicável)")
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True, help_text="CNPJ no formato XX.XXX.XXX/XXXX-XX")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, help_text="Tipo de serviço prestado")
    observacoes = models.TextField(blank=True, help_text="Anotações gerais sobre o fornecedor")

    def __str__(self):
        return f"{self.nome_fantasia} ({self.get_tipo_display()})"

    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

class ContatoFornecedor(models.Model):
    """
    Representa um contato individual dentro de uma empresa fornecedora.
    """
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name="contatos")
    nome = models.CharField(max_length=100, help_text="Nome do contato")
    cargo = models.CharField(max_length=100, blank=True, help_text="Ex: Vendedor, Motorista, Gerente")
    email = models.EmailField(max_length=254, blank=True)
    telefone = PhoneNumberField(region="BR", blank=True, help_text="Telefone principal do contato")
    observacoes = models.TextField(blank=True, help_text="Anotações sobre este contato específico")

    def __str__(self):
        return f"{self.nome} ({self.fornecedor.nome_fantasia})"

    class Meta:
        verbose_name = "Contato do Fornecedor"
        verbose_name_plural = "Contatos do Fornecedor"

class ContaBancariaFornecedor(models.Model):
    """
    Armazena os dados bancários de um fornecedor para pagamentos.
    """
    TIPO_CONTA_CHOICES = [('corrente', 'Conta Corrente'), ('poupanca', 'Conta Poupança')]

    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name="contas_bancarias")
    banco = models.CharField(max_length=100, help_text="Nome ou código do banco (Ex: Itaú, 341)")
    agencia = models.CharField(max_length=20, help_text="Número da agência")
    conta = models.CharField(max_length=30, help_text="Número da conta com dígito")
    tipo_conta = models.CharField(max_length=10, choices=TIPO_CONTA_CHOICES, default='corrente')
    titular = models.CharField(max_length=150, help_text="Nome completo do titular da conta")
    cpf_cnpj_titular = models.CharField("CPF/CNPJ do Titular", max_length=18, blank=True)
    chave_pix = models.CharField("Chave PIX", max_length=100, blank=True)

    def __str__(self):
        return f"Conta de {self.fornecedor.nome_fantasia} - Banco: {self.banco}"

class TipoVeiculo(models.Model):
    """
    Define um modelo de veículo, como 'Ônibus Leito' ou 'Van'.
    O administrador define o nome, a quantidade de fileiras e colunas.
    """
    nome = models.CharField(max_length=100, unique=True, help_text="Ex: Ônibus Leito 46 Lugares")
    fileiras = models.PositiveIntegerField(default=12, help_text="Número de fileiras de assentos")
    capacidade = models.PositiveIntegerField(default=48, help_text="Capacidade total de passageiros")
    layout_colunas = models.CharField(
        max_length=10,
        default='2-2',
        help_text="Layout das colunas, separado por hífen (ex: '2-2', '2-1')."
    )
    custo_base_transporte = models.DecimalField(
        "Custo Base de Transporte (R$)",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Custo estimado para o transporte deste tipo de veículo, usado se não houver cotação aceita."
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Modelo de Veículo"
        verbose_name_plural = "Modelos de Veículos"
