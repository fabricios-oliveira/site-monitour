from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms import ExtratoUploadForm
from .models import Transacao, RegraCategorizacao, Conta
from django.db.models import Sum, Count
from ofxparse import OfxParser
import hashlib
import json
from core.services.financial_service import FinancialService

@staff_member_required
def dashboard_financeiro_view(request):
    """
    Dashboard financeiro COMPLETO com visão consolidada de toda a saúde financeira do negócio.
    Mostra receitas, despesas, lucros, contas a pagar/receber, e análise por passeio.
    """
    # Obtém período de análise (padrão: 30 dias)
    periodo_dias = int(request.GET.get('periodo', 30))
    
    # Busca todos os dados financeiros consolidados via serviço
    dados_financeiros = FinancialService.get_dashboard_completo(periodo_dias=periodo_dias)
    
    # Dados do módulo de contas bancárias (se houver)
    saldo_contas_bancarias = 0.00
    try:
        contas = Conta.objects.filter(usuario=request.user)
        if contas.exists():
            saldo_contas_bancarias = contas.aggregate(
                total=Sum('transacoes__valor')
            )['total'] or 0.00
    except Exception as e:
        # Se houver erro ao acessar contas, apenas ignora
        pass
    
    # Prepara dados para gráficos
    # Gráfico 1: Receitas vs Despesas
    chart_receitas_despesas = {
        'labels': ['Receita Confirmada', 'Despesa Confirmada'],
        'data': [
            float(dados_financeiros['receitas']['receita_confirmada']),
            float(dados_financeiros['despesas']['despesa_confirmada'])
        ],
        'colors': ['#28a745', '#dc3545']
    }
    
    # Gráfico 2: Resultado por Passeio (Top 5)
    chart_resultado_passeios = {
        'labels': [r['passeio'].titulo[:30] for r in dados_financeiros['resultados_passeios']],
        'data': [float(r['lucro']) for r in dados_financeiros['resultados_passeios']],
        'colors': ['#28a745' if r['status'] == 'lucro' else '#dc3545' for r in dados_financeiros['resultados_passeios']]
    }
    
    # Gráfico 3: Composição de Despesas
    chart_composicao_despesas = {
        'labels': ['Sem dados'],
        'data': [0]
    }
    
    # Tenta buscar dados de despesas por tipo, mas não quebra se falhar
    try:
        from passeios.models import GastoPasseio, Cotacao
        gastos_por_tipo = {}
        for gasto in GastoPasseio.objects.filter(
            data_gasto__date__gte=dados_financeiros['periodo']['data_inicio']
        ):
            tipo = gasto.get_tipo_gasto_display()
            gastos_por_tipo[tipo] = gastos_por_tipo.get(tipo, 0) + float(gasto.valor)
        
        for cotacao in Cotacao.objects.filter(
            status='aceita',
            data_cotacao__date__gte=dados_financeiros['periodo']['data_inicio']
        ):
            tipo = cotacao.get_tipo_servico_display()
            gastos_por_tipo[tipo] = gastos_por_tipo.get(tipo, 0) + float(cotacao.valor_cotado)
        
        if gastos_por_tipo:
            chart_composicao_despesas = {
                'labels': list(gastos_por_tipo.keys()),
                'data': list(gastos_por_tipo.values())
            }
    except Exception as e:
        # Se houver erro, mantém os dados vazios
        pass
    
    context = {
        'dados': dados_financeiros,
        'saldo_contas_bancarias': saldo_contas_bancarias,
        'periodo_selecionado': periodo_dias,
        'periodos_disponiveis': [7, 15, 30, 60, 90, 180, 365],
        # Dados para gráficos (em JSON)
        'chart_receitas_despesas_json': json.dumps(chart_receitas_despesas),
        'chart_resultado_passeios_json': json.dumps(chart_resultado_passeios),
        'chart_composicao_despesas_json': json.dumps(chart_composicao_despesas),
    }
    return render(request, 'financas/dashboard_financeiro.html', context)

def _aplicar_regras_categorizacao(descricao, usuario):
    """Aplica as regras de categorização para encontrar a categoria correta."""
    regras = RegraCategorizacao.objects.filter(usuario=usuario)
    for regra in regras:
        if regra.palavra_chave.lower() in descricao.lower():
            return regra.categoria
    return None

@staff_member_required
def upload_extrato_view(request):
    transacoes_importadas = 0
    transacoes_ignoradas = 0

    if request.method == 'POST':
        form = ExtratoUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            conta_selecionada = form.cleaned_data['conta']
            arquivo_ofx = request.FILES['arquivo_ofx']

            try:
                # Lê o arquivo em memória
                ofx_content = arquivo_ofx.read()
                ofx = OfxParser.parse(ofx_content)

                for transacao_ofx in ofx.account.statement.transactions:
                    # 1. Lógica de Deduplicação
                    unique_string = f"{transacao_ofx.date.strftime('%Y-%m-%d')}-{transacao_ofx.amount}-{transacao_ofx.memo}"
                    hash_id = hashlib.sha256(unique_string.encode()).hexdigest()

                    if Transacao.objects.filter(hash_transacao=hash_id).exists():
                        transacoes_ignoradas += 1
                        continue # Pula para a próxima transação

                    # 2. Lógica de Categorização Inteligente
                    categoria_sugerida = _aplicar_regras_categorizacao(transacao_ofx.memo, request.user)

                    # 3. Persistência no Banco de Dados
                    Transacao.objects.create(
                        conta=conta_selecionada,
                        data=transacao_ofx.date.date(),
                        descricao=transacao_ofx.memo,
                        valor=transacao_ofx.amount,
                        categoria=categoria_sugerida,
                        # O hash será gerado automaticamente pelo método save() do modelo
                    )
                    transacoes_importadas += 1

                messages.success(request, f"{transacoes_importadas} transações importadas com sucesso!")
                if transacoes_ignoradas > 0:
                    messages.info(request, f"{transacoes_ignoradas} transações duplicadas foram ignoradas.")
                
                return redirect('financas:lista_transacoes')

            except Exception as e:
                messages.error(request, f"Erro ao processar o arquivo: {e}")

    else:
        form = ExtratoUploadForm(user=request.user)

    context = {
        'form': form,
        'title': 'Importar Extrato Bancário'
    }
    return render(request, 'financas/upload_extrato.html', context)

@staff_member_required
def lista_transacoes_view(request):
    transacoes = Transacao.objects.select_related('conta', 'categoria').all()
    context = {
        'transacoes': transacoes,
        'title': 'Transações Importadas'
    }
    return render(request, 'financas/lista_transacoes.html', context)