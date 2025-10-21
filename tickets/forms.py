from django import forms
from .models import Talep, Comment  # Ticket -> Talep

class TicketForm(forms.ModelForm):
    """Talep modeli için form (eski Ticket) - Modern UI ile"""

    class Meta:
        model = Talep
        fields = ['title', 'description', 'priority', 'category', 'sla', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Talebinizin kısa ve açık bir başlığını yazın...',
                'maxlength': 200,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Talebinizi detaylı bir şekilde açıklayın...',
                'style': 'resize: vertical;'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'sla': forms.Select(attrs={
                'class': 'form-select',
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'title': 'Talep Başlığı',
            'description': 'Detaylı Açıklama',
            'priority': 'Öncelik Seviyesi',
            'category': 'Kategori',
            'sla': 'Hizmet Seviyesi',
            'assigned_to': 'Atanacak Kişi',
        }
        help_texts = {
            'title': 'Talebinizi özetleyen kısa bir başlık',
            'description': 'Sorununuzu veya ihtiyacınızı detaylı şekilde açıklayın',
            'priority': 'Talebinizin aciliyet seviyesini belirleyin',
            'category': 'Talebinizin hangi kategoriye ait olduğunu seçin',
            'sla': 'Beklenen yanıt süresini belirleyin',
            'assigned_to': 'Belirli bir kişiye atamak istiyorsanız seçin',
        }

    def __init__(self, *args, **kwargs):
        """Form initialization ve widget customization"""
        super().__init__(*args, **kwargs)
        
        # Zorunlu alanları belirle
        self.fields['title'].required = True
        self.fields['description'].required = True
        
        # Atama alanı için boş seçenek
        self.fields['assigned_to'].empty_label = "--- Otomatik Atama ---"
        
        # Bootstrap CSS sınıflarını otomatik ekle
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = True

class CommentForm(forms.ModelForm):
    """Comment modeli için form - Modern UI ile"""
    
    class Meta:
        model = Comment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Yorumunuzu yazın...',
                'style': 'resize: vertical;'
            })
        }
        labels = {
            'message': 'Yorum'
        }
        help_texts = {
            'message': 'Bu talep hakkında yorumunuzu yazın'
        }