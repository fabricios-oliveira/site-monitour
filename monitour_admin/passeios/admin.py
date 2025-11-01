from django.contrib import admin
from django.db import models
from .models import Passeio, Pacote, Inscricao, Pagamento, VeiculoPasseio, Cotacao, GastoPasseio, PagamentoFornecedor, ItemPacote, PaymentGatewayTransaction
from django.contrib import messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

class PacoteInline(admin.TabularInline):
    model = Pacote
    extra = 1 # Mostra 1 formulário extra para adicionar pacote

class PagamentoInline(admin.TabularInline):
    model = Pagamento
    extra = 1

class VeiculoPasseioInline(admin.TabularInline):
    model = VeiculoPasseio
    extra = 1
    autocomplete_fields = ['tipo_veiculo']

class PagamentoFornecedorInline(admin.TabularInline):
    model = PagamentoFornecedor
    extra = 1

class CotacaoInline(admin.TabularInline):
    model = Cotacao
    extra = 1
    autocomplete_fields = ['fornecedor']
    fields = ('fornecedor', 'tipo_servico', 'valor_cotado', 'status', 'fornecedor_selecionado')

class GastoPasseioInline(admin.TabularInline):
    model = GastoPasseio
    extra = 1
    fields = ('descricao', 'tipo_gasto', 'valor', 'responsavel')

@admin.register(Passeio)
class PasseioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'get_destino_formatado', 'data_ida', 'status', 'ver_inscricoes_link', 'mapa_de_assentos_link', 'gerar_relatorio_link', 'resumo_financeiro_link', 'relatorio_cotacoes_link')
    list_filter = ('status', 'cidade_destino', 'data_ida') # Corrigido para usar o campo que existe
    search_fields = ('titulo', 'cidade_destino', 'cidade_origem')
    autocomplete_fields = ['tipo_veiculo', 'fornecedor_transporte', 'fornecedor_hospedagem']

    # Organiza os campos em seções mais limpas e lógicas
    fieldsets = (
        ('Informações Principais', {
            'fields': ('titulo', ('cidade_origem', 'uf_origem'), ('cidade_destino', 'uf_destino'), 'status', 'tipo_veiculo')
        }),
        ('Datas e Horários', {
            'fields': (('data_ida', 'data_volta'),)
        }),
        ('Planejamento Financeiro', {
            'fields': ('margem_lucro_desejada', 'margem_lucro_promocional', 'lotacao_minima_desejada')
        }),
        ('Detalhes Adicionais', {
            'classes': ('collapse',), # Esta seção começará fechada
            'fields': ('descricao',),
        }),
        ('Parceiros de Serviço', {
            'classes': ('collapse',), # Esta seção também começará fechada
            'fields': ('fornecedor_transporte', 'fornecedor_hospedagem'),
        }),
    )

    def get_inlines(self, request, obj=None):
        # Mostra a seção de Pacotes apenas se o Passeio já existir
        return [PacoteInline, VeiculoPasseioInline, CotacaoInline, GastoPasseioInline] if obj else []

    def mapa_de_assentos_link(self, obj):
        links = []
        # Para cada veículo associado a este passeio, cria um link para o mapa
        for veiculo in obj.veiculos.all():
            url = reverse('passeios:mapa_assentos', args=[veiculo.pk])
            links.append(f'<a href="{url}" class="button">{veiculo.identificacao}</a>')
        if not links:
            return "Nenhum veículo"
        return format_html('<br>'.join(links))
    mapa_de_assentos_link.short_description = "Mapas de Assentos"

    def gerar_relatorio_link(self, obj):
        url = reverse('passeios:relatorio_passageiros', args=[obj.pk])
        return format_html('<a class="button" href="{}">Gerar Relatório</a>', url)
    gerar_relatorio_link.short_description = "Relatório de Passageiros"

    def resumo_financeiro_link(self, obj):
        url = reverse('passeios:relatorio_financeiro', args=[obj.pk])
        return format_html('<a href="{}">Ver Resumo</a>', url)
    resumo_financeiro_link.short_description = "Resumo Financeiro"

    def ver_inscricoes_link(self, obj):
        # Conta o número de inscrições para este passeio
        count = Inscricao.objects.filter(pacote__passeio=obj).count()
        # Gera a URL para a lista de inscrições, já filtrada por este passeio
        url = reverse('admin:passeios_inscricao_changelist') + f'?pacote__passeio__id__exact={obj.pk}'
        return format_html('<a href="{}">{} Inscrições</a>', url, count)
    ver_inscricoes_link.short_description = "Inscrições"
    
    def relatorio_cotacoes_link(self, obj):
        url = reverse('passeios:relatorio_cotacoes', args=[obj.pk])
        return format_html('<a href="{}">Ver Cotações</a>', url)
    relatorio_cotacoes_link.short_description = "Cotações"

    @admin.display(description='Destino', ordering='cidade_destino')
    def get_destino_formatado(self, obj):
        return obj.destino_formatado

