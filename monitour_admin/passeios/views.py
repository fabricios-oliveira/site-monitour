from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
import json
from decimal import Decimal
from django.db.models import Sum, F, DecimalField
from django.shortcuts import get_object_or_404
from weasyprint import HTML
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Passeio, Inscricao, VeiculoPasseio, Assento, Pacote, Cotacao, GastoPasseio
from cadastros.models import Cliente

# Create your views here.

def _montar_layout_assentos(veiculo_passeio, com_dados_cliente=False):
    """Função auxiliar para gerar a estrutura de assentos de um veículo."""
    tipo_veiculo = veiculo_passeio.tipo_veiculo
    assentos_ocupados = {a.numero: a.cliente for a in veiculo_passeio.assentos.all().select_related('cliente')}
    
    layout = []
    assento_num = 1
    colunas_layout = tipo_veiculo.layout_colunas.split('-')
    
    for fileira_num in range(1, tipo_veiculo.fileiras + 1):
        fileira_obj = {'grupos': []}
        for grupo_str in colunas_layout:
            grupo_assentos = []
            if grupo_str.isdigit():
                for _ in range(int(grupo_str)):
                    if assento_num > tipo_veiculo.capacidade:
                        continue
    
                    cliente = assentos_ocupados.get(assento_num)
                    assento_data = {'numero': assento_num, 'cliente_nome': cliente.nome if cliente else ''}
                    if com_dados_cliente:
                        assento_data.update({'ocupado': cliente is not None, 'cliente_id': cliente.id if cliente else ''})
                    grupo_assentos.append(assento_data)
                    assento_num += 1
            fileira_obj['grupos'].append(grupo_assentos)
        layout.append(fileira_obj)
    return layout

def gerar_relatorio_passageiros(request, passeio_id):
    """
    Gera um relatório em PDF com a lista de passageiros de um passeio.
    """
    passeio = get_object_or_404(Passeio, pk=passeio_id)
    inscricoes = Inscricao.objects.filter(pacote__passeio=passeio).select_related('cliente', 'pacote').order_by('cliente__nome')
    
    # --- Lógica para montar o mapa de assentos para o PDF ---
    mapa_layout = None
    # Lógica CORRIGIDA e robusta:
    # Se o passeio tem um tipo de veículo, garante que o VeiculoPasseio correspondente exista ou o cria.
    if passeio.tipo_veiculo:
        veiculo_passeio, _ = VeiculoPasseio.objects.get_or_create(
            passeio=passeio,
            defaults={'tipo_veiculo': passeio.tipo_veiculo, 'identificacao': 'Veículo Principal'}
        )
        mapa_layout = _montar_layout_assentos(veiculo_passeio)

    context = {'passeio': passeio, 'inscricoes': inscricoes, 'mapa_layout': mapa_layout}
    html_string = render_to_string('passeios/relatorio_passageiros.html', context)
    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{passeio.titulo}.pdf"'
    return response

@staff_member_required
def mapa_assentos_view(request, veiculo_passeio_id):
    veiculo_passeio = get_object_or_404(VeiculoPasseio.objects.select_related('tipo_veiculo', 'passeio'), pk=veiculo_passeio_id)
    layout_data = _montar_layout_assentos(veiculo_passeio, com_dados_cliente=True)

    # Otimização: Pega apenas os clientes que AINDA NÃO estão alocados neste veículo
    # E também os clientes que estão inscritos no passeio, para relevância.
    clientes_inscritos_ids = Inscricao.objects.filter(pacote__passeio=veiculo_passeio.passeio).values_list('cliente_id', flat=True)
    clientes_alocados_ids = veiculo_passeio.assentos.exclude(cliente__isnull=True).values_list('cliente_id', flat=True)
    
    # Clientes disponíveis são os inscritos no passeio que ainda não foram alocados.
    clientes_disponiveis = Cliente.objects.filter(id__in=clientes_inscritos_ids).exclude(id__in=clientes_alocados_ids).order_by('nome')

    context = {
        'veiculo_passeio': veiculo_passeio,
        'layout': layout_data,
        'clientes': clientes_disponiveis,
        'title': f"Mapa de Assentos - {veiculo_passeio.identificacao}"
    }
    return render(request, 'passeios/mapa_assentos.html', context)

