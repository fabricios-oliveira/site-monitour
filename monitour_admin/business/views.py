from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import FileResponse, Http404
from django.views.static import serve
from datetime import timedelta
from django.db.models import Count, F
import json
import os
import mimetypes

from cadastros.models import Cliente, Fornecedor
from passeios.models import Passeio, Inscricao, VeiculoPasseio

@staff_member_required
def dashboard_view(request):
    """
    Renderiza a página inicial do admin (dashboard) com dados personalizados.
    """
    # --- Coleta de Dados para a Dashboard ---
    hoje = timezone.now().date()
    proximos_passeios = Passeio.objects.filter(
        data_ida__gte=hoje,
        status__in=['agendado', 'confirmado']
    ).annotate(
        num_inscricoes=Count('pacotes__inscricoes', distinct=True)
    ).select_related('tipo_veiculo').order_by('data_ida')

    data_limite = hoje - timedelta(days=7)
    inscricoes_recentes = Inscricao.objects.filter(data_inscricao__gte=data_limite).count()

    # --- Dados para o Gráfico de Lotação ---
    chart_labels = [p.titulo for p in proximos_passeios[:5]]
    chart_data_inscricoes = [p.num_inscricoes for p in proximos_passeios[:5]]
    chart_data_capacidade = [p.tipo_veiculo.capacidade if p.tipo_veiculo else 0 for p in proximos_passeios[:5]]

    chart_data = {
        "labels": chart_labels,
        "datasets": [
            {
                "label": 'Inscrições',
                "data": chart_data_inscricoes,
                "backgroundColor": 'rgba(40, 167, 69, 0.7)',
                "borderColor": 'rgba(40, 167, 69, 1)',
                "borderWidth": 1
            },
            {
                "label": 'Capacidade',
                "data": chart_data_capacidade,
                "backgroundColor": 'rgba(200, 200, 200, 0.5)',
                "borderColor": 'rgba(150, 150, 150, 1)',
                "borderWidth": 1
            }
        ]
    }

    # --- Passeios que Requerem Atenção ---
    passeios_em_risco = proximos_passeios.filter(
        lotacao_minima_desejada__gt=0,
        num_inscricoes__lt=F('lotacao_minima_desejada')
    )

    context = {
    **admin.site.each_context(request),
        'title': 'Dashboard Principal',
        'total_fornecedores': Fornecedor.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_passeios_agendados': Passeio.objects.filter(status__in=['agendado', 'confirmado']).count(),
        'inscricoes_recentes': inscricoes_recentes,
        'proximos_passeios': proximos_passeios[:5], # Limita a 5 na tabela
        'passeios_em_risco': passeios_em_risco,
        'chart_data_json': json.dumps(chart_data),
    }

    return TemplateResponse(request, "core/dashboard.html", context)


@staff_member_required
def documentation_view(request, filename='index.html'):
    """
    Serve arquivos da documentação HTML de forma segura.
    Permite acesso apenas a arquivos da pasta docs_html/
    """
    # Caminho base da documentação
    docs_base = os.path.dirname(os.path.dirname(__file__))
    docs_root = os.path.join(docs_base, 'docs_html')
    
    # Sanitizar filename (remove path traversal attempts)
    filename = os.path.basename(filename)  # Remove any path separators
    
    # Caminho completo do arquivo
    file_path = os.path.join(docs_root, filename)
    
    # Verificar se arquivo existe
    if not os.path.exists(file_path):
        raise Http404(f"Documentação não encontrada: {filename}")
    
    # Verificar se é um arquivo (não diretório)
    if not os.path.isfile(file_path):
        raise Http404("Acesso inválido")
    
    # Servir o arquivo
    mime_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(open(file_path, 'rb'), content_type=mime_type or 'text/html')