from django.db import models
from cadastros.models import Fornecedor, Cliente, TipoVeiculo
from django.contrib.auth import get_user_model # Para o campo responsável no GastoPasseio
from decimal import Decimal

UFS_BRASIL = [
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
    ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')
]

class PasseioManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('tipo_veiculo')

    def with_custo_total(self):
        """
        Anota cada passeio com o seu custo total previsto, calculado de forma eficiente.
        """
        from django.db.models import Sum, F, Case, When, Value, DecimalField

        # Custo de transporte: usa a cotação aceita ou o custo base do veículo
        custo_transporte = Case(
            When(cotacoes__status='aceita', cotacoes__tipo_servico='transporte', then=F('cotacoes__valor_cotado')),
            default=F('tipo_veiculo__custo_base_transporte'),
            output_field=DecimalField()
        )

        return self.annotate(
            _custo_cotacoes_outros=Sum('cotacoes__valor_cotado', filter=models.Q(cotacoes__status='aceita') & ~models.Q(cotacoes__tipo_servico='transporte'), default=Value(0)),
            _custo_gastos=Sum('gastos__valor', default=Value(0)),
            _custo_transporte=Sum(custo_transporte, filter=models.Q(cotacoes__tipo_servico='transporte'), default=F('tipo_veiculo__custo_base_transporte')),
            _custo_pacotes=Sum('pacotes__preco', default=Value(0)),
            _custo_total_previsto=F('_custo_cotacoes_outros') + F('_custo_gastos') + F('_custo_transporte') + F('_custo_pacotes')
        )

class Passeio(models.Model):
    """
    Representa um passeio ou viagem oferecido pela agência.
    """
    STATUS_PASSEIO = [
        ('agendado', 'Agendado'),
        ('confirmado', 'Confirmado'),
        ('realizado', 'Realizado'),
        ('cancelado', 'Cancelado'),
    ]

    titulo = models.CharField(max_length=200, help_text="Título principal do passeio")
    descricao = models.TextField(blank=True, help_text="Descrição detalhada do que o passeio inclui")
    cidade_origem = models.CharField("Origem", max_length=100, default="A Definir")
    uf_origem = models.CharField("UF", max_length=2, choices=UFS_BRASIL, default="SP")
    cidade_destino = models.CharField("Destino", max_length=100, default="A Definir")
    uf_destino = models.CharField("UF", max_length=2, choices=UFS_BRASIL, default="SP")
    data_ida = models.DateTimeField(help_text="Data e hora de partida")
    data_volta = models.DateTimeField(help_text="Data e hora de retorno")
    status = models.CharField(max_length=20, choices=STATUS_PASSEIO, default='agendado', help_text="Status atual do passeio")

    # --- AQUI ESTÁ A CONEXÃO ---
    fornecedor_transporte = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        related_name="passeios_transporte",
        help_text="Empresa de ônibus/transporte responsável.",
        limit_choices_to={'tipo': 'transporte'}, # Filtra para mostrar apenas fornecedores de transporte
    )

    fornecedor_hospedagem = models.ForeignKey(
        Fornecedor,
        on_delete=models.PROTECT,
        related_name="passeios_hospedagem",
        help_text="Hotel ou pousada da hospedagem (se houver).",
        limit_choices_to={'tipo': 'hospedagem'}, # Filtra para mostrar apenas fornecedores de hospedagem
        blank=True, null=True # Permite que este campo seja opcional
    )

    # --- NOVA ASSOCIAÇÃO DE VEÍCULO ---
    tipo_veiculo = models.ForeignKey(
        TipoVeiculo,
        on_delete=models.PROTECT,
        help_text="Selecione o modelo de veículo principal para este passeio.",
        null=True, blank=True # Opcional para permitir salvar passeios sem veículo definido
    )
    margem_lucro_desejada = models.DecimalField(
        "Margem de Lucro Desejada (%)",
        max_digits=5,
        decimal_places=2,
        default=30.00,
        help_text="Percentual de lucro desejado sobre o preço de venda final."
    )
    margem_lucro_promocional = models.DecimalField(
        "Margem de Lucro Promocional (%)",
        max_digits=5,
        decimal_places=2,
        default=10.00,
        help_text="Margem de lucro mínima para vendas promocionais."
    )
    lotacao_minima_desejada = models.PositiveIntegerField(
        "Lotação Mínima Desejada",
        default=0,
        help_text="Número mínimo de passageiros desejado para o passeio. Use 0 para desativar."
    )
    alerta_equilibrio_enviado = models.BooleanField(
        "Alerta de Ponto de Equilíbrio Enviado",
        default=False,
        help_text="Marca se o e-mail de alerta de ponto de equilíbrio já foi enviado."
    )

    objects = PasseioManager()

    def __str__(self):
        return self.titulo

    @property
    def origem_formatada(self):
        return f"{self.cidade_origem}/{self.uf_origem}"

    @property
    def destino_formatado(self):
        return f"{self.cidade_destino}/{self.uf_destino}"

    @property
    def custo_total_previsto(self):
        """Retorna o custo total previsto, idealmente pré-calculado via anotação."""
        if hasattr(self, '_custo_total_previsto'):
            return self._custo_total_previsto
        # Fallback para cálculo manual (menos eficiente)
        # Este bloco pode ser removido se garantirmos que a anotação é sempre usada.
        return self._calculate_custo_total_manual()
    
    def _calculate_custo_total_manual(self):
        """Calcula manualmente o custo total quando a anotação não está disponível."""
        from decimal import Decimal
        custo = Decimal('0.00')
        
        # Soma custos de cotações aceitas
        if self.cotacoes.exists():
            custo += self.cotacoes.filter(status='aceita').aggregate(
                total=models.Sum('valor_cotado')
            )['total'] or Decimal('0.00')
        
        # Soma custos de gastos
        if self.gastos.exists():
            custo += self.gastos.aggregate(
                total=models.Sum('valor')
            )['total'] or Decimal('0.00')
        
        return custo

    class Meta:
        verbose_name = "Passeio"
        verbose_name_plural = "Passeios"

