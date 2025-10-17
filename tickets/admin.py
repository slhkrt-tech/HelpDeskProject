# admin.py ile modeller admin panelinde görünür hale gelir
# list_display → hangi alanların listede görüneceğini belirler
# list_filter → filtreleme seçenekleri ekler
# search_fields → arama çubuğunda hangi alanların aranacağını belirler

from django.contrib import admin
from .models import Category, SLA, Ticket, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'response_time', 'resolve_time')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'priority', 'user', 'assigned_to', 'category', 'created_at', 'get_description')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')
    actions = ['mark_as_closed', 'mark_as_pending', 'mark_as_open']

    # Custom action: Close selected tickets

    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f"{updated} ticket kapatıldı.")
    mark_as_closed.short_description = "Close selected tickets"

    # Custom action: Put selected tickets on hold

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f"{updated} ticket beklemeye alındı.")
    mark_as_pending.short_description = "Put selected tickets on hold"

    # Custom action: Mark selected tickets as open

    def mark_as_open(self, request, queryset):
        updated = queryset.update(status='open')
        self.message_user(request, f"{updated} ticket açık olarak işaretlendi.")
    mark_as_open.short_description = "Mark selected tickets as open"

    # Kısa description göstermek için helper fonksiyon

    def get_description(self, obj):
        return (obj.description[:75] + "...") if len(obj.description) > 75 else obj.description
    get_description.short_description = "Description"

    # Sadece bazı alanlar editable

    readonly_fields = ('title', 'description', 'priority', 'user', 'assigned_to', 'category', 'created_at')

    # Silme yetkisi

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'created_at')
    search_fields = ('message',)