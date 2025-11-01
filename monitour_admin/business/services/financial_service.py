"""
Serviço centralizado para cálculos financeiros do sistema.
Evita duplicação de código e melhora testabilidade.
"""
from decimal import Decimal
from django.db.models import Sum, Q, F, DecimalField, Case, When, Value
from django.utils import timezone
from datetime import timedelta


class FinancialService:
    """Serviço para cálculos e análises financeiras consolidadas."""
    
    @staticmethod
    def get_receitas_periodo(data_inicio=None, data_fim=None):
        """
        Calcula receitas (pagamentos recebidos de clientes) no período.
        
        Args:
            data_inicio: Data inicial do período (default: primeiro dia do mês atual)
            data_fim: Data final do período (default: hoje)
            
        Returns:
            dict com receita_total, receita_confirmada, receita_pendente
        """
        from passeios.models import Inscricao, Pagamento
        
        if not data_inicio:
            hoje = timezone.now().date()
            data_inicio = hoje.replace(day=1)
        if not data_fim:
            data_fim = timezone.now().date()
        
        # Receita de inscrições no período
        inscricoes_periodo = Inscricao.objects.filter(
            data_inscricao__date__range=[data_inicio, data_fim]
        )
        
        receita_total_prevista = inscricoes_periodo.aggregate(
            total=Sum('pacote__preco')
        )['total'] or Decimal('0.00')
        
        # Pagamentos efetivamente recebidos no período
        pagamentos_recebidos = Pagamento.objects.filter(
            data_pagamento__date__range=[data_inicio, data_fim]
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        receita_pendente = receita_total_prevista - pagamentos_recebidos
        
        return {
            'receita_total_prevista': receita_total_prevista,
            'receita_confirmada': pagamentos_recebidos,
            'receita_pendente': receita_pendente,
            'total_inscricoes': inscricoes_periodo.count()
        }
    
    @staticmethod
    def get_despesas_periodo(data_inicio=None, data_fim=None):
        """
        Calcula despesas (pagamentos a fornecedores + gastos internos) no período.
        
        Returns:
            dict com despesa_total, despesa_paga, despesa_pendente
        """
        from passeios.models import Cotacao, PagamentoFornecedor, GastoPasseio
        
        if not data_inicio:
            hoje = timezone.now().date()
            data_inicio = hoje.replace(day=1)
        if not data_fim:
            data_fim = timezone.now().date()
        
        # Despesas de cotações aceitas com vencimento no período
        cotacoes_periodo = Cotacao.objects.filter(
            status='aceita',
            data_vencimento_pagamento__range=[data_inicio, data_fim]
        ) | Cotacao.objects.filter(
            status='aceita',
            data_cotacao__date__range=[data_inicio, data_fim],
            data_vencimento_pagamento__isnull=True
        )
        
        despesa_cotacoes_prevista = cotacoes_periodo.aggregate(
            total=Sum('valor_cotado')
        )['total'] or Decimal('0.00')
        
        # Pagamentos efetivamente feitos a fornecedores no período
        pagamentos_fornecedores = PagamentoFornecedor.objects.filter(
            data_pagamento__date__range=[data_inicio, data_fim]
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        # Gastos internos no período
        gastos_internos = GastoPasseio.objects.filter(
            data_gasto__date__range=[data_inicio, data_fim]
        ).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')
        
        despesa_total = despesa_cotacoes_prevista + gastos_internos
        despesa_paga = pagamentos_fornecedores + gastos_internos
        despesa_pendente = despesa_total - despesa_paga
        
        return {
            'despesa_total_prevista': despesa_total,
            'despesa_confirmada': despesa_paga,
            'despesa_pendente': despesa_pendente,
            'cotacoes_previstas': cotacoes_periodo.count(),
            'gastos_internos': gastos_internos
        }
    
    @staticmethod
    def get_contas_a_receber():
        """
        Lista todas as inscrições com saldo devedor (contas a receber de clientes).
        
        Returns:
            QuerySet anotado com saldo_devedor
        """
        from passeios.models import Inscricao
        from django.db.models import Sum
        
        return Inscricao.objects.annotate(
            valor_pago_total=Sum('pagamentos__valor')
        ).annotate(
            saldo_devedor=F('pacote__preco') - F('valor_pago_total')
        ).filter(
            saldo_devedor__gt=0,
            status_inscricao='confirmada'
        ).select_related('cliente', 'pacote__passeio').order_by('pacote__passeio__data_ida')
    
    @staticmethod
    def get_contas_a_pagar():
        """
        Lista todas as cotações aceitas com saldo a pagar (contas a pagar a fornecedores).
        
        Returns:
            QuerySet anotado com saldo_a_pagar
        """
        from passeios.models import Cotacao
        
        return Cotacao.objects.annotate(
            valor_pago_total=Sum('pagamentos_fornecedor__valor')
        ).annotate(
            saldo_calculado=F('valor_cotado') - F('valor_pago_total')
        ).filter(
            status='aceita',
            saldo_calculado__gt=0
        ).select_related('fornecedor', 'passeio').order_by('data_vencimento_pagamento')
    
    @staticmethod
    def get_resultados_por_passeio():
        """
        Calcula o resultado financeiro (lucro/prejuízo) de cada passeio.
        
        Returns:
            Lista de dicts com informações de cada passeio
        """
        from passeios.models import Passeio, Inscricao
        
        passeios = Passeio.objects.with_custo_total().filter(
            status__in=['confirmado', 'realizado']
        ).prefetch_related('pacotes__inscricoes')
        
        resultados = []
        for passeio in passeios:
            receita = Inscricao.objects.filter(
                pacote__passeio=passeio
            ).aggregate(total=Sum('pacote__preco'))['total'] or Decimal('0.00')
            
            custo = passeio.custo_total_previsto
            lucro = receita - custo
            margem = (lucro / receita * 100) if receita > 0 else 0
            
            resultados.append({
                'passeio': passeio,
                'receita': receita,
                'custo': custo,
                'lucro': lucro,
                'margem_percentual': margem,
                'status': 'lucro' if lucro > 0 else 'prejuizo'
            })
        
        return sorted(resultados, key=lambda x: x['lucro'], reverse=True)
    
    @staticmethod
    def get_dashboard_completo(periodo_dias=30):
        """
        Retorna todos os dados consolidados para o dashboard financeiro.
        
        Args:
            periodo_dias: Número de dias para análise (default: 30)
            
        Returns:
            dict com todas as métricas financeiras consolidadas
        """
        hoje = timezone.now().date()
        data_inicio = hoje - timedelta(days=periodo_dias)
        
        # Receitas
        receitas = FinancialService.get_receitas_periodo(data_inicio, hoje)
        
        # Despesas
        despesas = FinancialService.get_despesas_periodo(data_inicio, hoje)
        
        # Lucro do período
        lucro_periodo = receitas['receita_confirmada'] - despesas['despesa_confirmada']
        lucro_previsto = receitas['receita_total_prevista'] - despesas['despesa_total_prevista']
        
        # Contas a receber/pagar
        contas_receber = FinancialService.get_contas_a_receber()
        contas_pagar = FinancialService.get_contas_a_pagar()
        
        total_a_receber = contas_receber.aggregate(
            total=Sum('saldo_devedor')
        )['total'] or Decimal('0.00')
        
        total_a_pagar = contas_pagar.aggregate(
            total=Sum('saldo_calculado')
        )['total'] or Decimal('0.00')
        
        # Saldo líquido previsto (caixa + a receber - a pagar)
        saldo_liquido_previsto = receitas['receita_confirmada'] - despesas['despesa_confirmada'] + total_a_receber - total_a_pagar
        
        # Resultados por passeio
        resultados_passeios = FinancialService.get_resultados_por_passeio()
        
        return {
            'periodo': {
                'data_inicio': data_inicio,
                'data_fim': hoje,
                'dias': periodo_dias
            },
            'receitas': receitas,
            'despesas': despesas,
            'lucro': {
                'confirmado': lucro_periodo,
                'previsto': lucro_previsto,
                'margem': (lucro_periodo / receitas['receita_confirmada'] * 100) if receitas['receita_confirmada'] > 0 else 0
            },
            'contas_receber': {
                'total': total_a_receber,
                'quantidade': contas_receber.count(),
                'lista': contas_receber[:10]  # Top 10 para o dashboard
            },
            'contas_pagar': {
                'total': total_a_pagar,
                'quantidade': contas_pagar.count(),
                'lista': contas_pagar[:10]  # Top 10 para o dashboard
            },
            'saldo_liquido_previsto': saldo_liquido_previsto,
            'resultados_passeios': resultados_passeios[:5],  # Top 5 passeios
        }
