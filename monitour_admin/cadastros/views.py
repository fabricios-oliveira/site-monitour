from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Sum
from .models import Cliente

# Create your views here.

@staff_member_required
def relatorio_clientes_chave(request):
    """
    Gera e exibe um relatório de clientes chave, ordenados por
    valor gasto e número de viagens.
    """
    # Anota (adiciona) em cada cliente o total de viagens e o gasto total
    clientes_com_dados = Cliente.objects.annotate(
        num_viagens=Count('inscricoes', distinct=True),
        valor_total_gasto=Sum('inscricoes__pagamentos__valor')
    ).filter(valor_total_gasto__gt=0) # Filtra para mostrar apenas clientes que já compraram algo

    # Ordena por quem gastou mais
    clientes_por_gasto = clientes_com_dados.order_by('-valor_total_gasto')[:10]

    # Ordena por quem viajou mais
    clientes_por_viagem = clientes_com_dados.order_by('-num_viagens')[:10]

    context = {
        'title': 'Relatório de Clientes Chave',
        'clientes_por_gasto': clientes_por_gasto,
        'clientes_por_viagem': clientes_por_viagem,
    }
    return render(request, 'cadastros/relatorio_clientes_chave.html', context)

@staff_member_required
def verificar_cpf(request):
    """
    View para verificar via AJAX se um CPF já existe no banco de dados.
    """
    cpf = request.GET.get('cpf', None)
    cliente_id = request.GET.get('cliente_id', None)

    if not cpf:
        return JsonResponse({'error': 'CPF não fornecido.'}, status=400)

    # Remove a máscara para buscar no banco
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    query = Cliente.objects.filter(cpf__exact=cpf)
    if cliente_id and cliente_id.isdigit():
        query = query.exclude(pk=cliente_id) # Exclui o próprio cliente da busca

    data = {'exists': query.exists()}
    return JsonResponse(data)
