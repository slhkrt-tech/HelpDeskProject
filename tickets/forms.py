from django import forms #django’nun form kütüphanesi
from .models import Ticket, Comment #aynı uygulamadaki Ticket ve Comment modelleri

class TicketForm(forms.ModelForm): #ticket modeli için ModelForm olarak tanımlanır
    class Meta:
        model = Ticket
        fields = ['title','description','priority','category','sla']

class CommentForm(forms.ModelForm): #comment modeli için ModelForm olarak tanımlanır
    class Meta:
        model = Comment
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'rows':3})}