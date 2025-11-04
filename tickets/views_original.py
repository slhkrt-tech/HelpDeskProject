# tickets/views.py
"""
Yardım Masası Ticket Yönetimi - Ana View'lar
========================================

Bu modül ticket CRUD işlemleri, yetkilendirme ve durum yönetimi içerir.
Modern UI/UX desteği ile kullanıcı dostu arayüz
Kullanıcı rolleri: admin, support, customer
"""

# Django temel importları
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

# Yerel model ve form importları
from .models import Talep, Category, Comment
from .forms import TicketForm

# Dinamik olarak CustomUser modelini al
User = get_user_model()

# ================================================================================
# Yardımcı Fonksiyonlar
# ================================================================================

def is_admin_user(user):
    """
    Admin kullanıcı kontrolü
    
    Args:
        user: Kullanıcı objesi
        
    Returns:
        bool: Admin yetkisi var mı?
    """
    return user.is_superuser or getattr(user, 'role', None) == 'admin'

def is_support_user(user):
    """
    Support kullanıcı kontrolü (admin + support)
    
    Args:
        user: Kullanıcı objesi
        
    Returns:
        bool: Support yetkisi var mı?
    """
    return user.is_superuser or getattr(user, 'role', None) in ['admin', 'support']

def get_user_tickets_queryset(user):
    """
    Kullanıcı rolüne göre ticket queryset'ini döndür
    
    Args:
        user: Kullanıcı objesi
        
    Returns:
        QuerySet: Kullanıcının görebileceği ticket'lar
    """
    if is_admin_user(user) or is_support_user(user):
        # Admin ve support tüm ticket'ları görebilir
        return Talep.objects.all()
    
    # Normal kullanıcılar sadece grup ticket'larını görebilir
    if user.groups.exists():
        group_users = User.objects.filter(groups__in=user.groups.all()).distinct()
        return Talep.objects.filter(user__in=group_users)
    
    # Gruplu değilse sadece kendi ticket'larını görebilir
    return Talep.objects.filter(user=user)

def _user_can_access_ticket(user, ticket):
    """
    Kullanıcının ticket'a erişip erişemeyeceğini kontrol eder
    
    Args:
        user: Kullanıcı objesi
        ticket: Ticket objesi
        
    Returns:
        bool: Erişim izni var mı?
    """
    # Admin ve support her ticket'a erişebilir
    if is_admin_user(user) or is_support_user(user):
        return True
    
    # Normal kullanıcılar için grup kontrolü
    if user.groups.exists():
        group_users = User.objects.filter(groups__in=user.groups.all()).distinct()
        return ticket.user in group_users
    
    # Grup yoksa sadece kendi ticket'ları
    return ticket.user == user

# ================================================================================
# Ana View'lar
# ================================================================================

