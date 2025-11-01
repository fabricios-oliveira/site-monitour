import sqlite3

# Conectar ao banco antigo
conn = sqlite3.connect('sistema_antigo_backup.sqlite3')
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('Tabelas no banco antigo:')
for table in tables:
    print(f'- {table[0]}')

print('\n' + '='*50)
print('Verificando dados em todas as tabelas:')

# Verificar dados em todas as tabelas (exceto internas do Django)
for table in tables:
    table_name = table[0]
    if not table_name.startswith('django_') and not table_name.startswith('auth_') and not table_name.startswith('sqlite_') and not table_name.startswith('admin_'):
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            if count > 0:
                print(f'✓ {table_name}: {count} registros')
            else:
                print(f'- {table_name}: vazio')
        except sqlite3.OperationalError as e:
            print(f'✗ Erro ao acessar {table_name}: {e}')

conn.close()