@admin.action(description='Confirmar inscrições selecionadas')
def confirmar_inscricoes(modeladmin, request, queryset):
    """Ação para mudar o status de inscrições para 'confirmada'."""
    updated_count = queryset.update(status_inscricao='confirmada')
    modeladmin.message_user(request, f'{updated_count} inscrições foram confirmadas.', messages.SUCCESS)

@admin.action(description='Marcar como Pago Integralmente')
def marcar_como_pago(modeladmin, request, queryset):
    """Ação para mudar o status de pagamento para 'pago'."""
    updated_count = queryset.update(status_pagamento='pago')
    modeladmin.message_user(request, f'{updated_count} inscrições foram marcadas como pagas.', messages.SUCCESS)

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('voucher', 'cliente_link', 'get_passeio', 'status_inscricao_formatado', 'status_pagamento_formatado', 'get_valor_pago', 'get_saldo_devedor')
    list_filter = ('status_inscricao', 'status_pagamento', 'pacote__passeio') # Filtra por status e pelo passeio do pacote
    search_fields = ('cliente__nome', 'pacote__titulo')
    autocomplete_fields = ['cliente', 'pacote']
    readonly_fields = ('data_inscricao', 'voucher')
    inlines = [PagamentoInline]
    actions = [confirmar_inscricoes, marcar_como_pago]
    list_per_page = 25

    @admin.display(description='Cliente', ordering='cliente__nome')
    def cliente_link(self, obj):
        """Cria um link para a página de edição do cliente."""
        url = reverse('admin:cadastros_cliente_change', args=[obj.cliente.pk])
        return format_html('<a href="{}">{}</a>', url, obj.cliente.nome)

    @admin.display(description='Status da Inscrição', ordering='status_inscricao')
    def status_inscricao_formatado(self, obj):
        """Formata o status da inscrição com cores."""
        status_map = {
            'confirmada': ('#28a745', 'Confirmada'),
            'lista_espera': ('#ffc107', 'Lista de Espera'),
            'cancelada_cliente': ('#dc3545', 'Cancelada (Cliente)'),
            'cancelada_agencia': ('#dc3545', 'Cancelada (Agência)'),
        }
        cor, texto = status_map.get(obj.status_inscricao, ('#6c757d', obj.get_status_inscricao_display()))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            cor, texto
        )

    @admin.display(description='Status do Pagamento', ordering='status_pagamento')
    def status_pagamento_formatado(self, obj):
        """Formata o status do pagamento com cores."""
        status_map = {
            'pago': ('#28a745', 'Pago'),
            'parcial': ('#ffc107', 'Parcial'),
            'aguardando': ('#17a2b8', 'Aguardando'),
            'cancelado': ('#dc3545', 'Cancelado'),
        }
        cor, texto = status_map.get(obj.status_pagamento, ('#6c757d', obj.get_status_pagamento_display()))
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            cor, texto
        )

    def get_queryset(self, request):
        # Otimiza a consulta, pré-calculando o total pago para cada inscrição
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'cliente', 'pacote', 'pacote__passeio'
        ).annotate(
            total_pago=models.Sum('pagamentos__valor'))
        return queryset

    @admin.display(description='Passeio', ordering='pacote__passeio')
    def get_passeio(self, obj):
        return obj.pacote.passeio.titulo

    @admin.display(description='Preço (R$)', ordering='pacote__preco')
    def get_preco_pacote(self, obj):
        return obj.pacote.preco

    @admin.display(description='Valor Pago (R$)', ordering='total_pago')
    def get_valor_pago(self, obj):
        return obj.valor_pago

    @admin.display(description='Saldo Devedor (R$)', ordering='pacote__preco')
    def get_saldo_devedor(self, obj):
        saldo = obj.saldo_devedor
        # Formata o saldo para ter duas casas decimais
        saldo_formatado = f"{saldo:.2f}".replace('.', ',')

        if saldo <= 0:
            return format_html('<span style="color: #28a745; font-weight: bold;">R$ 0,00</span>')
        return format_html('<span style="color: red; font-weight: bold;">R$ {}</span>', saldo_formatado)

class ItemPacoteInline(admin.TabularInline):
    model = ItemPacote
    extra = 1

@admin.register(Pacote)
class PacoteAdmin(admin.ModelAdmin):
    """Configurações de administração para o modelo Pacote."""
    list_display = ('titulo', 'passeio', 'preco')
    list_filter = ('passeio',)
    search_fields = ('titulo', 'passeio__titulo')
    inlines = [ItemPacoteInline]

