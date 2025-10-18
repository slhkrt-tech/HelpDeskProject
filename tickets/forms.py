from django import forms
from .models import Talep, Comment  # Talep = Ticket modeli


class TicketForm(forms.ModelForm):
    """Talep oluşturma/güncelleme formu.

    ModelForm kullanılarak Talep modelinin alanları form üzerinde gösterilir.
    """

    class Meta:
        model = Talep
        fields = ['title', 'description', 'priority', 'category', 'sla', 'assigned_to']


class CommentForm(forms.ModelForm):
    """Talep için yorum gönderme formu."""

    class Meta:
        model = Comment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3})
        }