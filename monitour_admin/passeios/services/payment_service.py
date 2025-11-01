"""
Service para gerenciar integrações com gateways de pagamento (Mercado Pago).
Centraliza toda a lógica de pagamento para simplificar as views.
"""

from decimal import Decimal
from django.conf import settings
from passeios.models import Pagamento, PaymentGatewayTransaction, Inscricao
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    import mercadopago
except ImportError:
    logger.warning("Mercado Pago SDK não instalado. Execute: pip install mercado-pago-sdk")


class MercadoPagoService:
    """
    Serviço para integração com Mercado Pago.
    """
    
    def __init__(self):
        """Inicializa o cliente do Mercado Pago com a chave de acesso."""
        self.access_token = settings.MERCADO_PAGO_ACCESS_TOKEN
        self.public_key = settings.MERCADO_PAGO_PUBLIC_KEY
        try:
            self.sdk = mercadopago.SDK(self.access_token)
        except NameError:
            logger.error("Mercado Pago SDK não carregado. Instale: pip install mercado-pago-sdk")
            raise
    
    def criar_preferencia_pagamento(self, inscricao, metodo_pagamento, parcelas=1):
        """
        Cria uma preferência de pagamento no Mercado Pago.
        
        Args:
            inscricao (Inscricao): Inscrição (venda) que será paga
            metodo_pagamento (str): 'cartao_credito', 'cartao_debito' ou 'pix'
            parcelas (int): Número de parcelas (1-12 para cartão, 1 para outros)
        
        Returns:
            dict: {
                'id': preferencia_id,
                'init_point': url_de_checkout,
                'sandbox_init_point': url_de_checkout_teste
            }
        """
        
        # Validar parcelas
        if metodo_pagamento != 'cartao_credito' and parcelas != 1:
            logger.warning(f"Parcelas requeridas para {metodo_pagamento}, usando 1x")
            parcelas = 1
        
        # Preparar dados da preferência
        preference_data = {
            "items": [
                {
                    "title": f"{inscricao.pacote.passeio.titulo}",
                    "description": f"Passeio de {inscricao.pacote.data_ida.strftime('%d/%m/%Y')}",
                    "picture_url": "https://www.mercadopago.com/img/home/logoMP3.gif",
                    "category_id": "art",
                    "quantity": 1,
                    "unit_price": float(inscricao.pacote.preco)
                }
            ],
            "payer": {
                "name": inscricao.cliente.nome.split()[0],  # Primeiro nome
                "surname": " ".join(inscricao.cliente.nome.split()[1:]),  # Resto do nome
                "email": inscricao.cliente.email,
                "phone": {
                    "area_code": "11",  # TODO: extrair do telefone
                    "number": "1234567890"  # TODO: extrair do telefone
                },
                "address": {
                    "street_name": inscricao.cliente.endereco or "Rua não informada",
                    "street_number": inscricao.cliente.numero or "0",
                    "zip_code": inscricao.cliente.cep or "00000000"
                }
            },
            "payment_methods": {
                "excluded_payment_methods": [],
                "excluded_payment_types": [],
                "installments": parcelas if metodo_pagamento == 'cartao_credito' else 1
            },
            "back_urls": {
                "success": f"{settings.SITE_URL}/passeios/venda/sucesso/",
                "failure": f"{settings.SITE_URL}/passeios/venda/falha/",
                "pending": f"{settings.SITE_URL}/passeios/venda/pendente/"
            },
            "auto_return": "approved",
            "external_reference": f"inscricao_{inscricao.id}",
            "notification_url": f"{settings.SITE_URL}/api/webhook/mercadopago/",
        }
        
        # Criar preferência
        preference_response = self.sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            return {
                'id': preference_response["response"]["id"],
                'init_point': preference_response["response"]["init_point"],
                'sandbox_init_point': preference_response["response"]["sandbox_init_point"]
            }
        else:
            logger.error(f"Erro ao criar preferência: {preference_response}")
            raise Exception(f"Erro ao criar preferência no Mercado Pago")
    
    def processar_webhook(self, data):
        """
        Processa notificação de webhook do Mercado Pago.
        
        Args:
            data (dict): Dados recebidos do webhook
        
        Returns:
            bool: True se processado com sucesso
        """
        
        # Validar tipo de notificação
        if data.get('type') != 'payment':
            logger.info(f"Webhook ignorado, tipo: {data.get('type')}")
            return False
        
        # Obter ID da transação
        payment_id = data.get('data', {}).get('id')
        if not payment_id:
            logger.error("ID de pagamento não encontrado no webhook")
            return False
        
        # Buscar transação existente
        try:
            transaction = PaymentGatewayTransaction.objects.get(gateway_id=payment_id)
        except PaymentGatewayTransaction.DoesNotExist:
            logger.error(f"Transação não encontrada: {payment_id}")
            return False
        
        # Buscar detalhes do pagamento no MP
        payment_response = self.sdk.payment().get(payment_id)
        payment_info = payment_response["response"]
        
        # Atualizar status
        if payment_info["status"] == "approved":
            transaction.status = 'aprovado'
            transaction.confirmada_em = datetime.now()
            
            # Atualizar pagamento relacionado
            if transaction.pagamento:
                transaction.pagamento.data_pagamento = datetime.now()
                transaction.pagamento.save()
                
                # Atualizar inscrição se todos os pagamentos estão feitos
                inscricao = transaction.pagamento.inscricao
                if inscricao.valor_pago >= inscricao.pacote.preco:
                    inscricao.status_pagamento = 'pago'
                    inscricao.save()
        
        elif payment_info["status"] == "pending":
            transaction.status = 'processando'
        
        elif payment_info["status"] == "rejected":
            transaction.status = 'rejeitado'
        
        elif payment_info["status"] == "cancelled":
            transaction.status = 'cancelado'
        
        transaction.webhook_confirmado = True
        transaction.save()
        
        logger.info(f"Webhook processado: {payment_id} -> {transaction.status}")
        return True
    
    def criar_transacao_local(self, inscricao, metodo_pagamento, parcelas=1, gateway_id=None):
        """
        Cria registro local da transação antes de redirecionar para checkout.
        
        Args:
            inscricao (Inscricao): Inscrição a ser paga
            metodo_pagamento (str): Método de pagamento
            parcelas (int): Número de parcelas
            gateway_id (str): ID da transação no gateway (se já criada)
        
        Returns:
            PaymentGatewayTransaction: Transação criada
        """
        
        # Criar pagamento local
        pagamento = Pagamento.objects.create(
            inscricao=inscricao,
            valor=inscricao.pacote.preco,
            metodo=metodo_pagamento
        )
        
        # Criar transação no gateway
        transaction = PaymentGatewayTransaction.objects.create(
            gateway='mercadopago',
            gateway_id=gateway_id or f"temp_{inscricao.id}_{datetime.now().timestamp()}",
            pagamento=pagamento,
            status='pendente',
            valor=inscricao.pacote.preco,
            metodo_pagamento=metodo_pagamento,
            parcelas=parcelas
        )
        
        return transaction
    
    def cancelar_pagamento(self, transaction_id):
        """
        Cancela uma transação no Mercado Pago.
        
        Args:
            transaction_id (str): ID da transação no MP
        
        Returns:
            bool: True se cancelado com sucesso
        """
        try:
            response = self.sdk.payment().update(transaction_id, {"status": "cancelled"})
            if response["status"] == 200:
                # Atualizar transação local
                transaction = PaymentGatewayTransaction.objects.get(gateway_id=transaction_id)
                transaction.status = 'cancelado'
                transaction.save()
                return True
        except Exception as e:
            logger.error(f"Erro ao cancelar pagamento: {e}")
        
        return False


class PaymentService:
    """
    Serviço genérico de pagamento que abstrai diferentes gateways.
    """
    
    _mp_service = None
    
    @classmethod
    def get_mp_service(cls):
        """Obtém instância do serviço do Mercado Pago (singleton)."""
        if cls._mp_service is None:
            cls._mp_service = MercadoPagoService()
        return cls._mp_service
    
    @staticmethod
    def criar_preferencia(inscricao, metodo_pagamento, parcelas=1):
        """Wrapper para criar preferência de pagamento."""
        service = PaymentService.get_mp_service()
        return service.criar_preferencia_pagamento(inscricao, metodo_pagamento, parcelas)
    
    @staticmethod
    def processar_webhook(data):
        """Wrapper para processar webhook."""
        service = PaymentService.get_mp_service()
        return service.processar_webhook(data)
    
    @staticmethod
    def criar_transacao(inscricao, metodo_pagamento, parcelas=1):
        """Wrapper para criar transação local."""
        service = PaymentService.get_mp_service()
        return service.criar_transacao_local(inscricao, metodo_pagamento, parcelas)


# Exportar
__all__ = ['PaymentService', 'MercadoPagoService']