class Pacote(models.Model):
    """
    Representa uma opção de pacote (com preço) para um determinado passeio.
    """
    passeio = models.ForeignKey(Passeio, on_delete=models.CASCADE, related_name="pacotes")
    titulo = models.CharField(max_length=100, help_text="Ex: Somente Passagem, Pacote Completo")
    preco = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preço de venda deste pacote")

    def __str__(self):
        return f"{self.passeio.titulo} - {self.titulo} (R$ {self.preco})"

    class Meta:
        verbose_name = "Pacote"
        verbose_name_plural = "Pacotes"

class ItemPacote(models.Model):
    """
    Representa um item individual que compõe um pacote (ex: 'Transporte', 'Almoço').
    """
    pacote = models.ForeignKey(Pacote, on_delete=models.CASCADE, related_name="itens")
    descricao = models.CharField(max_length=200, help_text="Descrição do item incluído. Ex: Transporte ida e volta")

    def __str__(self):
        return self.descricao

class Inscricao(models.Model):
    """
    Representa a inscrição (venda) de um cliente em um pacote de passeio.
    """
    STATUS_PAGAMENTO = [
        ('aguardando', 'Aguardando Pagamento'),
        ('parcial', 'Pagamento Parcial'),
        ('pago', 'Pago Integralmente'),
        ('cancelado', 'Cancelado'),
    ]
    STATUS_INSCRICAO = [
        ('confirmada', 'Confirmada'),
        ('lista_espera', 'Lista de Espera'),
        ('cancelada_cliente', 'Cancelada pelo Cliente'),
        ('cancelada_agencia', 'Cancelada pela Agência'),
    ]

    pacote = models.ForeignKey(Pacote, on_delete=models.PROTECT, related_name="inscricoes")
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="inscricoes")
    data_inscricao = models.DateTimeField(auto_now_add=True)
    status_pagamento = models.CharField(max_length=20, choices=STATUS_PAGAMENTO, default='aguardando')
    status_inscricao = models.CharField("Status da Inscrição", max_length=20, choices=STATUS_INSCRICAO, default='confirmada')
    observacoes = models.TextField(blank=True, help_text="Anotações específicas sobre esta inscrição")
    voucher = models.CharField(max_length=10, unique=True, blank=True, null=True, help_text="Código único da inscrição (gerado automaticamente)")


    def __str__(self):
        return f"Inscrição de {self.cliente.nome} no pacote {self.pacote.titulo}"

    class Meta:
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"
        # Garante que um cliente não pode se inscrever duas vezes no mesmo pacote
        unique_together = ('pacote', 'cliente')

    @property
    def valor_pago(self):
        """Calcula o valor total pago para esta inscrição."""
        # A anotação 'total_pago' é adicionada no queryset do admin para eficiência.
        # Se o objeto não tiver essa anotação, calculamos aqui.
        if hasattr(self, 'total_pago') and self.total_pago is not None:
            return self.total_pago
        return self.pagamentos.aggregate(total=models.Sum('valor'))['total'] or Decimal('0.00')

    @property
    def saldo_devedor(self):
        """Calcula o saldo devedor com base no preço do pacote e no valor pago."""
        return self.pacote.preco - self.valor_pago

