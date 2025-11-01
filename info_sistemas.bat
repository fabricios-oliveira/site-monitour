@echo off
echo ========================================
echo        MONITOUR - SISTEMAS EM EXECUÇÃO
echo ========================================
echo.
echo ✅ Site Principal: http://127.0.0.1:8000/
echo ✅ Sistema Administrativo: http://127.0.0.1:8001/admin/
echo.
echo ========================================
echo        CREDENCIAIS DE ACESSO
echo ========================================
echo.
echo 👤 SISTEMA ADMINISTRATIVO:
echo    Username: admin
echo    Password: admin123
echo.
echo    OU
echo.
echo    Username: fabricio  
echo    Password: fabricio123
echo.
echo ========================================
echo        COMANDOS ÚTEIS
echo ========================================
echo.
echo Para reiniciar os sistemas:
echo 1. Site Principal:
echo    cd %~dp0
echo    python manage.py runserver 8000
echo.
echo 2. Sistema Administrativo:
echo    cd %~dp0monitour_admin
echo    set DJANGO_SETTINGS_MODULE=admin_system.settings
echo    python manage.py runserver 8001
echo.
echo ========================================
pause