@staff_member_required
@require_POST
def salvar_assento_view(request):
    try:
        veiculo_passeio_id = request.POST.get('veiculo_passeio_id')
        numero_assento = request.POST.get('numero_assento')
        cliente_id = request.POST.get('cliente_id')

        veiculo_passeio = get_object_or_404(VeiculoPasseio, pk=veiculo_passeio_id)

        # Se cliente_id for vazio, significa desocupar o assento
        if not cliente_id:
            Assento.objects.filter(veiculo_passeio=veiculo_passeio, numero=numero_assento).delete()
            return JsonResponse({'status': 'success', 'message': 'Assento desocupado.'})

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        # Atualiza ou cria o assento
        assento, created = Assento.objects.update_or_create(
            veiculo_passeio=veiculo_passeio, numero=numero_assento,
            defaults={'cliente': cliente}
        )
        return JsonResponse({'status': 'success', 'message': f'Assento {numero_assento} salvo para {cliente.nome}.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@staff_member_required
def relatorio_financeiro_view(request, passeio_id):
    """
    Gera uma página com o resumo financeiro de um passeio.
    """
    # Usando o manager otimizado para calcular o custo total em uma única consulta
    passeio = get_object_or_404(
        Passeio.objects.with_custo_total().prefetch_related('cotacoes', 'gastos', 'pacotes__inscricoes'), pk=passeio_id
    )

    # --- CÁLCULO DE CUSTOS ---
    custo_total_previsto = passeio.custo_total_previsto
    custos_detalhados = {
        'cotacoes_aceitas': passeio.cotacoes.filter(status='aceita').select_related('fornecedor'),
        'gastos_internos': passeio.gastos.all()
    }

    # --- DADOS PARA O GRÁFICO DE CUSTOS ---
    custos_por_categoria = {}
    for cotacao in custos_detalhados['cotacoes_aceitas']:
        categoria = cotacao.get_tipo_servico_display()
        custos_por_categoria[categoria] = custos_por_categoria.get(categoria, 0) + cotacao.valor_cotado
    for gasto in custos_detalhados['gastos_internos']:
        categoria = gasto.get_tipo_gasto_display()
        custos_por_categoria[categoria] = custos_por_categoria.get(categoria, 0) + gasto.valor

    chart_data = {
        "labels": list(custos_por_categoria.keys()),
        "data": [float(v) for v in custos_por_categoria.values()], # Converte Decimal para float
    }

    # --- CÁLCULO DE RECEITAS ---
    total_inscricoes = Inscricao.objects.filter(
        pacote__passeio=passeio
    ).count()

    # Usa o preço médio dos pacotes para uma análise mais precisa
    from django.db.models import Avg
    preco_medio_pacote = passeio.pacotes.aggregate(avg_price=Avg('preco'))['avg_price'] or Decimal('0.00')
    if preco_medio_pacote == Decimal('0.00') and passeio.pacotes.exists():
        preco_medio_pacote = passeio.pacotes.first().preco # Fallback para o primeiro pacote

    # Cálculo de receita mais preciso, somando o preço do pacote de cada inscrição
    receita_total_prevista = Inscricao.objects.filter(
        pacote__passeio=passeio
    ).aggregate(total=Sum('pacote__preco'))['total'] or Decimal('0.00')

    # Calcula o total efetivamente pago até o momento
    total_arrecadado = Inscricao.objects.filter(
        pacote__passeio=passeio
    ).aggregate(total=Sum('pagamentos__valor'))['total'] or 0

    saldo_a_receber = receita_total_prevista - total_arrecadado

    # --- CÁLCULO DE LUCRO ---
    lucro_projetado = receita_total_prevista - custo_total_previsto
    lucro_atual = total_arrecadado - custo_total_previsto

    # --- CÁLCULO DE PONTO DE EQUILÍBRIO (BREAK-EVEN) ---
    lotacao_break_even = 0
    if preco_medio_pacote > 0:
        lotacao_break_even = (custo_total_previsto / preco_medio_pacote)

    # --- INDICADOR DE STATUS DE VIABILIDADE (A "INTELIGÊNCIA") ---
    status_viabilidade = {
        "texto": "Análise Indisponível",
        "cor": "gray",
        "descricao": "Cadastre os custos e o preço do pacote para iniciar a análise."
    }
    if custo_total_previsto > 0 and preco_medio_pacote > 0:
        if receita_total_prevista >= custo_total_previsto:
            status_viabilidade = {"texto": "Lucrativo", "cor": "#28a745", "descricao": "O passeio já cobriu seus custos e está gerando lucro."}
        elif total_inscricoes >= passeio.lotacao_minima_desejada:
            status_viabilidade = {"texto": "Atenção", "cor": "#ffc107", "descricao": "Atingiu a lotação mínima, mas ainda não cobriu todos os custos."}
        else:
            status_viabilidade = {"texto": "Em Risco", "cor": "#dc3545", "descricao": "Abaixo da lotação mínima e não atingiu o ponto de equilíbrio."}


    # --- ANÁLISE DE VIABILIDADE (Ponto de Equilíbrio e Preço Sugerido) ---
    preco_sugerido = 0
    preco_promocional_sugerido = 0
    lucro_por_pessoa_ideal = 0
    lucro_por_pessoa_promocional = 0
    custo_por_pessoa_break_even = 0
    capacidade = passeio.tipo_veiculo.capacidade if passeio.tipo_veiculo and passeio.tipo_veiculo.capacidade > 0 else total_inscricoes
    if capacidade > 0:
        custo_por_pessoa_break_even = custo_total_previsto / capacidade
        if passeio.margem_lucro_desejada < 100:
            # Fórmula: Preço de Venda = Custo / (1 - Margem de Lucro)
            preco_sugerido = custo_por_pessoa_break_even / (1 - (passeio.margem_lucro_desejada / 100))
            lucro_por_pessoa_ideal = preco_sugerido - custo_por_pessoa_break_even
        if passeio.margem_lucro_promocional < 100:
            preco_promocional_sugerido = custo_por_pessoa_break_even / (1 - (passeio.margem_lucro_promocional / 100))
            lucro_por_pessoa_promocional = preco_promocional_sugerido - custo_por_pessoa_break_even
        else:
            # Evita divisão por zero ou negativo se a margem for >= 100%
            preco_sugerido = custo_por_pessoa_break_even * 2 # Apenas um fallback

    # --- "INTELIGÊNCIA ARTIFICIAL": SUGESTÃO DE MARGEM DE LUCRO ---
    margem_sugerida = None
    passeios_similares_count = 0
    passeios_historicos = Passeio.objects.filter(
        cidade_destino=passeio.cidade_destino,
        uf_destino=passeio.uf_destino,
        status='realizado'
    ).exclude(pk=passeio.pk).prefetch_related('pacotes__inscricoes', 'cotacoes', 'gastos')

    margens_historicas = []
    if passeios_historicos.exists():
        for p_hist in passeios_historicos:
            receita_hist = p_hist.pacotes.aggregate(total=Sum('inscricoes__pacote__preco'))['total'] or Decimal('0.00')
            custo_hist = p_hist.custo_total_previsto
            if receita_hist > 0:
                lucro_hist = receita_hist - custo_hist
                margem_real = (lucro_hist / receita_hist) * 100
                margens_historicas.append(margem_real)
        if margens_historicas:
            margem_sugerida = sum(margens_historicas) / len(margens_historicas)
            passeios_similares_count = len(margens_historicas)

    context = {
        'title': f'Resumo Financeiro: {passeio.titulo}',
        'passeio': passeio,
        'custo_total_previsto': custo_total_previsto,
        'custos_detalhados': custos_detalhados,
        'total_inscricoes': total_inscricoes,
        'preco_medio_pacote': preco_medio_pacote,
        'receita_total_prevista': receita_total_prevista,
        'total_arrecadado': total_arrecadado,
        'saldo_a_receber': saldo_a_receber,
        'lucro_projetado': lucro_projetado,
        'lucro_atual': lucro_atual,
        'preco_sugerido': preco_sugerido,
        'preco_promocional_sugerido': preco_promocional_sugerido,
        'lucro_por_pessoa_ideal': lucro_por_pessoa_ideal,
        'lucro_por_pessoa_promocional': lucro_por_pessoa_promocional,
        'lotacao_break_even': lotacao_break_even,
        'status_viabilidade': status_viabilidade,
        'custo_por_pessoa_break_even': custo_por_pessoa_break_even,
        'chart_data_json': json.dumps(chart_data),
        'margem_sugerida': margem_sugerida,
        'passeios_similares_count': passeios_similares_count,
    }

    return render(request, 'passeios/relatorio_financeiro.html', context)

@staff_member_required
def relatorio_cotacoes_view(request, passeio_id):
    """
    Gera uma página com o resumo das cotações para um passeio.
    """
    passeio = get_object_or_404(Passeio, pk=passeio_id)
    cotacoes = Cotacao.objects.filter(passeio=passeio).select_related('fornecedor').order_by('tipo_servico', 'valor_cotado')

    # Você pode adicionar lógica para agrupar por tipo de serviço,
    # ou destacar a cotação selecionada.

    context = {
        'title': f'Relatório de Cotações: {passeio.titulo}',
        'passeio': passeio,
        'cotacoes': cotacoes,
    }
    # Renderize um template HTML específico para este relatório
    return render(request, 'passeios/relatorio_cotacoes.html', context)

@staff_member_required
def gerar_relatorio_cotacoes_pdf(request, passeio_id):
    """
    Gera um relatório em PDF com a lista de cotações de um passeio.
    """
    passeio = get_object_or_404(Passeio, pk=passeio_id)
    cotacoes = Cotacao.objects.filter(passeio=passeio).select_related('fornecedor').order_by('tipo_servico', 'valor_cotado')

    context = {
        'passeio': passeio,
        'cotacoes': cotacoes,
    }
    html_string = render_to_string('passeios/relatorio_cotacoes_pdf.html', context)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cotacoes_{passeio.titulo.replace(" ", "_")}.pdf"'
    return response

@staff_member_required
def relatorio_contas_a_pagar_view(request):
    """
    Gera um relatório inteligente de "Contas a Pagar" para fornecedores.
    Lista todas as cotações aceitas com saldo devedor.
    """
    # Anota o total pago para cada cotação
    contas = Cotacao.objects.annotate(
        total_pago=Sum('pagamentos_fornecedor__valor', output_field=DecimalField())
    ).select_related('passeio', 'fornecedor')

    # Filtra apenas as cotações aceitas que ainda têm saldo a pagar
    contas_a_pagar = contas.filter(
        status='aceita',
        valor_cotado__gt=F('total_pago')
    ).order_by('data_vencimento_pagamento') # Ordena pela data de vencimento mais próxima

    context = {
        'title': 'Relatório de Contas a Pagar',
        'contas_a_pagar': contas_a_pagar,
    }
    return render(request, 'passeios/relatorio_contas_a_pagar.html', context)
