from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid
from .models import Passeio, VeiculoPasseio, Inscricao, Pagamento

@receiver(post_save, sender=Passeio)
def criar_ou_atualizar_veiculo_passeio(sender, instance, created, **kwargs):
    """
    Garante que um VeiculoPasseio seja criado ou atualizado sempre que um
    Passeio com um tipo_veiculo definido for salvo.
    """
    if instance.tipo_veiculo:
        # Tenta encontrar um VeiculoPasseio existente ou cria um novo.
        # Isso garante que haja apenas um veículo principal por passeio.
        veiculo, veiculo_created = VeiculoPasseio.objects.get_or_create(
            passeio=instance,
            defaults={'tipo_veiculo': instance.tipo_veiculo, 'identificacao': 'Veículo Principal'}
        )
        # Se o tipo de veículo foi alterado em um passeio existente, atualiza o veículo.
        if not veiculo_created and veiculo.tipo_veiculo != instance.tipo_veiculo:
            veiculo.tipo_veiculo = instance.tipo_veiculo
            veiculo.save()

@receiver(post_save, sender=Inscricao)
def verificar_ponto_de_equilibrio(sender, instance, created, **kwargs):
    """
    Após cada nova inscrição, verifica se o passeio atingiu o ponto de equilíbrio.
    Se sim, e se o alerta ainda não foi enviado, envia um e-mail.
    """
    # Apenas executa para novas inscrições
    if not created:
        return

    passeio = instance.pacote.passeio

    # Se o alerta já foi enviado, não faz nada
    if passeio.alerta_equilibrio_enviado:
        return

    # Recalcula as métricas necessárias
    total_inscricoes = Inscricao.objects.filter(pacote__passeio=passeio).count()
    custo_total = passeio.custo_total_previsto
    preco_base_pacote = passeio.pacotes.first().preco if passeio.pacotes.exists() else Decimal('0.00')

    if preco_base_pacote > 0:
        lotacao_break_even = (custo_total / preco_base_pacote)

        # Verifica se atingiu ou ultrapassou o ponto de equilíbrio
        if total_inscricoes >= lotacao_break_even:
            # Envia o e-mail (com tratamento de erro para desenvolvimento)
            try:
                subject = f"Ponto de Equilibrio Atingido: {passeio.titulo}"
                message = f"Olá!\n\nO passeio '{passeio.titulo}' acaba de atingir seu ponto de equilibrio com {total_inscricoes} inscricoes.\n\nA partir de agora, cada nova inscricao representa lucro!\n\nParabens!"
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER])
            except Exception as e:
                # Em desenvolvimento, falha silenciosa no envio de email
                if settings.DEBUG:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Falha ao enviar email de equilibrio: {str(e)}")
                else:
                    raise

            # Marca o alerta como enviado para não repetir
            passeio.alerta_equilibrio_enviado = True
            passeio.save(update_fields=['alerta_equilibrio_enviado'])

@receiver(post_save, sender=Inscricao)
def gerar_voucher_inscricao(sender, instance, created, **kwargs):
    """Gera um voucher único para novas inscrições."""
    if created and not instance.voucher:
        # Gera um código curto e único a partir do UUID
        instance.voucher = str(uuid.uuid4()).split('-')[0].upper()
        instance.save(update_fields=['voucher'])

@receiver([post_save, post_delete], sender=Pagamento)
def atualizar_status_pagamento_inscricao(sender, instance, **kwargs):
    """
    Após salvar ou deletar um pagamento, recalcula o total pago e atualiza
    o status da inscrição correspondente.
    """
    inscricao = instance.inscricao
    
    # Recalcula o valor pago diretamente do banco de dados para garantir precisão
    total_pago = inscricao.pagamentos.aggregate(total=models.Sum('valor'))['total'] or Decimal('0.00')

    if total_pago >= inscricao.pacote.preco:
        inscricao.status_pagamento = 'pago'
    elif total_pago > Decimal('0.00'):
        inscricao.status_pagamento = 'parcial'
    else:
        inscricao.status_pagamento = 'aguardando'
    
    inscricao.save(update_fields=['status_pagamento'])