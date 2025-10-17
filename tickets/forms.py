from django import forms
from .models import Talep, Comment  # Ticket -> Talep

class TicketForm(forms.ModelForm):

    """Talep modeli için form (eski Ticket)"""

    class Meta:
        model = Talep
        fields = ['title', 'description', 'priority', 'category', 'sla', 'assigned_to']

class CommentForm(forms.ModelForm):

    """Comment modeli için form"""
    
    class Meta:
        model = Comment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3})
        }