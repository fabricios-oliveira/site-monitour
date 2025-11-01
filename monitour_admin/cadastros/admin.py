from django.contrib import admin
from .models import Cliente, Fornecedor, TipoVeiculo, ContatoFornecedor, ContaBancariaFornecedor, MatriculaCliente
from django.db.models import Count, Sum
from django.contrib import messages
from passeios.models import Inscricao  # Importa o modelo diretamente, o que é seguro.
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class InscricaoInline(admin.TabularInline):
    """Mostra as inscrições do cliente de forma compacta na tela do Cliente."""
    model = Inscricao
    extra = 0
    # Usamos os nomes dos campos do modelo diretamente, que é mais simples para inlines.
    fields = ('pacote', 'status_inscricao', 'status_pagamento', 'data_inscricao')
    readonly_fields = fields
    can_delete = False
    verbose_name = "Inscrição"
    verbose_name_plural = "Histórico de Inscrições"

    def has_add_permission(self, request, obj=None):
        return False

@admin.action(description='Enviar e-mail de promoção para clientes selecionados')
def enviar_email_promocional(modeladmin, request, queryset):
    # Por enquanto, esta ação apenas simula o envio e marca os clientes.
    # No futuro, aqui entraria a lógica de envio de e-mail real.
    count = queryset.count()
    messages.success(request, f'{count} cliente(s) foram notificados com a promoção.')
    # Exemplo: queryset.update(recebeu_promocao=True)

class ClienteResource(resources.ModelResource):
    def before_import_row(self, row, **kwargs):
        """
        Este método é executado ANTES de cada linha ser importada.
        Usamos ele para limpar e padronizar os dados.
        """
        # Limpa o CPF: remove pontos, traços, espaços e qualquer outra coisa que não seja número.
        if 'cpf' in row and row['cpf']:
            # Mantém apenas os dígitos numéricos
            row['cpf'] = ''.join(filter(str.isdigit, str(row['cpf'])))

    class Meta:
        model = Cliente
        
        # --- SIMPLIFICANDO O MODELO DA PLANILHA ---
        # Define os campos essenciais para importação e exportação.
        # O usuário só precisará preencher estes campos.
        fields = ('nome', 'cpf', 'email', 'telefone')
        
        # Pula a importação de linhas que não mudaram ou que gerariam erro
        skip_unchanged = True
        report_skipped = True
        
        # Se um cliente com o mesmo 'id' ou 'cpf' já existir, ele será atualizado
        import_id_fields = ('cpf',)
        
        # Ignora linhas que tenham erros (ex: nome ou cpf em branco) e continua a importação.
        skip_row_on_error = True

@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin):
    """
    Configurações de administração para o modelo Cliente.
    Interface melhorada com campos pessoais completos e histórico de vendas.
    """
    # Campos exibidos na lista de clientes
    list_display = (
        'get_matricula_formatada', 'nome', 'cpf_formatado', 'telefone', 
        'total_viagens', 'gasto_total', 'nivel_fidelidade', 'data_cadastro'
    )
    list_filter = ('data_cadastro', 'genero', 'estado_civil', 'cidade')
    search_fields = ('nome', 'cpf', 'email', 'matricula__id', 'rg')
    
    # Readonly para campos auto-gerados
    readonly_fields = ('data_cadastro', 'data_atualizacao', 'get_matricula_info', 'get_historico_vendas')
    
    # Inlines para mostrar dados relacionados
    inlines = [InscricaoInline]
    
    # Ações customizadas
    actions = [enviar_email_promocional]
    
    # Organiza campos em seções lógicas
    fieldsets = (
        ('📋 DADOS DE MATRÍCULA', {
            'fields': ('get_matricula_info',),
            'description': 'Matrícula gerada automaticamente ao criar o cliente'
        }),
        ('👤 DADOS PESSOAIS', {
            'fields': ('nome', 'cpf', 'rg', 'data_nascimento', 'genero', 'nacionalidade', 'estado_civil', 'profissao'),
            'classes': ('wide',)
        }),
        ('📞 CONTATO', {
            'fields': ('email', 'telefone', 'telefone_adicional'),
            'classes': ('wide',)
        }),
        ('📍 ENDEREÇO', {
            'fields': (
                'endereco', 'numero', 'complemento', 'bairro', 
                'cep', 'cidade', 'estado', 'ponto_referencia'
            ),
            'classes': ('wide', 'collapse'),
            'description': 'Endereço residencial do cliente'
        }),
        ('📊 HISTÓRICO DE VENDAS', {
            'fields': ('get_historico_vendas',),
            'classes': ('wide', 'collapse'),
            'description': 'Resumo de inscrições e pagamentos'
        }),
        ('📝 OBSERVAÇÕES E DATAS', {
            'fields': ('observacoes', 'data_cadastro', 'data_atualizacao'),
            'classes': ('wide', 'collapse')
        }),
    )
    
    resource_class = ClienteResource

    def get_queryset(self, request):
        """Otimiza a consulta para evitar N+1."""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _total_viagens=Count('inscricoes__pacote__passeio', distinct=True),
            _gasto_total=Sum('inscricoes__pagamentos__valor')
        )
        return queryset.select_related('matricula').prefetch_related('inscricoes__pacote__passeio')

    @admin.display(description='Matrícula', ordering='matricula__id')
    def get_matricula_formatada(self, obj):
        """Exibe o número da matrícula formatado."""
        if obj.matricula:
            return f"{obj.matricula.id}"  # Exibe apenas os números
        return "❌ Sem matrícula"

    @admin.display(description='CPF')
    def cpf_formatado(self, obj):
        """Exibe o CPF formatado."""
        cpf = obj.cpf
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf

    @admin.display(description='Total de Viagens', ordering='_total_viagens')
    def total_viagens(self, obj):
        """Mostra o total de viagens."""
        viagens = obj._total_viagens or 0
        return f"🎫 {viagens}" if viagens > 0 else "0"

    @admin.display(description='Gasto Total (R$)', ordering='_gasto_total')
    def gasto_total(self, obj):
        """Mostra o gasto total formatado."""
        gasto = obj._gasto_total or 0
        return f"R$ {gasto:,.2f}".replace(',', '.').replace('.', ',', 1)

    def get_matricula_info(self, obj):
        """Exibe informações detalhadas da matrícula."""
        if obj.matricula:
            return f"""
            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; border-left: 4px solid #0066cc;">
                <h3 style="margin-top: 0;">🆔 Número de Matrícula: <strong style="color: #0066cc;">{obj.matricula.id}</strong></h3>
                <p><strong>CPF:</strong> {obj.cpf_formatado()}</p>
                <p><strong>Data de Criação:</strong> {obj.data_cadastro.strftime('%d/%m/%Y %H:%M')}</p>
                <p><em>A matrícula foi gerada automaticamente e é única para cada cliente.</em></p>
            </div>
            """
        return '<p style="color: red;"><strong>⚠️ Matrícula não gerada. Salve o cliente novamente.</strong></p>'
    
    get_matricula_info.allow_tags = True
    get_matricula_info.short_description = 'Informações da Matrícula'

    def get_historico_vendas(self, obj):
        """Exibe um resumo do histórico de vendas."""
        inscricoes = obj.inscricoes.all().select_related('pacote__passeio')
        
        if not inscricoes:
            return '<p style="color: #999;">Nenhuma inscrição registrada.</p>'
        
        html = '<div style="max-height: 400px; overflow-y: auto;">'
        html += '<table style="width: 100%; border-collapse: collapse;">'
        html += '<thead style="background-color: #f0f0f0;">'
        html += '<tr><th style="padding: 10px; text-align: left; border-bottom: 2px solid #ccc;">Passeio</th>'
        html += '<th style="padding: 10px; text-align: left; border-bottom: 2px solid #ccc;">Data</th>'
        html += '<th style="padding: 10px; text-align: left; border-bottom: 2px solid #ccc;">Valor</th>'
        html += '<th style="padding: 10px; text-align: left; border-bottom: 2px solid #ccc;">Status</th></tr>'
        html += '</thead><tbody>'
        
        total = 0
        for inscricao in inscricoes[:10]:  # Limita a 10 últimas
            passeio = inscricao.pacote.passeio
            valor = inscricao.pacote.preco
            total += valor
            status_color = {'pago': '#28a745', 'aguardando': '#ffc107', 'cancelado': '#dc3545', 'parcial': '#ff9800'}.get(
                inscricao.status_pagamento, '#6c757d'
            )
            status_label = dict(inscricao.STATUS_PAGAMENTO).get(inscricao.status_pagamento, 'Desconhecido')
            
            html += f'''<tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px;">{passeio.titulo}</td>
                <td style="padding: 10px;">{inscricao.data_inscricao.strftime('%d/%m/%Y')}</td>
                <td style="padding: 10px; text-align: right;">R$ {valor:,.2f}</td>
                <td style="padding: 10px;">
                    <span style="background-color: {status_color}; color: white; padding: 4px 8px; border-radius: 3px; font-size: 12px;">
                        {status_label}
                    </span>
                </td>
            </tr>'''
        
        html += f'''<tr style="background-color: #f9f9f9; font-weight: bold; border-top: 2px solid #ccc;">
            <td colspan="2" style="padding: 10px;">Total de Vendas:</td>
            <td style="padding: 10px; text-align: right;">R$ {total:,.2f}</td>
            <td style="padding: 10px;"></td>
        </tr>'''
        
        html += '</tbody></table>'
        
        if inscricoes.count() > 10:
            html += f'<p style="color: #999; font-size: 12px;">... e mais {inscricoes.count() - 10} inscrições</p>'
        
        html += '</div>'
        return html
    
    get_historico_vendas.allow_tags = True
    get_historico_vendas.short_description = 'Histórico de Vendas'

    class Media:
        """Adiciona JS e CSS personalizados."""
        js = ('cadastros/js/cliente_admin.js',)

