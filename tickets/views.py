# tickets/views.py
# ================================================================================
# HelpDesk Ticket Yönetimi - Ana View'lar
# Ticket CRUD işlemleri, yetkilendirme, durum yönetimi
# ================================================================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q  # Gelişmiş sorgu filtreleme için

from .models import Talep, Category, Comment
from .forms import TicketForm

User = get_user_model()  # CustomUser modelini dinamik olarak al

# ================================================================================
# Yardımcı Fonksiyonlar - Kullanıcı Yetki Kontrolü
# ================================================================================

def is_admin_user(user):
    """
    Admin kullanıcı kontrolü - Sistem yöneticisi ve admin rol kontrolü
    Args:
        user: Kontrol edilecek kullanıcı objesi
    Returns:
        bool: Admin yetkisi var mı?
    """
    return user.is_superuser or user.role == 'admin'

def is_support_user(user):
    """
    Support kullanıcı kontrolü - Destek personeli ve üst roller
    Args:
        user: Kontrol edilecek kullanıcı objesi  
    Returns:
        bool: Support yetkisi var mı?
    """
    return user.is_superuser or user.role in ['admin', 'support']

@login_required
def ticket_list(request):
    """
    Gelişmiş Ticket listesi:
    - Admin kullanıcılar: Tüm talepleri görür ve durum değiştirebilir
    - Support kullanıcılar: Tüm talepleri görür, kısıtlı durum değiştirebilir
    - Normal kullanıcılar: Sadece kendi grubundaki talepleri görür
    """
    user = request.user
    
    # Admin kullanıcılar tüm talepleri görür
    if is_admin_user(user):
        tickets = Talep.objects.all().order_by('-created_at')
        user_role = 'admin'
    # Support kullanıcılar tüm talepleri görür
    elif is_support_user(user):
        tickets = Talep.objects.all().order_by('-created_at')
        user_role = 'support'
    else:
        # Normal kullanıcılar: Kendi talepleri + aynı gruptaki diğer talepleri
        if user.groups.exists():
            # Kullanıcının kendi talepleri + grup taleplerini al
            user_groups = user.groups.all()
            group_categories = Category.objects.filter(name__in=user_groups.values_list('name', flat=True))
            
            tickets = Talep.objects.filter(
                Q(user=user) |  # Kendi talepleri
                Q(category__in=group_categories)  # Grup talepleri
            ).distinct().order_by('-created_at')
        else:
            # Gruba ait değilse sadece kendi taleplerini görür
            tickets = Talep.objects.filter(user=user).order_by('-created_at')
        user_role = 'customer'
    
    # Durum filtreleme
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    
    # Öncelik filtreleme
    priority_filter = request.GET.get('priority')
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    
    context = {
        'tickets': tickets,
        'user_role': user_role,
        'is_admin': is_admin_user(user),
        'is_support': is_support_user(user),
        'status_choices': Talep.STATUS_CHOICES,
        'priority_choices': Talep.PRIORITY_CHOICES,
        'current_status_filter': status_filter,
        'current_priority_filter': priority_filter,
    }
    
    return render(request, 'tickets/ticket_list.html', context)

