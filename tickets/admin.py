#admin.py ile modeller admin panelinde görünür hale gelir
#list_display → hangi alanların listede görüneceğini belirler
#list_filter → filtreleme seçenekleri ekler
#search_fields → arama çubuğunda hangi alanların aranacağını belirler

from django.contrib import admin #django’nun hazır admin paneli
from .models import Category, SLA, Ticket, Comment #aynı uygulamadaki modeller

@admin.register(Category) #category modelini admin paneline kaydeder
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name') #admin panelinde listede hangi alanlar görünür

@admin.register(SLA) #SLA modeli admin paneline eklenir
class SLAAdmin(admin.ModelAdmin):
    list_display = ('id','name','response_time','resolve_time')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id','title','status','priority','user','assigned_to','category','created_at') #ticket listesinde görünen sütunlar
    list_filter = ('status','priority','category') #sağ panelde filtreleme seçenekleri
    search_fields = ('title','description') #üstte arama çubuğunda title ve description alanlarında arama yapar

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','ticket','user','created_at') #yorumlar admin panelinde listelenir
    search_fields = ('message',) #yorum metni (message) üzerinden arama yapılabilir
