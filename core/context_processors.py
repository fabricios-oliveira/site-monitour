from .models import SiteSettings

def site_settings(request):
    """Context processor para disponibilizar configurações do site em todos os templates"""
    try:
        settings_obj = SiteSettings.objects.get(pk=1)
    except SiteSettings.DoesNotExist:
        # Criar configurações padrão se não existirem
        settings_obj = SiteSettings.objects.create(
            company_name="MONITOUR",
            site_title="MONITOUR - Turismo & Viagens",
            meta_description="Sua agência de turismo especializada em experiências únicas e inesquecíveis.",
            phone="(11) 99999-9999",
            whatsapp="+5511999999999",
            email="contato@monitour.com.br"
        )
    
    # Estatísticas padrão
    stats = {
        'years_experience': 10,
        'happy_clients': 5000,
        'destinations': 50,
        'tours_completed': 1200,
    }
    
    return {
        'site_settings': settings_obj,
        'stats': stats,
    }