@admin.register(Cotacao)
class CotacaoAdmin(admin.ModelAdmin):
    """
    Tela de administração para gerenciar Cotações e seus pagamentos.
    """
    list_display = ('passeio', 'fornecedor', 'tipo_servico', 'valor_cotado', 'get_valor_pago', 'get_saldo_a_pagar', 'status', 'data_vencimento_pagamento')
    list_filter = ('status', 'passeio', 'fornecedor')
    search_fields = ('passeio__titulo', 'fornecedor__nome_fantasia')
    readonly_fields = ('get_valor_pago', 'get_saldo_a_pagar')
    inlines = [PagamentoFornecedorInline]

    fieldsets = (
        ('Detalhes da Cotação', {
            'fields': ('passeio', 'fornecedor', 'tipo_servico', 'valor_cotado', 'status', 'fornecedor_selecionado')
        }),
        ('Financeiro', {
            'fields': ('data_vencimento_pagamento', 'get_valor_pago', 'get_saldo_a_pagar')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['contas_a_pagar_url'] = reverse('passeios:relatorio_contas_a_pagar')
        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('passeio', 'fornecedor').annotate(total_pago_fornecedor=models.Sum('pagamentos_fornecedor__valor'))

    @admin.display(description='Valor Pago (R$)', ordering='total_pago_fornecedor')
    def get_valor_pago(self, obj):
        return obj.valor_pago

    @admin.display(description='Saldo a Pagar (R$)')
    def get_saldo_a_pagar(self, obj):
        saldo = obj.saldo_a_pagar
        cor = 'red' if saldo > 0 else 'green'
        return format_html(f'<span style="color: {cor}; font-weight: bold;">R$ {saldo:.2f}</span>')


# ========== PAYMENT GATEWAY TRANSACTION ADMIN ==========
@admin.register(PaymentGatewayTransaction)
class PaymentGatewayTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'gateway', 
        'get_gateway_id_display',
        'get_inscricao_display',
        'get_status_colored',
        'get_valor_display',
        'metodo_pagamento',
        'parcelas',
        'get_webhook_status',
        'criada_em'
    )
    
    list_filter = ('gateway', 'status', 'metodo_pagamento', 'criada_em', 'webhook_confirmado')
    search_fields = ('gateway_id', 'pagamento__inscricao__cliente__nome', 'pagamento__inscricao__id')
    readonly_fields = ('gateway_id', 'criada_em', 'get_json_webhook')
    
    fieldsets = (
        ('Informações do Gateway', {
            'fields': ('gateway', 'gateway_id', 'status')
        }),
        ('Pagamento Relacionado', {
            'fields': ('pagamento',)
        }),
        ('Valores e Parcelamento', {
            'fields': ('valor', 'metodo_pagamento', 'parcelas')
        }),
        ('Webhook', {
            'fields': ('webhook_confirmado', 'get_json_webhook'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('criada_em', 'confirmada_em'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pagamento__inscricao__cliente', 'pagamento__inscricao__pacote')
    
    @admin.display(description='Status', ordering='status')
    def get_status_colored(self, obj):
        cores = {
            'pendente': '#ffc107',
            'processando': '#17a2b8',
            'aprovado': '#28a745',
            'rejeitado': '#dc3545',
            'cancelado': '#6c757d',
            'reembolsado': '#e83e8c'
        }
        cor = cores.get(obj.status, '#999')
        return format_html(
            f'<span style="background-color: {cor}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{obj.get_status_display()}</span>'
        )
    
    @admin.display(description='Gateway ID')
    def get_gateway_id_display(self, obj):
        return format_html(
            f'<code style="background: #f5f5f5; padding: 2px 5px; border-radius: 3px;">{obj.gateway_id}</code>'
        )
    
    @admin.display(description='Inscrição')
    def get_inscricao_display(self, obj):
        if obj.pagamento and obj.pagamento.inscricao:
            inscricao = obj.pagamento.inscricao
            url = reverse('admin:passeios_inscricao_change', args=[inscricao.id])
            return format_html(
                f'<a href="{url}">Inscrição #{inscricao.id} - {inscricao.cliente.nome}</a>'
            )
        return '—'
    
    @admin.display(description='Valor')
    def get_valor_display(self, obj):
        return format_html(f'<strong>R$ {obj.valor:.2f}</strong>')
    
    @admin.display(description='Webhook', ordering='webhook_confirmado')
    def get_webhook_status(self, obj):
        if obj.webhook_confirmado:
            return format_html(
                f'<span style="color: green; font-weight: bold;">✅ Confirmado</span>'
            )
        else:
            return format_html(
                f'<span style="color: orange; font-weight: bold;">⏳ Pendente</span>'
            )
    
    @admin.display(description='JSON do Webhook')
    def get_json_webhook(self, obj):
        if obj.gateway_id:
            return format_html(
                f'<code style="background: #f5f5f5; padding: 10px; border-radius: 3px; display: block; overflow-x: auto; max-height: 200px;">ID: {obj.gateway_id}</code>'
            )
        return '—'
    
    def has_add_permission(self, request):
        # Não permitir criar manualmente, só via PaymentService
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Não permitir deletar, apenas para auditoria
        return False