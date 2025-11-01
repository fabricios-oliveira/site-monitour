#!/usr/bin/env python
"""Script para criar dados de teste no Sistema MONITOUR"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')
django.setup()

from cadastros.models import Cliente, MatriculaCliente
from datetime import date
import random

def criar_dados_teste():
    """Cria dados de teste para demonstração"""
    print("=== CRIANDO DADOS DE TESTE MONITOUR ===")
    
    # Criar alguns clientes de teste
    clientes_data = [
        {'nome': 'Maria Silva Santos', 'cpf': '12345678901', 'data_nascimento': date(1985, 6, 15)},
        {'nome': 'João Pedro Oliveira', 'cpf': '98765432109', 'data_nascimento': date(1990, 3, 22)},
        {'nome': 'Ana Carolina Costa', 'cpf': '45678912345', 'data_nascimento': date(1988, 11, 8)},
        {'nome': 'Carlos Eduardo Lima', 'cpf': '11122233344', 'data_nascimento': date(1992, 1, 10)},
        {'nome': 'Fernanda Alves Rocha', 'cpf': '55566677788', 'data_nascimento': date(1986, 9, 25)}
    ]

    print('Criando clientes de teste...')
    for data in clientes_data:
        try:
            cliente, created = Cliente.objects.get_or_create(
                cpf=data['cpf'],
                defaults={
                    'nome': data['nome'],
                    'data_nascimento': data['data_nascimento'],
                    'genero': random.choice(['M', 'F']),
                    'nacionalidade': 'Brasileira',
                    'estado_civil': random.choice(['solteiro', 'casado', 'divorciado']),
                    'telefone': f'(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                    'email': f"{data['nome'].lower().replace(' ', '.')}@email.com"
                }
            )
            if created:
                print(f'✅ Cliente criado: {cliente.nome} (Matrícula: {cliente.matricula})')
            else:
                print(f'ℹ️  Cliente já existe: {cliente.nome} (Matrícula: {cliente.matricula})')
        except Exception as e:
            print(f'❌ Erro ao criar cliente {data["nome"]}: {e}')

    print(f'\n📊 RESUMO:')
    print(f'Total de clientes: {Cliente.objects.count()}')
    print(f'Total de matrículas: {MatriculaCliente.objects.count()}')
    print('✅ Dados de teste criados com sucesso!')

if __name__ == '__main__':
    criar_dados_teste()