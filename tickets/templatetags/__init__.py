from django import template

register = template.Library()

@register.simple_tag
def badge(text, color='secondary'):
    """
    Bootstrap badge komponenti oluşturur.
    Kullanım: {% badge "Metin" "renk" %}
    """
    return f'<span class="badge bg-{color} bg-opacity-10 text-{color} border border-{color} border-opacity-25 px-3 py-2">{text}</span>'