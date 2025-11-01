from django import forms
from .models import Conta

class ExtratoUploadForm(forms.ModelForm):
    conta = forms.ModelChoiceField(
        queryset=Conta.objects.none(), # Começa vazio, será preenchido na view
        label="Selecione a Conta"
    )
    arquivo_ofx = forms.FileField(label="Arquivo de Extrato (.ofx)")

    def __init__(self, *args, **kwargs):
        # Remove o usuário do kwargs para passar para o super()
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtra o queryset para mostrar apenas as contas do usuário logado
            self.fields['conta'].queryset = Conta.objects.filter(usuario=user)