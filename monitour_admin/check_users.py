#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_system.settings')
django.setup()

from django.contrib.auth.models import User

print("=== USUÁRIOS DO SISTEMA ADMINISTRATIVO ===")
print(f"Total de usuários: {User.objects.all().count()}")
print(f"Superusuários: {User.objects.filter(is_superuser=True).count()}")
print()

print("Lista de usuários:")
for user in User.objects.all():
    print(f"- Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Superuser: {user.is_superuser}")
    print(f"  Ativo: {user.is_active}")
    print(f"  Último login: {user.last_login}")
    print()