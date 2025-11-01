from django.core.management.base import BaseCommand
from cadastros.models import Cliente, TipoVeiculo, Fornecedor
from passeios.models import Passeio, Pacote
from financas.models import Conta, Categoria
from business.models import AcaoRapida
from datetime import datetime, date
from decimal import Decimal

class Command(BaseCommand):
    help = 'Cria dados de exemplo para demonstrar o sistema MONITOUR integrado'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando criação de dados de exemplo...'))
        
        # Clientes
        cliente1 = Cliente.objects.get_or_create(
            nome='Maria Silva Santos',
            cpf='12345678901',
            defaults={
                'email': 'maria.silva@email.com',
                'telefone': '+5511987654321',
                'data_nascimento': date(1985, 3, 15),
                'genero': 'F',
                'endereco': 'Rua das Flores, 123',
                'cidade': 'São Paulo',
                'estado': 'SP',
                'cep': '01234-567'
            }
        )[0]
        
        cliente2 = Cliente.objects.get_or_create(
            nome='João Pedro Costa',
            cpf='98765432109',
            defaults={
                'email': 'joao.costa@email.com',
                'telefone': '+5511123456789',
                'data_nascimento': date(1990, 7, 22),
                'genero': 'M',
                'endereco': 'Av. Principal, 456',
                'cidade': 'Rio de Janeiro',
                'estado': 'RJ',
                'cep': '20000-000'
            }
        )[0]
        
        # Tipos de Veículo
        tipo_onibus = TipoVeiculo.objects.get_or_create(
            nome='Ônibus Executivo',
            defaults={
                'capacidade': 48,
                'custo_base_transporte': Decimal('500.00'),
                'descricao': 'Ônibus executivo com ar condicionado e poltronas reclináveis'
            }
        )[0]
        
        tipo_van = TipoVeiculo.objects.get_or_create(
            nome='Van Premium',
            defaults={
                'capacidade': 15,
                'custo_base_transporte': Decimal('200.00'),
                'descricao': 'Van premium para grupos menores'
            }
        )[0]
        
        # Fornecedores
        fornecedor_hotel = Fornecedor.objects.get_or_create(
            nome='Hotel Fazenda Paraíso',
            cnpj='12.345.678/0001-90',
            defaults={
                'tipo': 'hotel',
                'email': 'contato@hotelfazendaparaiso.com.br',
                'telefone': '+551540001234',
                'endereco': 'Estrada Rural, Km 15',
                'cidade': 'Campos do Jordão',
                'estado': 'SP'
            }
        )[0]
        
        # Passeios
        passeio1 = Passeio.objects.get_or_create(
            titulo='Campos do Jordão - Final de Semana',
            defaults={
                'descricao': 'Passeio para Campos do Jordão com hospedagem em hotel fazenda, refeições inclusas e passeios locais.',
                'data_inicio': date(2025, 12, 14),  # Próximo final de semana
                'data_fim': date(2025, 12, 15),
                'tipo_veiculo': tipo_onibus,
                'preco_individual': Decimal('350.00'),
                'local_saida': 'Terminal Tietê - São Paulo',
                'local_destino': 'Campos do Jordão - SP',
                'status': 'agendado',
                'observacoes': 'Levar agasalho - temperaturas baixas esperadas'
            }
        )[0]
        
        passeio2 = Passeio.objects.get_or_create(
            titulo='City Tour São Paulo - 1 Dia',
            defaults={
                'descricao': 'Tour pelos principais pontos turísticos de São Paulo: Centro Histórico, Mercado Municipal, Beco do Batman e muito mais.',
                'data_inicio': date(2025, 11, 10),
                'data_fim': date(2025, 11, 10),
                'tipo_veiculo': tipo_van,
                'preco_individual': Decimal('120.00'),
                'local_saida': 'Praça da República - São Paulo',
                'local_destino': 'Diversos pontos de SP',
                'status': 'confirmado',
                'observacoes': 'Almoço no Mercado Municipal incluso'
            }
        )[0]
        
        # Pacotes
        pacote1 = Pacote.objects.get_or_create(
            nome='Campos do Jordão Completo',
            defaults={
                'passeio': passeio1,
                'preco': Decimal('350.00'),
                'descricao': 'Pacote completo para Campos do Jordão',
                'inclui_hospedagem': True,
                'inclui_alimentacao': True,
                'inclui_transporte': True
            }
        )[0]
        
        # Contas e Categorias Financeiras
        conta_caixa = Conta.objects.get_or_create(
            nome='Caixa Principal',
            defaults={
                'tipo': 'corrente',
                'saldo_atual': Decimal('10000.00'),
                'ativa': True
            }
        )[0]
        
        categoria_receita = Categoria.objects.get_or_create(
            nome='Vendas de Pacotes',
            defaults={
                'tipo': 'receita',
                'cor': '#28a745',
                'descricao': 'Receitas provenientes da venda de pacotes turísticos'
            }
        )[0]
        
        categoria_despesa = Categoria.objects.get_or_create(
            nome='Combustível',
            defaults={
                'tipo': 'despesa',
                'cor': '#dc3545',
                'descricao': 'Gastos com combustível dos veículos'
            }
        )[0]
        
        # Ações Rápidas
        acao1 = AcaoRapida.objects.get_or_create(
            titulo='Relatório de Vendas',
            defaults={
                'descricao': 'Gerar relatório de vendas do mês atual',
                'url': '/admin/relatorios/vendas/',
                'icone': 'fa-chart-bar',
                'cor': '#007bff',
                'ativo': True
            }
        )[0]
        
        acao2 = AcaoRapida.objects.get_or_create(
            titulo='Cadastrar Cliente',
            defaults={
                'descricao': 'Cadastro rápido de novo cliente',
                'url': '/admin/cadastros/cliente/add/',
                'icone': 'fa-user-plus',
                'cor': '#28a745',
                'ativo': True
            }
        )[0]
        
        self.stdout.write(
            self.style.SUCCESS('Dados de exemplo criados com sucesso!')
        )
        self.stdout.write(f'• {Cliente.objects.count()} clientes')
        self.stdout.write(f'• {Passeio.objects.count()} passeios')
        self.stdout.write(f'• {Fornecedor.objects.count()} fornecedores')
        self.stdout.write(f'• {TipoVeiculo.objects.count()} tipos de veículos')
        self.stdout.write(f'• {Conta.objects.count()} contas financeiras')
        self.stdout.write(f'• {AcaoRapida.objects.count()} ações rápidas')
        self.stdout.write(
            self.style.WARNING('\nAcesse http://127.0.0.1:8001/admin/ para visualizar!')
        )