class Pagamento(models.Model):
    """
    Representa um pagamento individual feito para uma inscrição.
    """
    METODO_PAGAMENTO = [
        ('pix', 'PIX'),
        ('dinheiro', 'Dinheiro'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
        ('transferencia', 'Transferência Bancária'),
        ('outro', 'Outro'),
    ]

    inscricao = models.ForeignKey(Inscricao, on_delete=models.CASCADE, related_name="pagamentos")
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_pagamento = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=50, choices=METODO_PAGAMENTO, blank=True, help_text="Método utilizado para o pagamento")

    def __str__(self):
        return f"Pagamento de R$ {self.valor} para {self.inscricao.cliente.nome}"

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

class VeiculoPasseio(models.Model):
    """
    Associa um veículo específico a um passeio. Um passeio pode ter vários veículos.
    """
    passeio = models.ForeignKey(Passeio, on_delete=models.CASCADE, related_name="veiculos")
    tipo_veiculo = models.ForeignKey(TipoVeiculo, on_delete=models.PROTECT)
    identificacao = models.CharField(max_length=100, help_text="Ex: Ônibus 1, Van de Apoio")

    def __str__(self):
        return f"{self.identificacao} ({self.tipo_veiculo.nome}) - {self.passeio.titulo}"

    class Meta:
        verbose_name = "Veículo do Passeio"
        verbose_name_plural = "Veículos do Passeio"

class Assento(models.Model):
    """
    Representa um assento específico em um veículo de um passeio,
    e o cliente associado a ele.
    """
    veiculo_passeio = models.ForeignKey(VeiculoPasseio, on_delete=models.CASCADE, related_name="assentos")
    numero = models.PositiveIntegerField()
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="assentos_reservados")

    def __str__(self):
        return f"Assento {self.numero} - {self.veiculo_passeio.identificacao}"

    class Meta:
        # Garante que um assento seja único por veículo e que um cliente só ocupe um assento por veículo.
        unique_together = [['veiculo_passeio', 'numero'], ['veiculo_passeio', 'cliente']]
        verbose_name = "Assento"
        verbose_name_plural = "Assentos"


class Cotacao(models.Model):
    """
    Representa uma cotação de serviço de um fornecedor para um passeio específico.
    """
    STATUS_COTACAO = [
        ('pendente', 'Pendente'),
        ('aceita', 'Aceita'),
        ('rejeitada', 'Rejeitada'),
        ('negociando', 'Negociando'),
    ]
    TIPO_SERVICO_COTADO = [
        ('transporte', 'Transporte'),
        ('hospedagem', 'Hospedagem'),
        ('alimentacao', 'Alimentação'),
        ('guia', 'Guia Turístico'),
        ('seguro', 'Seguro Viagem'),
        ('taxas', 'Taxas/Permissões'),
        ('outro', 'Outro'),
    ]

    passeio = models.ForeignKey(Passeio, on_delete=models.CASCADE, related_name="cotacoes")
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name="cotacoes_recebidas")
    tipo_servico = models.CharField(max_length=50, choices=TIPO_SERVICO_COTADO, help_text="Tipo de serviço cotado")
    valor_cotado = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor proposto pelo fornecedor")
    data_cotacao = models.DateTimeField(auto_now_add=True, help_text="Data em que a cotação foi registrada")
    observacoes = models.TextField(blank=True, help_text="Detalhes adicionais da cotação")
    status = models.CharField(max_length=20, choices=STATUS_COTACAO, default='pendente', help_text="Status atual da cotação")
    data_vencimento_pagamento = models.DateField(null=True, blank=True, help_text="Data limite para o pagamento final")
    fornecedor_selecionado = models.BooleanField(default=False, help_text="Marque se esta cotação foi a escolhida para o serviço")

    def __str__(self):
        return f"Cotação de {self.fornecedor.nome_fantasia} para {self.get_tipo_servico_display()} no {self.passeio.titulo}"

    @property
    def valor_pago(self):
        """Calcula o valor total pago para esta cotação."""
        if hasattr(self, 'total_pago_fornecedor') and self.total_pago_fornecedor is not None:
            return self.total_pago_fornecedor
        return self.pagamentos_fornecedor.aggregate(total=models.Sum('valor'))['total'] or Decimal('0.00')

    @property
    def saldo_a_pagar(self):
        """Calcula o saldo devedor com base no valor cotado e no valor pago."""
        return self.valor_cotado - self.valor_pago

    class Meta:
        verbose_name = "Cotação"
        verbose_name_plural = "Cotações"
        ordering = ['-data_cotacao']


