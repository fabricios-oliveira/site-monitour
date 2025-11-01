# Configurações customizadas para Crispy Forms com TailwindCSS

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML, Submit
from crispy_forms.bootstrap import PrependedText, AppendedText
from django import forms


class ContactFormHelper(FormHelper):
    """Helper para formulário de contato"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'space-y-6'
        self.field_class = 'mb-4'
        self.label_class = 'block text-sm font-semibold text-gray-700 mb-2'
        self.field_template = 'crispy/field.html'
        
        # Layout customizado
        self.layout = Layout(
            Div(
                Field('name', 
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                      placeholder='Seu nome completo'),
                css_class='mb-4'
            ),
            Div(
                Field('email',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                      placeholder='seu@email.com'),
                css_class='mb-4'
            ),
            Div(
                Field('phone',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                      placeholder='(11) 99999-9999'),
                css_class='mb-4'
            ),
            Div(
                Field('subject',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                      placeholder='Assunto da sua mensagem'),
                css_class='mb-4'
            ),
            Div(
                Field('message',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none',
                      placeholder='Sua mensagem...',
                      rows=5),
                css_class='mb-6'
            ),
            Div(
                Submit('submit', 'Enviar Mensagem',
                       css_class='w-full bg-primary hover:bg-primary-dark text-white font-bold py-4 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 flex items-center justify-center'),
                css_class='text-center'
            )
        )


class NewsletterFormHelper(FormHelper):
    """Helper para formulário de newsletter"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'flex flex-col sm:flex-row gap-3'
        self.field_class = ''
        
        self.layout = Layout(
            Field('email',
                  css_class='flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                  placeholder='Seu melhor email'),
            Submit('submit', 'Inscrever-se',
                   css_class='bg-primary hover:bg-primary-dark text-white px-6 py-3 rounded-lg transition-colors font-semibold flex items-center justify-center')
        )


class BookingFormHelper(FormHelper):
    """Helper para formulário de reserva"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'space-y-4'
        self.field_class = 'mb-4'
        
        self.layout = Layout(
            Div(
                Field('name',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                      placeholder='Nome completo'),
                css_class='mb-4'
            ),
            Div(
                Field('email',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                      placeholder='Email'),
                css_class='mb-4'
            ),
            Div(
                Field('phone',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                      placeholder='Telefone'),
                css_class='mb-4'
            ),
            Div(
                Field('participants',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent'),
                css_class='mb-4'
            ),
            Div(
                Field('preferred_date',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent'),
                css_class='mb-4'
            ),
            Div(
                Field('message',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none',
                      placeholder='Alguma solicitação especial?',
                      rows=3),
                css_class='mb-6'
            ),
            Div(
                Submit('submit', 'Solicitar Orçamento',
                       css_class='w-full bg-primary hover:bg-primary-dark text-white font-bold py-4 rounded-lg transition-all duration-300 transform hover:scale-105 flex items-center justify-center'),
                css_class='text-center'
            )
        )


class CommentFormHelper(FormHelper):
    """Helper para formulário de comentários"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_class = 'space-y-4'
        
        self.layout = Layout(
            Div(
                Div(
                    Field('name',
                          css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                          placeholder='Seu nome'),
                    css_class='md:col-span-1'
                ),
                Div(
                    Field('email',
                          css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent',
                          placeholder='Seu email'),
                    css_class='md:col-span-1'
                ),
                css_class='grid grid-cols-1 md:grid-cols-2 gap-4 mb-4'
            ),
            Div(
                Field('content',
                      css_class='w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none',
                      placeholder='Deixe seu comentário...',
                      rows=4),
                css_class='mb-4'
            ),
            Div(
                Submit('submit', 'Publicar Comentário',
                       css_class='bg-primary hover:bg-primary-dark text-white px-6 py-3 rounded-lg transition-colors flex items-center'),
                css_class=''
            )
        )


# Formulários Django com Crispy Forms
class ContactForm(forms.Form):
    """Formulário de contato"""
    name = forms.CharField(
        max_length=100,
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=20,
        label='Telefone',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(
        max_length=200,
        label='Assunto',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label='Mensagem',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = ContactFormHelper()


class NewsletterForm(forms.Form):
    """Formulário de newsletter"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = NewsletterFormHelper()


class BookingForm(forms.Form):
    """Formulário de reserva"""
    name = forms.CharField(
        max_length=100,
        label='Nome Completo'
    )
    email = forms.EmailField(
        label='Email'
    )
    phone = forms.CharField(
        max_length=20,
        label='Telefone'
    )
    participants = forms.IntegerField(
        min_value=1,
        max_value=20,
        label='Número de Participantes'
    )
    preferred_date = forms.DateField(
        required=False,
        label='Data Preferida',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    message = forms.CharField(
        required=False,
        label='Mensagem',
        widget=forms.Textarea(attrs={'rows': 3})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BookingFormHelper()


class CommentForm(forms.Form):
    """Formulário de comentários"""
    name = forms.CharField(
        max_length=100,
        label='Nome'
    )
    email = forms.EmailField(
        label='Email'
    )
    content = forms.CharField(
        label='Comentário',
        widget=forms.Textarea(attrs={'rows': 4})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = CommentFormHelper()