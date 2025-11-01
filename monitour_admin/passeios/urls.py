from django.urls import path
from . import views
from . import views_vendas

app_name = 'passeios'

urlpatterns = [
    path('relatorio/<int:passeio_id>/', views.gerar_relatorio_passageiros, name='relatorio_passageiros'),
    path('mapa-assentos/<int:veiculo_passeio_id>/', views.mapa_assentos_view, name='mapa_assentos'),
    path('salvar-assento/', views.salvar_assento_view, name='salvar_assento'),
    path('relatorio-financeiro/<int:passeio_id>/', views.relatorio_financeiro_view, name='relatorio_financeiro'),
    path('relatorio-cotacoes/<int:passeio_id>/', views.relatorio_cotacoes_view, name='relatorio_cotacoes'),
    path('relatorio-cotacoes/pdf/<int:passeio_id>/', views.gerar_relatorio_cotacoes_pdf, name='relatorio_cotacoes_pdf'),
    path('relatorio-contas-a-pagar/', views.relatorio_contas_a_pagar_view, name='relatorio_contas_a_pagar'),
    
    # === NOVAS URLS PARA VENDAS E PAGAMENTOS ===
    path('venda/', views_vendas.tela_venda_principal, name='venda_principal'),
    path('venda/buscar-cliente/', views_vendas.buscar_cliente, name='buscar_cliente'),
    path('venda/processar/', views_vendas.processar_pagamento_inscricao, name='processar_pagamento'),
    path('venda/checkout/<int:transaction_id>/', views_vendas.checkout_mercadopago, name='checkout'),
    path('venda/sucesso/', views_vendas.sucesso_pagamento, name='pagamento_sucesso'),
    path('venda/falha/', views_vendas.falha_pagamento, name='pagamento_falha'),
    path('venda/pendente/', views_vendas.pendente_pagamento, name='pagamento_pendente'),
    
    # === APIS REST ===
    path('api/inscricoes/', views_vendas.api_listar_inscricoes, name='api_inscricoes'),
    path('api/inscricoes/<int:inscricao_id>/', views_vendas.api_detalhes_inscricao, name='api_inscricao_detalhes'),
    path('api/webhook/mercadopago/', views_vendas.webhook_mercadopago, name='webhook_mp'),
]