class GastoPasseio(models.Model):
    """
    Representa um gasto operacional interno associado a um passeio.
    """
    TIPO_GASTO_CHOICES = [
        ('alimentacao', 'Alimentação (Lanches, Refeições)'),
        ('combustivel', 'Combustível'),
        ('taxas', 'Taxas/Pedágios'),
        ('material', 'Material de Apoio'),
        ('imprevisto', 'Imprevisto'),
        ('outro', 'Outro'),
    ]

    passeio = models.ForeignKey(Passeio, on_delete=models.CASCADE, related_name="gastos")
    descricao = models.CharField(max_length=255, help_text="Descrição detalhada do gasto")
    valor = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor do gasto")
    data_gasto = models.DateTimeField(auto_now_add=True, help_text="Data em que o gasto foi registrado")
    tipo_gasto = models.CharField(max_length=50, choices=TIPO_GASTO_CHOICES, help_text="Categoria do gasto")
    responsavel = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuário responsável pelo gasto")

    def __str__(self):
        return f"Gasto de R$ {self.valor} ({self.get_tipo_gasto_display()}) para {self.passeio.titulo}"

    class Meta:
        verbose_name = "Gasto do Passeio"
        verbose_name_plural = "Gastos do Passeio"
        ordering = ['-data_gasto']


class PagamentoFornecedor(models.Model):
    """
    Representa um pagamento individual feito a um fornecedor para uma cotação aceita.
    """
    METODO_PAGAMENTO = [('pix', 'PIX'), ('transferencia', 'Transferência Bancária'), ('boleto', 'Boleto'), ('outro', 'Outro')]

    cotacao = models.ForeignKey(Cotacao, on_delete=models.CASCADE, related_name="pagamentos_fornecedor", help_text="Cotação à qual este pagamento se refere")
    valor = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor pago")
    data_pagamento = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=50, choices=METODO_PAGAMENTO, default='transferencia')
    observacoes = models.TextField(blank=True, help_text="Anotações ou informações do comprovante")

    def __str__(self):
        return f"Pagamento de R$ {self.valor} para {self.cotacao.fornecedor.nome_fantasia}"


class PaymentGatewayTransaction(models.Model):
    """
    Rastreia transações processadas por gateways de pagamento (ex: Mercado Pago).
    Uma transação pode estar ligada a um ou mais pagamentos.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
        ('cancelado', 'Cancelado'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    GATEWAY_CHOICES = [
        ('mercadopago', 'Mercado Pago'),
        ('stripe', 'Stripe'),
    ]
    
    # Identificação da transação no gateway
    gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES, default='mercadopago')
    gateway_id = models.CharField(max_length=100, unique=True, help_text="ID único da transação no gateway")
    
    # Referência ao pagamento local
    pagamento = models.OneToOneField(
        Pagamento,
        on_delete=models.CASCADE,
        related_name='gateway_transaction',
        null=True,
        blank=True
    )
    
    # Status e dados da transação
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = models.CharField(
        max_length=50,
        choices=[
            ('cartao_credito', 'Cartão de Crédito'),
            ('cartao_debito', 'Cartão de Débito'),
            ('pix', 'PIX'),
            ('boleto', 'Boleto'),
        ]
    )
    
    # Detalhes específicos (salvo como JSON se necessário)
    parcelas = models.PositiveIntegerField(default=1)
    
    # Rastreamento de webhook
    webhook_confirmado = models.BooleanField(default=False)
    
    # Datas
    criada_em = models.DateTimeField(auto_now_add=True)
    confirmada_em = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.gateway.upper()} - {self.gateway_id} ({self.status})"
    
    class Meta:
        verbose_name = "Transação de Gateway"
        verbose_name_plural = "Transações de Gateway"
        ordering = ['-criada_em']