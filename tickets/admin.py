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
    list_display = ('id','title','status','priority','user','assigned_to','category','created_at', 'get_description') #ticket listesinde görünen sütunlar
    list_filter = ('status','priority','category') #sağ panelde filtreleme seçenekleri
    search_fields = ('title','description') #üstte arama çubuğunda title ve description alanlarında arama yapar
    actions = ['mark_as_closed', 'mark_as_pending', 'mark_as_open'] #kapatma, bekletme, açık
    
    # sadece status’u "kapatacak" değiştirebilecek custom action
    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='closed')  # status alanını 'closed' yap
        self.message_user(request, f"{updated} ticket kapatıldı.")
    mark_as_closed.short_description = "Close selected tickets"

     # sadece status’u "bekletme" yapacak custom action
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')  # status alanını 'pending' yap
        self.message_user(request, f"{updated} ticket beklemeye alındı.")
    mark_as_pending.short_description = "Put selected tickets on hold"
    
    # sadece status’u "open" yapacak custom action
    def mark_as_open(self, request, queryset):
        updated = queryset.update(status='open')  # status alanını 'open' yap
        self.message_user(request, f"{updated} ticket açık olarak işaretlendi.")
    mark_as_open.short_description = "Mark selected tickets as open"


    # Kısa description göstermek için helper fonksiyon
    def get_description(self, obj):
        if len(obj.description) > 75:
            return obj.description[:75] + "..."
        return obj.description
    get_description.short_description = "Description"

    def has_delete_permission(self, request, obj=None):
        return True
    
    # Diğer alanlar readonly, status editable
    readonly_fields = ('title', 'description', 'priority', 'user', 'assigned_to', 'category', 'created_at')
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','ticket','user','created_at') #yorumlar admin panelinde listelenir
    search_fields = ('message',) #yorum metni (message) üzerinden arama yapılabilir
