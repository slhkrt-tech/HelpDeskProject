from django import forms
from .models import Ticket, Comment

class TicketForm(forms.ModelForm):

    """Ticket modeli için form"""

    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category', 'sla']


class CommentForm(forms.ModelForm):

    """Comment modeli için form"""

    class Meta:
        model = Comment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3})
        }