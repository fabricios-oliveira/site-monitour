#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')
django.setup()

from django.contrib.auth.models import User

# Resetar senha do usuário admin
try:
    user = User.objects.get(username='admin')
    user.set_password('admin123')
    user.save()
    print(f"✅ Senha do usuário '{user.username}' foi resetada para 'admin123'")
except User.DoesNotExist:
    print("❌ Usuário admin não encontrado")

# Também resetar senha do fabricio
try:
    user = User.objects.get(username='fabricio')
    user.set_password('fabricio123')
    user.save()
    print(f"✅ Senha do usuário '{user.username}' foi resetada para 'fabricio123'")
except User.DoesNotExist:
    print("❌ Usuário fabricio não encontrado")