@login_required
def ticket_list(request):
    """
    Ticket listesi - rol bazlı erişim kontrolü ve modern UI
    
    Args:
        request: HTTP request objesi
        
    Returns:
        HttpResponse: Ticket listesi sayfası
    """
    user = request.user
    
    # Kullanıcı rolüne göre ticket'ları al
    tickets = get_user_tickets_queryset(user).order_by('-created_at')
    
    # Kullanıcı rolünü belirle
    if is_admin_user(user):
        user_role = 'admin'
    elif is_support_user(user):
        user_role = 'support'
    else:
        user_role = 'customer'

    # Filtreleme parametreleri
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    # Filtreleri uygula
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)

    # Template context'i
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
    Ticket durumu değiştirme - sadece admin/support yetkili
    
    Args:
        request: HTTP request objesi
        pk: Ticket ID
        
    Returns:
        JsonResponse: İşlem sonucu
    """
    ticket = get_object_or_404(Talep, pk=pk)
    
    # JSON ve form data desteği
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Geçersiz JSON verisi.'
            }, status=400)
    else:
        new_status = request.POST.get('status')

    # Yetki kontrolü - sadece admin/support
    if not is_support_user(request.user):
        return JsonResponse({
            'success': False, 
            'message': 'Bu işlem için yetkiniz yok.'
        }, status=403)

    # Geçerli status kontrolü
    valid_statuses = [choice[0] for choice in Talep.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse({
            'success': False, 
            'message': 'Geçersiz durum.'
        }, status=400)

    # Admin olmayan kullanıcılar bazı durumlara geçemez
    if not is_admin_user(request.user) and new_status in ['wrong_section']:
        return JsonResponse({
            'success': False, 
            'message': 'Bu duruma geçiş için admin yetkisi gerekli.'
        }, status=403)

    # Durum değişikliğini kaydet
    old_status = ticket.status
    ticket.status = new_status

    # Otomatik atama mantığı
    if not ticket.assigned_to and is_support_user(request.user):
        ticket.assigned_to = request.user

    # Değişiklikleri kaydet
    ticket.save()

    # Status değişikliği için sistem yorumu ekle
    status_display = dict(Talep.STATUS_CHOICES).get(new_status, new_status)
    old_status_display = dict(Talep.STATUS_CHOICES).get(old_status, old_status)

    Comment.objects.create(
        talep=ticket,
        user=request.user,
        message=f"Durum '{old_status_display}' → '{status_display}' olarak değiştirildi."
    )

    return JsonResponse({
        'success': True,
        'status_display': status_display,
        'message': f'Talep durumu "{status_display}" olarak değiştirildi.',
        'assigned_to': ticket.assigned_to.username if ticket.assigned_to else None
    })

@login_required
def ticket_detail(request, pk):
    """
    Ticket detay sayfası ve yorum ekleme işlemleri
    Modern UI/UX ile gelişmiş kullanıcı deneyimi
    
    Args:
        request: HTTP request objesi
        pk: Ticket ID
        
    Returns:
        HttpResponse: Ticket detay sayfası
    """
    ticket = get_object_or_404(Talep, pk=pk)
    user = request.user

    # Yetki kontrolü - kullanıcı bu ticket'a erişebilir mi?
    if not _user_can_access_ticket(user, ticket):
        messages.error(request, 'Bu talebe erişim yetkiniz yok.')
        return redirect('ticket_list')

    # Ticket yorumlarını al
    comments = ticket.yorumlar.all().order_by('created_at')

    # Yorum ekleme işlemi
    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_text = request.POST.get('comment', '').strip()
        
        if comment_text:
            try:
                Comment.objects.create(
                    talep=ticket, 
                    user=user, 
                    message=comment_text
                )
                messages.success(request, 'Yorum başarıyla eklendi.')
                return redirect('ticket_detail', pk=pk)
            except Exception as e:
                messages.error(request, f'Yorum eklenirken hata oluştu: {str(e)}')
        else:
            messages.error(request, 'Yorum boş olamaz.')

    # Template context'i
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
def ticket_create(request):
    """
    Yeni ticket oluşturma - Modern form tasarımı
    
    Args:
        request: HTTP request objesi
        
    Returns:
        HttpResponse: Ticket oluşturma sayfası veya yönlendirme
    """
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            talep = form.save(commit=False)
            talep.user = request.user

            # Grup kategorisi otomatik ataması
            if request.user.groups.exists():
                group_name = request.user.groups.first().name
                category = Category.objects.filter(name=group_name).first()
                if category:
                    talep.category = category

            talep.save()

            # Başarı mesajı ve yönlendirme
            messages.success(request, 'Talep başarıyla oluşturuldu.')
            
            # Kullanıcı rolüne göre yönlendir
            if is_admin_user(request.user):
                return redirect('admin_panel')
            elif is_support_user(request.user):
                return redirect('support_panel')
            else:
                return redirect('customer_panel')
    else:
        # GET request - boş form göster
        form = TicketForm()

    # Template context'i
    context = {
        'form': form,
        'page_title': 'Yeni Talep Oluştur',
        'is_admin': is_admin_user(request.user),
        'is_support': is_support_user(request.user),
    }

    return render(request, 'tickets/ticket_create.html', context)


# ================================================================================
# Ana View'lar
# ================================================================================

@login_required
def ticket_list(request):
    """
    Ticket listesi - rol bazlı erişim kontrolü
    
    Args:
        request: HTTP request objesi
        
    Returns:
        HttpResponse: Ticket listesi sayfası
    """
    user = request.user
    
    # Kullanıcı rolüne göre ticket'ları al
    tickets = get_user_tickets_queryset(user).order_by('-created_at')
    
    # Kullanıcı rolünü belirle
    if is_admin_user(user):
        user_role = 'admin'
    elif is_support_user(user):
        user_role = 'support'
    else:
        user_role = 'customer'

    # Filtreleme parametreleri
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    # Filtreleri uygula
    if status_filter:
        tickets = tickets.filter(status=status_filter)
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
    Ticket durumu değiştirme - sadece admin/support yetkili
    
    Args:
        request: HTTP request objesi
        pk: Ticket ID
        
    Returns:
        JsonResponse: İşlem sonucu
    """
    ticket = get_object_or_404(Talep, pk=pk)
    
    # JSON ve form data desteği
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Geçersiz JSON verisi.'
            }, status=400)
    else:
        new_status = request.POST.get('status')

    # Yetki kontrolü - sadece admin/support
    if not is_support_user(request.user):
        return JsonResponse({
            'success': False, 
            'message': 'Bu işlem için yetkiniz yok.'
        }, status=403)

    # Geçerli status kontrolü
    valid_statuses = [choice[0] for choice in Talep.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse({
            'success': False, 
            'message': 'Geçersiz durum.'
        }, status=400)

    # Admin olmayan kullanıcılar bazı durumlara geçemez
    if not is_admin_user(request.user) and new_status in ['wrong_section']:
        return JsonResponse({
            'success': False, 
            'message': 'Bu duruma geçiş için admin yetkisi gerekli.'
        }, status=403)

    # Durum değişikliğini kaydet
    old_status = ticket.status
    ticket.status = new_status

        # Otomatik atama mantığı
    if not ticket.assigned_to and is_support_user(request.user):
        ticket.assigned_to = request.user

    # Değişiklikleri kaydet
    ticket.save()

    # Status değişikliği için sistem yorumu ekle
    status_display = dict(Talep.STATUS_CHOICES).get(new_status, new_status)
    old_status_display = dict(Talep.STATUS_CHOICES).get(old_status, old_status)

    Comment.objects.create(
        talep=ticket,
        user=request.user,
        message=f"Durum '{old_status_display}' → '{status_display}' olarak değiştirildi."
    )

    return JsonResponse({
        'success': True,
        'status_display': status_display,
        'message': f'Talep durumu "{status_display}" olarak değiştirildi.',
        'assigned_to': ticket.assigned_to.username if ticket.assigned_to else None
    })


@login_required
def ticket_detail(request, pk):
    """
    Ticket detay sayfası ve yorum ekleme işlemleri
    
    Args:
        request: HTTP request objesi
        pk: Ticket ID
        
    Returns:
        HttpResponse: Ticket detay sayfası
    """


def _user_can_access_ticket(user, ticket):
    """
    Kullanıcının ticket'a erişip erişemeyeceğini kontrol eder
    
    Args:
        user: Kullanıcı objesi
        ticket: Ticket objesi
        
    Returns:
        bool: Erişim izni var mı?
    """
    # Admin ve support her ticket'a erişebilir
    if is_admin_user(user) or is_support_user(user):
        return True
    
    # Normal kullanıcılar için grup kontrolü
    if user.groups.exists():
        group_users = User.objects.filter(groups__in=user.groups.all()).distinct()
        return ticket.user in group_users
    
    # Grup yoksa sadece kendi ticket'ları
    return ticket.user == user


# ================================================================================
# Ticket Detay View
# ================================================================================
@login_required
def ticket_detail(request, pk):
    """
    Ticket detay sayfası ve yorum ekleme işlemleri
    
    Args:
        request: HTTP request objesi
        pk: Ticket ID
        
    Returns:
        HttpResponse: Ticket detay sayfası
    """
    ticket = get_object_or_404(Talep, pk=pk)
    user = request.user

    # Yetki kontrolü - kullanıcı bu ticket'a erişebilir mi?
    if not _user_can_access_ticket(user, ticket):
        messages.error(request, 'Bu talebe erişim yetkiniz yok.')
        return redirect('ticket_list')

    # Ticket yorumlarını al
    comments = ticket.yorumlar.all().order_by('created_at')

    # Yorum ekleme işlemi
    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_text = request.POST.get('comment', '').strip()
        
        if comment_text:
            try:
                Comment.objects.create(
                    talep=ticket, 
                    user=user, 
                    message=comment_text
                )
                messages.success(request, 'Yorum başarıyla eklendi.')
                return redirect('ticket_detail', pk=pk)
            except Exception as e:
                messages.error(request, f'Yorum eklenirken hata oluştu: {str(e)}')
        else:
            messages.error(request, 'Yorum boş olamaz.')

    # Template context'i
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
def ticket_create(request):
    """
    Yeni ticket oluşturma
    
    Args:
        request: HTTP request objesi
        
    Returns:
        HttpResponse: Ticket oluşturma sayfası veya yönlendirme
    """
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            talep = form.save(commit=False)
            talep.user = request.user

            # Grup kategorisi otomatik ataması
            if request.user.groups.exists():
                group_name = request.user.groups.first().name
                category = Category.objects.filter(name=group_name).first()
                if category:
                    talep.category = category

            talep.save()

            # Başarı mesajı ve yönlendirme
            messages.success(request, 'Talep başarıyla oluşturuldu.')
            
            # Kullanıcı rolüne göre yönlendir
            if is_admin_user(request.user):
                return redirect('admin_panel')
            elif is_support_user(request.user):
                return redirect('support_panel')
            else:
                return redirect('customer_panel')
    else:
        # GET request - boş form göster
        form = TicketForm()

    return render(request, 'tickets/ticket_create.html', {'form': form})