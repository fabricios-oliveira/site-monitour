"""
Forms para o Sistema Interno MONITOUR
"""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div, HTML
from .models import TourPackage, Sale, CustomerInquiry, TourPackageCategory, Destination

class PackageForm(forms.ModelForm):
    """Formulário para criação/edição de pacotes"""
    
    class Meta:
        model = TourPackage
        fields = [
            'title', 'slug', 'short_description', 'description',
            'category', 'destination', 'duration_days', 'duration_nights',
            'max_participants', 'min_participants', 'difficulty',
            'price_per_person', 'discount_percentage', 'available_spots',
            'start_date', 'end_date', 'booking_deadline',
            'includes', 'excludes', 'featured_image',
            'is_active', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'includes': forms.Textarea(attrs={'rows': 4}),
            'excludes': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'
        
        self.helper.layout = Layout(
            HTML('<div class="bg-white p-6 rounded-lg shadow-md">'),
            HTML('<h2 class="text-xl font-bold text-blue-900 mb-4">Informações Básicas</h2>'),
            Row(
                Column('title', css_class='form-group col-md-8'),
                Column('slug', css_class='form-group col-md-4'),
            ),
            Row(
                Column('category', css_class='form-group col-md-6'),
                Column('destination', css_class='form-group col-md-6'),
            ),
            'short_description',
            'description',
            HTML('</div>'),
            
            HTML('<div class="bg-white p-6 rounded-lg shadow-md mt-6">'),
            HTML('<h2 class="text-xl font-bold text-blue-900 mb-4">Detalhes do Pacote</h2>'),
            Row(
                Column('duration_days', css_class='form-group col-md-3'),
                Column('duration_nights', css_class='form-group col-md-3'),
                Column('difficulty', css_class='form-group col-md-6'),
            ),
            Row(
                Column('min_participants', css_class='form-group col-md-6'),
                Column('max_participants', css_class='form-group col-md-6'),
            ),
            HTML('</div>'),
            
            HTML('<div class="bg-white p-6 rounded-lg shadow-md mt-6">'),
            HTML('<h2 class="text-xl font-bold text-blue-900 mb-4">Preços e Disponibilidade</h2>'),
            Row(
                Column('price_per_person', css_class='form-group col-md-4'),
                Column('discount_percentage', css_class='form-group col-md-4'),
                Column('available_spots', css_class='form-group col-md-4'),
            ),
            HTML('</div>'),
            
            HTML('<div class="bg-white p-6 rounded-lg shadow-md mt-6">'),
            HTML('<h2 class="text-xl font-bold text-blue-900 mb-4">Datas</h2>'),
            Row(
                Column('start_date', css_class='form-group col-md-4'),
                Column('end_date', css_class='form-group col-md-4'),
                Column('booking_deadline', css_class='form-group col-md-4'),
            ),
            HTML('</div>'),
            
            HTML('<div class="bg-white p-6 rounded-lg shadow-md mt-6">'),
            HTML('<h2 class="text-xl font-bold text-blue-900 mb-4">Inclusões</h2>'),
            'includes',
            'excludes',
            HTML('</div>'),
            
            HTML('<div class="bg-white p-6 rounded-lg shadow-md mt-6">'),
            HTML('<h2 class="text-xl font-bold text-blue-900 mb-4">Imagem e Status</h2>'),
            'featured_image',
            Row(
                Column('is_active', css_class='form-group col-md-6'),
                Column('is_featured', css_class='form-group col-md-6'),
            ),
            HTML('</div>'),
            
            Div(
                Submit('submit', 'Salvar Pacote', css_class='btn-primary mt-6'),
                css_class='text-right'
            )
        )

class SaleStatusForm(forms.Form):
    """Formulário para atualizar status de venda"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmada'),
        ('paid', 'Paga'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Concluída'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        label='Status da Venda',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        label='Notas Internas',
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'status',
            'notes',
            Submit('submit', 'Atualizar Status', css_class='btn-primary mt-3')
        )

class InquiryResponseForm(forms.Form):
    """Formulário para responder consultas"""
    response = forms.CharField(
        label='Resposta',
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        help_text='Digite a resposta que será enviada ao cliente'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'response',
            Submit('submit', 'Enviar Resposta', css_class='btn-primary mt-3')
        )

class CategoryForm(forms.ModelForm):
    """Formulário para categorias"""
    class Meta:
        model = TourPackageCategory
        fields = ['name', 'description', 'slug', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DestinationForm(forms.ModelForm):
    """Formulário para destinos"""
    class Meta:
        model = Destination
        fields = [
            'name', 'country', 'state', 'city', 'description',
            'featured_image', 'slug', 'is_featured', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }