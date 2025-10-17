# admin.py
# ---------------------------------------------------------------------
# Bu dosya modellerin Django admin panelinde nasıl görüneceğini ve
# yönetileceğini tanımlar.
# ---------------------------------------------------------------------

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Category, SLA, Ticket, Comment

# ---------------------------------------------------------------------
# Category (Kategori) Modeli
# ---------------------------------------------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Listede gösterilecek sütunlar
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)
    verbose_name = _("Kategori")
    verbose_name_plural = _("Kategoriler")

# ---------------------------------------------------------------------
# SLA (Servis Düzeyi Anlaşması) Modeli
# ---------------------------------------------------------------------

@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'response_time', 'resolve_time')
    search_fields = ('name',)
    ordering = ('id',)
    verbose_name = _("SLA")
    verbose_name_plural = _("SLA'lar")

# ---------------------------------------------------------------------
# Ticket (Talep) Modeli
# ---------------------------------------------------------------------

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    # Liste görünümünde gösterilecek sütunlar
    
    list_display = (
        'id',
        'title',
        'get_status_display',  # Durumun okunabilir hali
        'priority',
        'user',
        'assigned_to',
        'category',
        'created_at',
        'get_description',
    )

    # Sağ kenar filtre alanları
    list_filter = ('status', 'priority', 'category')

    # Arama yapılacak alanlar
    search_fields = ('title', 'description')

    # Özelleştirilmiş işlemler (actions)
    actions = [
        'mark_as_closed',
        'mark_as_pending',
        'mark_as_open',
        'mark_as_wrong_section'
    ]

    # -----------------------------------------------------------------
    # Özel işlemler (Custom Admin Actions)
    # -----------------------------------------------------------------

    def mark_as_closed(self, request, queryset):
        updated = queryset.update(status='closed')
        self.message_user(request, f"{updated} talep kapatıldı.")
    mark_as_closed.short_description = "Seçilen talepleri (Kapatıldı) olarak işaretle"

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f"{updated} talep beklemeye alındı.")
    mark_as_pending.short_description = "Seçilen talepleri (Beklemede) olarak işaretle"

    def mark_as_open(self, request, queryset):
        updated = queryset.update(status='open')
        self.message_user(request, f"{updated} talep açık olarak işaretlendi.")
    mark_as_open.short_description = "Seçilen talepleri (Açık) olarak işaretle"

    def mark_as_wrong_section(self, request, queryset):
        updated = queryset.update(status='wrong_section')
        self.message_user(request, f"{updated} talep 'Yanlış Bölüm / Kapatıldı' olarak işaretlendi.")
    mark_as_wrong_section.short_description = "Seçilen talepleri (Yanlış Bölüm / Kapatıldı) olarak işaretle"

    # -----------------------------------------------------------------
    # Yardımcı Fonksiyonlar
    # -----------------------------------------------------------------

    # Açıklamayı 75 karakterle kısaltarak göster

    def get_description(self, obj):
        return (obj.description[:75] + "...") if len(obj.description) > 75 else obj.description
    get_description.short_description = "Açıklama"

    # -----------------------------------------------------------------
    # Salt Okunur Alanlar
    # -----------------------------------------------------------------

    readonly_fields = (
        'title',
        'description',
        'priority',
        'user',
        'assigned_to',
        'category',
        'created_at',
    )

    # -----------------------------------------------------------------
    # Silme Yetkisi
    # -----------------------------------------------------------------
    # Admin her zaman silebilir

    def has_delete_permission(self, request, obj=None):
        return True

    # "delete_selected" eylemini Türkçeleştir
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'] = (
                actions['delete_selected'][0],
                actions['delete_selected'][1],
                "Seçilen talepleri sil"
            )
        return actions

# ---------------------------------------------------------------------
# Comment (Yorum) Modeli
# ---------------------------------------------------------------------

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'created_at')
    search_fields = ('message',)
    ordering = ('-created_at',)
    verbose_name = _("Yorum")
    verbose_name_plural = _("Yorumlar")

# ---------------------------------------------------------------------
# Genel Admin Başlıkları
# ---------------------------------------------------------------------

admin.site.site_header = "Yönetim Paneli"
admin.site.site_title = "HelpDesk Yönetimi"
admin.site.index_title = "Hoşgeldiniz - HelpDesk Admin"