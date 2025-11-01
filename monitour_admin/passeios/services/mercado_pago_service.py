"""
Serviço de integração com Mercado Pago.
Responsável por criar preferências de pagamento e processar webhooks.
"""
import os
import requests
from decimal import Decimal
from django.conf import settings
from django.utils.timezone import now
from django.db import models
from passeios.models import PaymentGatewayTransaction, Inscricao, Pagamento

# Desabilita warning de SSL para desenvolvimento
if settings.DEBUG:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # Desabilita SSL verification no requests em desenvolvimento
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()


class MercadoPagoService:
    """
    Integração com Mercado Pago para criar links de pagamento e processar webhooks.
    """
    
    BASE_URL = "https://api.mercadopago.com"
    SANDBOX_URL = "https://sandbox.mercadopago.com"
    
    def __init__(self):
        """Inicializa o serviço com credenciais."""
        self.access_token = settings.MERCADO_PAGO_ACCESS_TOKEN
        self.public_key = settings.MERCADO_PAGO_PUBLIC_KEY
        
        # Use sandbox se em desenvolvimento
        self.is_sandbox = settings.DEBUG or not self.access_token
        self.base_url = self.SANDBOX_URL if self.is_sandbox else self.BASE_URL
    
    def criar_preferencia_pagamento(self, inscricao_id, cliente_nome, cliente_email, valor, metodo=''):
        """
        Cria uma preferência de pagamento no Mercado Pago.
        Em desenvolvimento, retorna um mock se não houver credenciais reais.
        
        Args:
            inscricao_id: ID da inscrição
            cliente_nome: Nome do cliente
            cliente_email: Email do cliente
            valor: Valor a pagar em BRL
            metodo: Método de pagamento opcional
        
        Returns:
            {
                'sucesso': True,
                'link_pagamento': 'https://www.mercadopago.com/checkout/v1/...',
                'preferencia_id': '123456789'
            }
        """
        try:
            inscricao = Inscricao.objects.select_related('pacote', 'pacote__passeio').get(id=inscricao_id)
            
            # Em desenvolvimento, se não houver credencial real, retorna mock
            if settings.DEBUG and self.access_token in ["APP_USR-SANDBOX-TOKEN-AQUI", "APP_USR-SANDBOX-TOKEN"]:
                # Mock response para desenvolvimento
                return {
                    'sucesso': True,
                    'link_pagamento': f"https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=mock_{inscricao_id}_{int(now().timestamp())}",
                    'preferencia_id': f"mock_{inscricao_id}",
                    'sandbox': True,
                    'nota': 'Em desenvolvimento: usando link mockado'
                }
            
            # Monta o payload para Mercado Pago
            preference_data = {
                "items": [
                    {
                        "title": inscricao.pacote.passeio.titulo,
                        "description": inscricao.pacote.titulo,
                        "picture_url": "",  # Opcional: URL da imagem
                        "category_id": "viagem",
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": float(valor),
                    }
                ],
                "payer": {
                    "email": cliente_email,
                    "name": cliente_nome,
                },
                "external_reference": f"inscricao_{inscricao_id}",
                "payment_methods": {
                    "excluded_payment_methods": [],
                    "excluded_payment_types": [],
                    "installments": 12,
                },
                "back_urls": {
                    "success": settings.MERCADO_PAGO_SUCCESS_URL,
                    "pending": settings.MERCADO_PAGO_PENDING_URL,
                    "failure": settings.MERCADO_PAGO_FAILURE_URL,
                },
                "notify_url": settings.MERCADO_PAGO_WEBHOOK_URL,
                "auto_return": "approved",
            }
            
            # Faz requisição para criar preferência
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }
            
            url = f"{self.base_url}/checkout/preferences"
            
            try:
                response = requests.post(
                    url, 
                    json=preference_data, 
                    headers=headers, 
                    timeout=10, 
                    verify=not settings.DEBUG
                )
                
                if response.status_code not in [200, 201]:
                    return {
                        'sucesso': False,
                        'erro': f"Erro ao criar preferência: {response.status_code} - {response.text}"
                    }
                
                data = response.json()
                
                return {
                    'sucesso': True,
                    'link_pagamento': data.get('init_point'),  # URL de checkout
                    'preferencia_id': data.get('id'),
                    'sandbox': data.get('sandbox_init_point') if self.is_sandbox else None,
                }
            except requests.exceptions.RequestException as req_error:
                # Se falhar a requisição em desenvolvimento, retorna mock
                if settings.DEBUG:
                    return {
                        'sucesso': True,
                        'link_pagamento': f"https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=dev_{inscricao_id}_{int(now().timestamp())}",
                        'preferencia_id': f"dev_{inscricao_id}",
                        'sandbox': True,
                        'nota': 'Em desenvolvimento: usando link mockado devido a erro SSL'
                    }
                else:
                    return {'sucesso': False, 'erro': f"Erro ao conectar com Mercado Pago: {str(req_error)}"}
        
        except Inscricao.DoesNotExist:
            return {'sucesso': False, 'erro': f'Inscrição {inscricao_id} não encontrada'}
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
    
    def processar_webhook(self, data):
        """
        Processa notificação de pagamento do Mercado Pago.
        
        Args:
            data: Dados recebidos via webhook
        
        Returns:
            {'sucesso': True/False, 'mensagem': '...'}
        """
        try:
            # Mercado Pago envia: {"data": {"id": "..."}, "type": "payment"}
            tipo = data.get('type')
            payload = data.get('data', {})
            
            if tipo != 'payment':
                return {'sucesso': True, 'mensagem': 'Webhook recebido mas não é pagamento'}
            
            payment_id = payload.get('id')
            if not payment_id:
                return {'sucesso': False, 'erro': 'Payment ID não encontrado no webhook'}
            
            # Busca detalhes do pagamento no Mercado Pago
            detalhes = self._buscar_detalhes_pagamento(payment_id)
            if not detalhes:
                return {'sucesso': False, 'erro': 'Não foi possível buscar detalhes do pagamento'}
            
            # Extrai informações
            status_mp = detalhes.get('status')
            valor = Decimal(str(detalhes.get('transaction_amount', 0)))
            external_reference = detalhes.get('external_reference', '')
            metodo = detalhes.get('payment_method_id', '')
            
            # Extrai inscricao_id do external_reference
            # Formato: "inscricao_123"
            if not external_reference.startswith('inscricao_'):
                return {'sucesso': True, 'mensagem': 'External reference não é uma inscricao'}
            
            inscricao_id = int(external_reference.split('_')[1])
            
            # Busca ou cria a transação no gateway
            gateway_tx, criada = PaymentGatewayTransaction.objects.get_or_create(
                gateway='mercadopago',
                gateway_id=str(payment_id),
                defaults={
                    'valor': valor,
                    'metodo_pagamento': metodo,
                    'status': 'pendente',
                }
            )
            
            # Atualiza status conforme Mercado Pago
            if status_mp == 'approved':
                gateway_tx.status = 'aprovado'
                gateway_tx.webhook_confirmado = True
                
                # Cria Pagamento local se não existir
                try:
                    inscricao = Inscricao.objects.get(id=inscricao_id)
                    if not gateway_tx.pagamento:
                        pagamento = Pagamento.objects.create(
                            inscricao=inscricao,
                            valor=valor,
                            metodo='mercadopago'
                        )
                        gateway_tx.pagamento = pagamento
                    
                    # Atualiza status de pagamento da inscrição
                    valor_pago = inscricao.pagamentos.aggregate(models.Sum('valor'))['valor__sum'] or Decimal('0')
                    if valor_pago >= inscricao.pacote.preco:
                        inscricao.status_pagamento = 'pago'
                    elif valor_pago > 0:
                        inscricao.status_pagamento = 'parcial'
                    inscricao.save()
                
                except Inscricao.DoesNotExist:
                    pass
            
            elif status_mp == 'pending':
                gateway_tx.status = 'processando'
            elif status_mp == 'rejected':
                gateway_tx.status = 'rejeitado'
            elif status_mp == 'cancelled':
                gateway_tx.status = 'cancelado'
            
            gateway_tx.save()
            
            return {
                'sucesso': True,
                'mensagem': f'Pagamento {payment_id} processado com status {status_mp}',
                'transaction_id': gateway_tx.id,
            }
        
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
    
    def _buscar_detalhes_pagamento(self, payment_id):
        """
        Busca detalhes de um pagamento no Mercado Pago.
        
        Args:
            payment_id: ID do pagamento no Mercado Pago
        
        Returns:
            dict com dados do pagamento ou None se erro
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
            }
            
            url = f"{self.base_url}/v1/payments/{payment_id}"
            response = requests.get(url, headers=headers, timeout=10, verify=not settings.DEBUG)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Erro ao buscar pagamento {payment_id}: {e}")
            return None
