"""
Signals para o app cadastros.
Gerencia operações automáticas como criação de matrículas.
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Cliente, MatriculaCliente, limpar_cpf


@receiver(post_save, sender=Cliente)
def criar_matricula_cliente(sender, instance, created, **kwargs):
    """
    Signal que cria automaticamente uma MatriculaCliente quando um Cliente é criado.
    
    A matrícula será vinculada ao CPF do cliente com um ID aleatório de 6 dígitos
    para preservar privacidade (não mostra quantos clientes estão cadastrados).
    """
    if created and not instance.matricula:
        # Cliente foi criado e não tem matrícula vinculada
        # Limpa o CPF (remove formatação)
        cpf_limpo = limpar_cpf(instance.cpf)
        
        try:
            # Tenta recuperar matrícula existente para esse CPF
            matricula, created_matricula = MatriculaCliente.objects.get_or_create(
                cpf=cpf_limpo
            )
            instance.matricula = matricula
            # Usa update() para evitar chamar o signal novamente (evita loop infinito)
            Cliente.objects.filter(pk=instance.pk).update(matricula=matricula)
        except Exception as e:
            # Log do erro (você pode adicionar logging aqui)
            print(f"Erro ao criar matrícula para cliente {instance.nome}: {str(e)}")


@receiver(pre_delete, sender=MatriculaCliente)
def prevenir_delecao_matricula(sender, instance, **kwargs):
    """
    Impede a exclusão de matrículas que estão vinculadas a clientes.
    """
    if instance.cliente_set.exists():
        raise Exception(
            f"Não é possível deletar a matrícula {instance.id}. "
            f"Existem clientes associados a esta matrícula."
        )
