# admin.py
# ================================================================================
# Django Admin Konfigürasyonu - Tickets Uygulaması
# Bu dosya, modellerin admin panelde nasıl görüneceğini ve yönetileceğini belirler.
# ================================================================================

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import Category, SLA, Talep, Comment


# -------------------------------------------------------------------------------
# Kategori (Category) Admin
# -------------------------------------------------------------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)
    verbose_name = _("Kategori")
    verbose_name_plural = _("Kategoriler")


# -------------------------------------------------------------------------------
# SLA (Servis Düzeyi Anlaşması) Admin
# -------------------------------------------------------------------------------
@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'response_time', 'resolve_time')
    search_fields = ('name',)
    ordering = ('id',)
    verbose_name = _("SLA")
    verbose_name_plural = _("SLA'lar")


# -------------------------------------------------------------------------------
# Talep (Ticket) Admin
# -------------------------------------------------------------------------------
@admin.register(Talep)
class TalepAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'get_status_display',
        'priority',
        'user',
        'assigned_to',
        'category',
        'created_at',
        'get_description',
        'status_change_buttons',
    )
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')
    actions = [
        'mark_as_closed',
        'mark_as_pending',
        'mark_as_open',
        'mark_as_wrong_section'
    ]

    # ================================
    # Custom URLs için
    # ================================
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('change_status/<int:talep_id>/<str:new_status>/', 
                 self.admin_site.admin_view(self.change_status_view), 
                 name='tickets_talep_change_status'),
        ]
        return custom_urls + urls

    def change_status_view(self, request, talep_id, new_status):
        """AJAX ile durum değiştirme"""
        talep = get_object_or_404(Talep, id=talep_id)
        
        # Durum geçerli mi kontrol et
        valid_statuses = [choice[0] for choice in Talep.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'error': 'Geçersiz durum'}, status=400)
        
        old_status = talep.get_status_display()
        talep.status = new_status
        talep.save()
        
        new_status_display = talep.get_status_display()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': f'Talep #{talep_id} durumu "{old_status}" → "{new_status_display}" olarak değiştirildi.',
                'new_status': new_status_display
            })
        else:
            messages.success(request, f'Talep #{talep_id} durumu "{old_status}" → "{new_status_display}" olarak değiştirildi.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/tickets/talep/'))

    # ================================
    # Durum Değiştirme Butonları
    # ================================
    def status_change_buttons(self, obj):
        """Her talep için durum değiştirme butonları"""
        buttons = []
        current_status = obj.status
        
        # Mevcut duruma göre gösterilecek butonları belirle
        status_transitions = {
            'new': ['seen', 'open', 'wrong_section'],
            'seen': ['open', 'pending', 'wrong_section'],
            'open': ['in_progress', 'pending', 'resolved'],
            'pending': ['open', 'in_progress'],
            'in_progress': ['resolved', 'pending'],
            'resolved': ['closed', 'open'],
            'closed': ['open'],
            'wrong_section': ['new', 'open']
        }
        
        available_statuses = status_transitions.get(current_status, [])
        
        for status_code in available_statuses:
            status_name = dict(Talep.STATUS_CHOICES)[status_code]
            color_map = {
                'seen': '#17a2b8',      # info
                'open': '#28a745',      # success
                'pending': '#ffc107',   # warning
                'in_progress': '#007bff', # primary
                'resolved': '#6f42c1',  # purple
                'closed': '#6c757d',    # secondary
                'wrong_section': '#dc3545', # danger
                'new': '#fd7e14'        # orange
            }
            
            button_html = format_html(
                '<button class="btn btn-sm status-change-btn" '
                'style="background-color: {}; color: white; margin: 1px; font-size: 10px; padding: 2px 6px;" '
                'data-talep-id="{}" data-new-status="{}" title="Durumu {} Yap">{}</button>',
                color_map.get(status_code, '#6c757d'),
                obj.id,
                status_code,
                status_name,
                status_name[:10]  # İlk 10 karakter
            )
            buttons.append(button_html)
        
        if not buttons:
            return format_html('<span style="color: #999;">Değişiklik yok</span>')
        
        return format_html('<div class="status-buttons-container">{}</div>', ''.join(buttons))
    
    status_change_buttons.short_description = "Durum Değiştir"
    status_change_buttons.allow_tags = True

    # ================================
    # Media (CSS/JS) Ekleme
    # ================================
    class Media:
        js = ('admin/js/status_change.js',)
        css = {
            'all': ('admin/css/status_change.css',)
        }

    # ================================
    # Toplu İşlemler (Bulk Actions)
    # ================================
    def mark_as_closed(self, request, queryset):
        """Seçilen talepleri 'Kapatıldı' olarak işaretle"""
        updated = queryset.update(status='closed')
        self.message_user(request, f"{updated} talep kapatıldı.")
    mark_as_closed.short_description = "Seçilen talepleri (Kapatıldı) olarak işaretle"

    def mark_as_pending(self, request, queryset):
        """Seçilen talepleri 'Beklemede' olarak işaretle"""
        updated = queryset.update(status='pending')
        self.message_user(request, f"{updated} talep beklemeye alındı.")
    mark_as_pending.short_description = "Seçilen talepleri (Beklemede) olarak işaretle"

    def mark_as_open(self, request, queryset):
        """Seçilen talepleri 'Açık' olarak işaretle"""
        updated = queryset.update(status='open')
        self.message_user(request, f"{updated} talep açık olarak işaretlendi.")
    mark_as_open.short_description = "Seçilen talepleri (Açık) olarak işaretle"

    def mark_as_wrong_section(self, request, queryset):
        """Seçilen talepleri 'Yanlış Bölüm' olarak işaretle"""
        updated = queryset.update(status='wrong_section')
        self.message_user(request, f"{updated} talep yanlış bölüm olarak işaretlendi.")
    mark_as_wrong_section.short_description = "Seçilen talepleri (Yanlış Bölüm) olarak işaretle"

    # ================================
    # Özel Görünüm Metodları (Custom Display)
    # ================================
    def get_description(self, obj):
        """Açıklama alanını 75 karakter ile sınırla"""
        return (obj.description[:75] + "...") if len(obj.description) > 75 else obj.description
    get_description.short_description = "Açıklama"

    def view_detail(self, obj):
        """Detay görüntüleme linki"""
        return format_html(
            '<a href="/admin/tickets/talep/{}/change/" target="_blank">Detay</a>',
            obj.id
        )
    view_detail.short_description = "📄"


# -------------------------------------------------------------------------------
# Yorum (Comment) Admin
# -------------------------------------------------------------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'talep', 'user', 'created_at')
    search_fields = ('message',)
    ordering = ('-created_at',)
    verbose_name = _("Yorum")
    verbose_name_plural = _("Yorumlar")


# -------------------------------------------------------------------------------
# Genel Admin Paneli Başlıkları
# -------------------------------------------------------------------------------
admin.site.site_header = "Yönetim Paneli"
admin.site.site_title = "Yardım Masası Yönetimi"
admin.site.index_title = "Hoşgeldiniz - Yardım Masası Admin"