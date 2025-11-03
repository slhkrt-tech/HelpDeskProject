from django import forms
from .models import Talep, Comment  # Talep modeli ve Comment modeli

# ================================================================================
# Talep Formu
# ================================================================================
class TicketForm(forms.ModelForm):
    """
    Talep (Ticket) modeli için form
    Modern UI ve Bootstrap ile uyumlu
    """

    class Meta:
        model = Talep
        fields = ['title', 'description', 'priority', 'category', 'sla', 'assigned_to']

        # Widget'lar (form alanlarının HTML özellikleri)
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
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'sla': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

        # Alan başlıkları (label)
        labels = {
            'title': 'Talep Başlığı',
            'description': 'Detaylı Açıklama',
            'priority': 'Öncelik Seviyesi',
            'category': 'Kategori',
            'sla': 'Hizmet Seviyesi',
            'assigned_to': 'Atanacak Kişi',
        }

        # Yardım metinleri (help_text)
        help_texts = {
            'title': 'Talebinizi özetleyen kısa bir başlık',
            'description': 'Sorununuzu veya ihtiyacınızı detaylı şekilde açıklayın',
            'priority': 'Talebinizin aciliyet seviyesini belirleyin',
            'category': 'Talebinizin hangi kategoriye ait olduğunu seçin',
            'sla': 'Beklenen yanıt süresini belirleyin',
            'assigned_to': 'Belirli bir kişiye atamak istiyorsanız seçin',
        }

    def __init__(self, *args, **kwargs):
        """
        Form başlatıldığında ek özelleştirmeler
        - Zorunlu alanlar
        - Boş seçenekler
        - HTML 'required' attribute ekleme
        """
        super().__init__(*args, **kwargs)
        
        # Zorunlu alanlar - sadece başlık ve açıklama
        self.fields['title'].required = True
        self.fields['description'].required = True
        
        # Opsiyonel alanlar - kullanıcı isterse doldurmayabilir
        self.fields['category'].required = False
        self.fields['sla'].required = False
        self.fields['priority'].required = False
        self.fields['assigned_to'].required = False
        
        # Boş seçenekler ekleme
        self.fields['category'].empty_label = "--- Kategori Seçin (İsteğe Bağlı) ---"
        self.fields['sla'].empty_label = "--- Hizmet Seviyesi Seçin (İsteğe Bağlı) ---"
        self.fields['priority'].empty_label = "--- Öncelik Seçin (İsteğe Bağlı) ---"
        self.fields['assigned_to'].empty_label = "--- Otomatik Atama ---"
        
        # Zorunlu alanlara 'required' attribute ekle
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = True
            else:
                # Zorunlu olmayan alanlardan required attribute'unu kaldır
                field.widget.attrs.pop('required', None)


# ================================================================================
# Yorum Formu
# ================================================================================
class CommentForm(forms.ModelForm):
    """
    Comment modeli için form
    Modern UI ve Bootstrap ile uyumlu
    """

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