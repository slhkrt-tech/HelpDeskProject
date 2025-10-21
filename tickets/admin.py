# admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db import models
from .models import Category, SLA, Talep, Comment

# ---------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    ordering = ('id',)
    verbose_name = _("Kategori")
    verbose_name_plural = _("Kategoriler")

# ---------------------------------------------------------------------
# SLA
# ---------------------------------------------------------------------

@admin.register(SLA)
class SLAAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'response_time', 'resolve_time')
    search_fields = ('name',)
    ordering = ('id',)
    verbose_name = _("SLA")
    verbose_name_plural = _("SLA'lar")

# ---------------------------------------------------------------------
# Talep
# ---------------------------------------------------------------------

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
        'view_detail',
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
    # Toplu İşlemler (Bulk Actions)
    # ================================

    def mark_as_closed(self, request, queryset):
        """Seçilen talepleri kapatıldı olarak işaretle"""
        updated = queryset.update(status='closed')
        self.message_user(request, f"{updated} talep kapatıldı.")
    mark_as_closed.short_description = "Seçilen talepleri (Kapatıldı) olarak işaretle"

    def mark_as_pending(self, request, queryset):
        """Seçilen talepleri beklemeye al"""
        updated = queryset.update(status='pending')
        self.message_user(request, f"{updated} talep beklemeye alındı.")
    mark_as_pending.short_description = "Seçilen talepleri (Beklemede) olarak işaretle"

    def mark_as_open(self, request, queryset):
        """Seçilen talepleri açık olarak işaretle"""
        updated = queryset.update(status='open')
        self.message_user(request, f"{updated} talep açık olarak işaretlendi.")
    mark_as_open.short_description = "Seçilen talepleri (Açık) olarak işaretle"

    # ================================
    # Custom Display Methods
    # ================================

    def get_description(self, obj):
        """Açıklama alanını kısalt"""
        return (obj.description[:75] + "...") if len(obj.description) > 75 else obj.description
    get_description.short_description = "Açıklama"

    def view_detail(self, obj):
        """Detay görüntüleme linki"""
        return format_html(
            '<a href="/admin/tickets/talep/{}/change/" target="_blank">Detay</a>',
            obj.id
        )
    view_detail.short_description = "📄"

# ---------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'talep', 'user', 'created_at')
    search_fields = ('message',)
    ordering = ('-created_at',)
    verbose_name = _("Yorum")
    verbose_name_plural = _("Yorumlar")

# ---------------------------------------------------------------------
# Genel admin başlıkları
# ---------------------------------------------------------------------

admin.site.site_header = "Yönetim Paneli"
admin.site.site_title = "Yardım Masası Yönetimi"
admin.site.index_title = "Hoşgeldiniz - HelpDesk Admin"