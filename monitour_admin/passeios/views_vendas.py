"""
Views e APIs para gerenciar o fluxo de pagamento de inscrições/vendas.
Integrado com Mercado Pago.
"""

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status as rest_status

from passeios.models import Inscricao, Pacote, Passeio, PaymentGatewayTransaction
from cadastros.models import Cliente, limpar_cpf
from passeios.services.payment_service import PaymentService
import logging
import json

logger = logging.getLogger(__name__)


@login_required
def tela_venda_principal(request):
    """
    Tela principal de vendas para operadores.
    Permite criar inscrições e processar pagamentos.
    """
    
    # Buscar dados para o formulário
    passeios = Passeio.objects.filter(status='confirmado').prefetch_related('pacotes')
    
    context = {
        'passeios': passeios,
        'metodos_pagamento': [
            {'id': 'cartao_credito', 'label': 'Cartão de Crédito', 'parcelas': True},
            {'id': 'cartao_debito', 'label': 'Cartão de Débito', 'parcelas': False},
            {'id': 'pix', 'label': 'PIX', 'parcelas': False},
        ]
    }
    
    return render(request, 'passeios/venda_principal.html', context)


@login_required
def buscar_cliente(request):
    """
    API para buscar clientes por CPF ou nome.
    Retorna JSON com dados do cliente.
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 3:
        return JsonResponse({'clientes': []})
    
    # Buscar por CPF (sem formatação)
    cpf_limpo = limpar_cpf(query)
    
    clientes = Cliente.objects.filter(
        models.Q(cpf=cpf_limpo) | models.Q(nome__icontains=query)
    )[:10]
    
    resultado = [
        {
            'id': c.id,
            'nome': c.nome,
            'cpf': c.cpf,
            'email': c.email,
            'matricula': c.matricula.id if c.matricula else 'N/A',
            'telefone': str(c.telefone) if c.telefone else '',
        }
        for c in clientes
    ]
    
    return JsonResponse({'clientes': resultado})


@require_POST
@login_required
def processar_pagamento_inscricao(request):
    """
    Processa o pagamento de uma inscrição.
    POST data:
    {
        "pacote_id": 123,
        "cliente_id": 456,
        "quantidade": 1,
        "metodo_pagamento": "cartao_credito|cartao_debito|pix",
        "parcelas": 1-12
    }
    """
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    
    # Validar dados
    pacote_id = data.get('pacote_id')
    cliente_id = data.get('cliente_id')
    metodo_pagamento = data.get('metodo_pagamento')
    parcelas = int(data.get('parcelas', 1))
    
    if not all([pacote_id, cliente_id, metodo_pagamento]):
        return JsonResponse({'error': 'Dados incompletos'}, status=400)
    
    try:
        pacote = Pacote.objects.get(id=pacote_id)
        cliente = Cliente.objects.get(id=cliente_id)
    except (Pacote.DoesNotExist, Cliente.DoesNotExist):
        return JsonResponse({'error': 'Pacote ou cliente não encontrado'}, status=404)
    
    # Verificar se cliente já está inscrito
    inscricao_existente = Inscricao.objects.filter(
        pacote=pacote,
        cliente=cliente
    ).first()
    
    if inscricao_existente:
        if inscricao_existente.status_pagamento == 'pago':
            return JsonResponse({
                'error': 'Cliente já está inscrito e pagou este pacote'
            }, status=400)
        else:
            inscricao = inscricao_existente
    else:
        # Criar nova inscrição
        inscricao = Inscricao.objects.create(
            pacote=pacote,
            cliente=cliente,
            status_inscricao='confirmada',
            status_pagamento='aguardando'
        )
    
    # Criar transação local
    try:
        transaction = PaymentService.criar_transacao(
            inscricao=inscricao,
            metodo_pagamento=metodo_pagamento,
            parcelas=parcelas
        )
    except Exception as e:
        logger.error(f"Erro ao criar transação: {e}")
        return JsonResponse({'error': 'Erro ao criar transação'}, status=500)
    
    # Criar preferência no Mercado Pago
    try:
        preferencia = PaymentService.criar_preferencia(
            inscricao=inscricao,
            metodo_pagamento=metodo_pagamento,
            parcelas=parcelas
        )
        
        # Atualizar transaction com ID do MP
        transaction.gateway_id = preferencia['id']
        transaction.save()
        
    except Exception as e:
        logger.error(f"Erro ao criar preferência MP: {e}")
        return JsonResponse({
            'error': f'Erro ao criar checkout: {str(e)}'
        }, status=500)
    
    # Retornar URL de checkout
    checkout_url = preferencia['sandbox_init_point'] if settings.DEBUG else preferencia['init_point']
    
    return JsonResponse({
        'success': True,
        'checkout_url': checkout_url,
        'inscricao_id': inscricao.id,
        'transaction_id': transaction.id
    })


@require_http_methods(["GET", "POST"])
def checkout_mercadopago(request, transaction_id):
    """
    Página de checkout (pode redirecionar direto para MP).
    """
    try:
        transaction = PaymentGatewayTransaction.objects.get(id=transaction_id)
    except PaymentGatewayTransaction.DoesNotExist:
        return JsonResponse({'error': 'Transação não encontrada'}, status=404)
    
    context = {
        'transaction': transaction,
        'mercadopago_public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
    }
    
    return render(request, 'passeios/checkout_mercadopago.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def webhook_mercadopago(request):
    """
    Webhook para receber notificações de pagamento do Mercado Pago.
    Mercado Pago fará POST aqui quando um pagamento é processado.
    """
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.warning("Webhook recebido com JSON inválido")
        return JsonResponse({'status': 'received'})
    
    logger.info(f"Webhook recebido: {data}")
    
    # Processar o webhook
    try:
        PaymentService.processar_webhook(data)
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {e}")
    
    # Sempre retornar 200 para evitar retentar
    return JsonResponse({'status': 'received'})


def sucesso_pagamento(request):
    """Página exibida após pagamento bem-sucedido."""
    return render(request, 'passeios/pagamento_sucesso.html')


def falha_pagamento(request):
    """Página exibida após falha no pagamento."""
    return render(request, 'passeios/pagamento_falha.html')


def pendente_pagamento(request):
    """Página exibida quando pagamento está pendente (ex: boleto)."""
    return render(request, 'passeios/pagamento_pendente.html')


# ============= APIS REST =============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_listar_inscricoes(request):
    """
    GET /api/inscricoes/ - Lista todas as inscrições do operador
    """
    inscricoes = Inscricao.objects.select_related('cliente', 'pacote__passeio')
    
    # Filtrar por status
    status_pagamento = request.query_params.get('status_pagamento')
    if status_pagamento:
        inscricoes = inscricoes.filter(status_pagamento=status_pagamento)
    
    # Paginação
    paginator = Paginator(inscricoes, 20)
    page = request.query_params.get('page', 1)
    inscricoes_page = paginator.get_page(page)
    
    serialized = [
        {
            'id': i.id,
            'cliente': i.cliente.nome,
            'pacote': i.pacote.titulo,
            'valor': float(i.pacote.preco),
            'status_pagamento': i.status_pagamento,
            'data_inscricao': i.data_inscricao.isoformat(),
            'valor_pago': float(i.valor_pago),
            'saldo_devedor': float(i.saldo_devedor),
        }
        for i in inscricoes_page
    ]
    
    return Response({
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'inscricoes': serialized
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_detalhes_inscricao(request, inscricao_id):
    """
    GET /api/inscricoes/{id}/ - Detalhes de uma inscrição
    """
    try:
        inscricao = Inscricao.objects.select_related('cliente', 'pacote__passeio').get(id=inscricao_id)
    except Inscricao.DoesNotExist:
        return Response({'error': 'Inscrição não encontrada'}, status=rest_status.HTTP_404_NOT_FOUND)
    
    return Response({
        'id': inscricao.id,
        'cliente': {
            'id': inscricao.cliente.id,
            'nome': inscricao.cliente.nome,
            'cpf': inscricao.cliente.cpf,
            'email': inscricao.cliente.email,
            'telefone': str(inscricao.cliente.telefone) if inscricao.cliente.telefone else '',
        },
        'pacote': {
            'id': inscricao.pacote.id,
            'titulo': inscricao.pacote.titulo,
            'passeio': inscricao.pacote.passeio.titulo,
            'preco': float(inscricao.pacote.preco),
        },
        'valor_pago': float(inscricao.valor_pago),
        'saldo_devedor': float(inscricao.saldo_devedor),
        'status_pagamento': inscricao.status_pagamento,
        'status_inscricao': inscricao.status_inscricao,
        'data_inscricao': inscricao.data_inscricao.isoformat(),
        'pagamentos': [
            {
                'id': p.id,
                'valor': float(p.valor),
                'metodo': p.metodo,
                'data': p.data_pagamento.isoformat(),
            }
            for p in inscricao.pagamentos.all()
        ]
    })
