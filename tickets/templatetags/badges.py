from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def badge(text, color='secondary'):
    """
    Bootstrap badge komponenti oluşturur.
    Kullanım: {% badge "Metin" "renk" %}
    """
    html = f'<span class="badge bg-{color} bg-opacity-10 text-{color} border border-{color} border-opacity-25 px-3 py-2">{text}</span>'
    return mark_safe(html)

@register.simple_tag
def status_badge(status_display, status_value):
    """
    Ticket durumuna göre otomatik renk seçen badge.
    """
    color_map = {
        'new': 'primary',      # Yeni - Mavi
        'seen': 'info',        # Görüldü - Açık mavi
        'open': 'warning',     # Açık - Sarı
        'pending': 'secondary', # Beklemeye alındı - Gri
        'in_progress': 'info', # İşlemde - Açık mavi
        'resolved': 'success', # Çözüldü - Yeşil
        'closed': 'dark',      # Kapatıldı - Siyah
        'wrong_section': 'danger', # Yanlış bölüm - Kırmızı
    }
    color = color_map.get(status_value, 'secondary')
    html = f'<span class="badge bg-{color} bg-opacity-10 text-{color} border border-{color} border-opacity-25 px-3 py-2">{status_display}</span>'
    return mark_safe(html)

@register.simple_tag
def priority_badge(priority_display, priority_value):
    """
    Ticket önceliğine göre otomatik renk seçen badge.
    """
    color_map = {
        'low': 'success',      # Düşük - Yeşil
        'normal': 'primary',   # Normal - Mavi
        'high': 'warning',     # Yüksek - Sarı
        'urgent': 'danger',    # Acil - Kırmızı
    }
    color = color_map.get(priority_value, 'secondary')
    html = f'<span class="badge bg-{color} bg-opacity-10 text-{color} border border-{color} border-opacity-25 px-3 py-2">{priority_display}</span>'
    return mark_safe(html)