@login_required
@require_POST
def change_ticket_status(request, pk):
    """
    Ticket durumu değiştirme (sadece admin ve support kullanıcılar)
    """
    ticket = get_object_or_404(Talep, pk=pk)
    new_status = request.POST.get('status')
    
    # Yetki kontrolü
    if not is_support_user(request.user):
        return JsonResponse({
            'success': False, 
            'error': 'Bu işlem için yetkiniz yok.'
        }, status=403)
    
    # Geçerli status kontrolü
    valid_statuses = [choice[0] for choice in Talep.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse({
            'success': False, 
            'error': 'Geçersiz durum.'
        }, status=400)
    
    # Admin olmayan kullanıcılar bazı durumlara geçiş yapamaz
    if not is_admin_user(request.user) and new_status in ['wrong_section']:
        return JsonResponse({
            'success': False, 
            'error': 'Bu duruma geçiş için admin yetkisi gerekli.'
        }, status=403)
    
    old_status = ticket.status
    ticket.status = new_status
    
    # Eğer ticket atanmamışsa ve admin/support kullanıcı durumu değiştiriyorsa
    # otomatik olarak kendisine ata
    if not ticket.assigned_to and is_support_user(request.user):
        ticket.assigned_to = request.user
    
    ticket.save()
    
    # Status değişikliği için yorum ekle
    status_display = dict(Talep.STATUS_CHOICES).get(new_status, new_status)
    old_status_display = dict(Talep.STATUS_CHOICES).get(old_status, old_status)
    
    Comment.objects.create(
        talep=ticket,
        user=request.user,
        message=f"Durum '{old_status_display}' → '{status_display}' olarak değiştirildi."
    )
    
    return JsonResponse({
        'success': True,
        'new_status': new_status,
        'new_status_display': status_display,
        'assigned_to': ticket.assigned_to.username if ticket.assigned_to else None
    })

@login_required
def ticket_detail(request, pk):
    """
    Ticket detay görüntüleme ve yorum ekleme
    
    Yetki Kontrolleri:
    - Admin/Support: Tüm ticket'lara erişebilir
    - Normal kullanıcılar: Sadece kendi gruplarındaki ticket'lara erişebilir
    
    Özellikler:
    - Ticket bilgileri görüntüleme
    - Yorum ekleme sistemi
    - Yetki tabanlı işlem butonları
    """
    ticket = get_object_or_404(Talep, pk=pk)
    user = request.user
    
    # ================================
    # Yetki Kontrolü
    # ================================
    if not is_admin_user(user) and not is_support_user(user):
        # Normal kullanıcı için grup tabanlı erişim kontrolü
        if user.groups.exists():
            # Kullanıcının gruplarındaki tüm kullanıcıları al
            group_users = User.objects.filter(groups__in=user.groups.all()).distinct()
            if ticket.user not in group_users:
                messages.error(request, 'Bu talebe erişim yetkiniz yok.')
                return redirect('ticket_list')
        else:
            # Gruba üye değilse sadece kendi ticket'larına bakabilir
            if ticket.user != user:
                messages.error(request, 'Bu talebe erişim yetkiniz yok.')
                return redirect('ticket_list')
    
    # ================================
    # Yorum Sistemi
    # ================================
    
    # Mevcut yorumları kronolojik sırada getir
    comments = ticket.yorumlar.all().order_by('created_at')
    
    # POST işlemi: Yeni yorum ekleme
    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            Comment.objects.create(
                talep=ticket,
                user=user,
                message=comment_text
            )
            messages.success(request, 'Yorum başarıyla eklendi.')
            return redirect('ticket_detail', pk=pk)
        else:
            messages.error(request, 'Yorum boş olamaz.')
    
    # ================================
    # Template Context Hazırlama
    # ================================
    context = {
        'ticket': ticket,
        'comments': comments,
        'is_admin': is_admin_user(user),
        'is_support': is_support_user(user),
        'status_choices': Talep.STATUS_CHOICES,
        'priority_choices': Talep.PRIORITY_CHOICES,
    }
    
    return render(request, 'tickets/ticket_detail.html', context)


@login_required
@login_required
def ticket_create(request):
    """
    Yeni ticket oluşturma view'ı
    
    POST: Form verilerini işler ve yeni ticket oluşturur
    GET: Boş ticket form'unu gösterir
    
    İş Akışı:
    1. Form validasyonu
    2. Kullanıcı bilgilerini ticket'a ata
    3. Grup kategorisi varsa otomatik ata
    4. Kullanıcının rolüne göre yönlendir
    """
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            # Ticket nesnesini oluştur ama henüz kaydetme
            talep = form.save(commit=False)
            
            # İşlem yapan kullanıcıyı ticket'a ata
            talep.user = request.user
            
            # Otomatik kategori atama (grup tabanlı)
            if request.user.groups.exists():
                group_name = request.user.groups.first().name
                category = Category.objects.filter(name=group_name).first()
                if category:
                    talep.category = category
            
            # Ticket'ı veritabanına kaydet
            talep.save()
            
            # Kullanıcının rolüne göre uygun panele yönlendir
            if request.user.role == 'admin':
                return redirect('admin_panel')
            elif request.user.role == 'support':
                return redirect('support_panel')
            else:  # customer role
                return redirect('customer_panel')
    else:
        # GET isteği - Boş form göster
        form = TicketForm()
    
    return render(request, 'tickets/ticket_create.html', {'form': form})


# ================================================================================
# DEPRECATED FUNCTIONS - MOVED TO ACCOUNTS APP
# Bu fonksiyonlar accounts app'ine taşındı, burada gereksiz
# ================================================================================

# NOT: signup ve add_user_to_group fonksiyonları artık accounts.views'de
# Geriye dönük uyumluluk için URL'ler hala çalışıyor ancak accounts app'e yönlendiriyor