class ContatoFornecedorInline(admin.TabularInline):
    model = ContatoFornecedor
    extra = 1

class ContaBancariaFornecedorInline(admin.TabularInline):
    model = ContaBancariaFornecedor
    extra = 1

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    """
    Configurações de administração para o modelo Fornecedor.
    """
    list_display = ('nome_fantasia', 'tipo', 'has_contacts', 'has_bank_accounts')
    search_fields = ('nome_fantasia', 'cnpj', 'razao_social')
    list_filter = ('tipo',)
    inlines = [ContatoFornecedorInline, ContaBancariaFornecedorInline]
    ordering = ('nome_fantasia',) # Ordena por nome fantasia por padrão
    fieldsets = (
        ('Informações Principais', {
            'fields': ('nome_fantasia', 'razao_social', 'cnpj', 'tipo')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )

    @admin.display(description='Contatos?', boolean=True)
    def has_contacts(self, obj):
        """Verifica se o fornecedor possui contatos cadastrados."""
        # Usamos .exists() para ser eficiente e não carregar todos os objetos
        return obj.contatos.exists()

    @admin.display(description='Contas Bancárias?', boolean=True)
    def has_bank_accounts(self, obj):
        """Verifica se o fornecedor possui contas bancárias cadastradas."""
        return obj.contas_bancarias.exists()

    def get_queryset(self, request):
        """Otimiza a consulta para o list_display."""
        queryset = super().get_queryset(request)
        # Prefetch related para as inlines, se você quiser usar os dados delas em list_display
        # ou para evitar N+1 ao acessar contatos/contas em outras partes do admin.
        return queryset.prefetch_related('contatos', 'contas_bancarias')

@admin.register(TipoVeiculo)
class TipoVeiculoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'capacidade', 'fileiras', 'layout_colunas')
    search_fields = ('nome',)
    fields = ('nome', 'capacidade', 'fileiras', 'layout_colunas', 'custo_base_transporte')

@admin.register(MatriculaCliente)
class MatriculaClienteAdmin(admin.ModelAdmin):
    """Admin para o modelo de matrículas, útil para consulta."""
    list_display = ('id', 'cpf')
    search_fields = ('id', 'cpf')
    readonly_fields = ('id', 'cpf') # Torna os campos somente leitura
