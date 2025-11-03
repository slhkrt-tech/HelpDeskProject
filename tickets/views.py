# tickets/views.py
"""
HelpDesk Ticket Yönetimi - Ana View'lar
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
from django import forms
from django.db.models import Count
import json

# Yerel model ve form importları
from .models import Talep, Category, Comment
from .forms import TicketForm

# Model alias'ları
Ticket = Talep  # Kolay kullanım için alias

# Dinamik olarak CustomUser modelini al
User = get_user_model()

# ================================================================================
# Yardımcı Fonksiyonlar
# ================================================================================

def is_admin_user(user):
    """Admin kullanıcı kontrolü"""
    return user.is_superuser or getattr(user, 'role', None) == 'admin'

def is_support_user(user):
    """Support kullanıcı kontrolü (admin + support)"""
    return is_admin_user(user) or getattr(user, 'role', None) == 'support'

def get_user_tickets_queryset(user):
    """Kullanıcı rolüne göre ticket'ları filtrele"""
    if is_admin_user(user):
        return Talep.objects.all()
    elif is_support_user(user):
        return Talep.objects.all()
    else:
        return Talep.objects.filter(user=user)

# ================================================================================
# Ana View'lar
# ================================================================================

@login_required
def ticket_list(request):
    """Ticket listesi - rol bazlı erişim kontrolü ve modern UI"""
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
    category_filter = request.GET.get('category')
    assigned_filter = request.GET.get('assigned_to')

    # Filtreleme uygula
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if category_filter:
        tickets = tickets.filter(category__id=category_filter)
    if assigned_filter:
        tickets = tickets.filter(assigned_to__id=assigned_filter)

    # Seçenekler için veriler
    categories = Category.objects.all()
    
    # Admin/Support kullanıcıları görebilsin
    if is_support_user(user):
        support_users = User.objects.filter(role__in=['admin', 'support'])
    else:
        support_users = []

    # İstatistikler
    total_tickets = tickets.count()
    open_tickets = tickets.filter(status__in=['open', 'in_progress']).count()
    closed_tickets = tickets.filter(status='closed').count()

    context = {
        'tickets': tickets,
        'user_role': user_role,
        'categories': categories,
        'support_users': support_users,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'assigned_filter': assigned_filter,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
    }

    return render(request, 'tickets/ticket_list.html', context)

@login_required
def ticket_detail(request, pk):
    """Ticket detay sayfası ve yorum ekleme"""
    ticket = get_object_or_404(Talep, pk=pk)
    user = request.user
    
    # Yetki kontrolü
    if not is_support_user(user) and ticket.user != user:
        messages.error(request, 'Bu talebe erişim yetkiniz bulunmuyor.')
        return redirect('ticket_list')
    
    # Kullanıcı rolünü belirle
    if is_admin_user(user):
        user_role = 'admin'
    elif is_support_user(user):
        user_role = 'support'
    else:
        user_role = 'customer'

    # POST request - Yorum ekleme
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        
        if comment_text:
            Comment.objects.create(
                talep=ticket,
                user=user,
                message=comment_text
            )
            messages.success(request, 'Yorumunuz başarıyla eklendi.')
            return redirect('ticket_detail', pk=pk)

    # Yorumları getir
    comments = Comment.objects.filter(talep=ticket).order_by('created_at')
    
    # Atanabilir kullanıcılar (sadece admin/support görebilir)
    if is_support_user(user):
        assignable_users = User.objects.filter(role__in=['admin', 'support'])
    else:
        assignable_users = []

    context = {
        'ticket': ticket,
        'comments': comments,
        'user_role': user_role,
        'assignable_users': assignable_users,
    }

    return render(request, 'tickets/ticket_detail.html', context)

@login_required
def ticket_create(request):
    """Yeni ticket oluşturma"""
    user = request.user
    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = user
            
            # Müşteri sadece kendine ticket açabilir
            if not is_support_user(user):
                ticket.assigned_to = None
            
            ticket.save()
            messages.success(request, f'Talep başarıyla oluşturuldu! Talep No: {ticket.talep_numarasi}')
            return redirect('ticket_detail', pk=ticket.pk)
        else:
            messages.error(request, 'Lütfen formu doğru şekilde doldurun.')
    else:
        form = TicketForm()
        
        # Müşteri kullanıcıları için assigned_to alanını gizle
        if not is_support_user(user):
            form.fields['assigned_to'].widget = forms.HiddenInput()

    # Kullanıcı rolünü belirle
    if is_admin_user(user):
        user_role = 'admin'
    elif is_support_user(user):
        user_role = 'support'
    else:
        user_role = 'customer'

    context = {
        'form': form,
        'user_role': user_role,
    }

    return render(request, 'tickets/ticket_create.html', context)

@require_POST
@login_required
def change_ticket_status(request, pk):
    """Ticket durumunu değiştir (AJAX)"""
    # Sadece admin/support kullanıcıları
    if not is_support_user(request.user):
        return JsonResponse({
            'status': 'error',
            'message': 'Bu işlem için yetkiniz bulunmuyor.'
        }, status=403)

    ticket = get_object_or_404(Talep, pk=pk)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Geçerli durum değerleri
        valid_statuses = ['new', 'seen', 'open', 'pending', 'in_progress', 'resolved', 'closed', 'wrong_section']
        
        if new_status not in valid_statuses:
            return JsonResponse({
                'status': 'error',
                'message': 'Geçersiz durum değeri.'
            })
        
        old_status = ticket.status
        ticket.status = new_status
        ticket.save()
        
        # Durum değişikliği yorumu ekle
        status_display = dict(ticket.STATUS_CHOICES).get(new_status, new_status)
        Comment.objects.create(
            talep=ticket,
            user=request.user,
            message=f"🔄 Durum değiştirildi: {dict(ticket.STATUS_CHOICES).get(old_status, old_status)} → {status_display}"
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Durum "{status_display}" olarak güncellendi.',
            'new_status': new_status
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Geçersiz JSON verisi.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Bir hata oluştu: {str(e)}'
        }, status=500)

@require_POST
@login_required
def update_ticket_assignment(request, pk):
    """Ticket atamasını güncelle (AJAX)"""
    # Sadece admin/support kullanıcıları
    if not is_support_user(request.user):
        return JsonResponse({
            'status': 'error',
            'message': 'Bu işlem için yetkiniz bulunmuyor.'
        }, status=403)

    ticket = get_object_or_404(Talep, pk=pk)
    
    try:
        data = json.loads(request.body)
        assigned_to_id = data.get('assigned_to_id')
        
        if assigned_to_id:
            assigned_user = get_object_or_404(User, pk=assigned_to_id)
            old_assigned = ticket.assigned_to
            ticket.assigned_to = assigned_user
            ticket.save()
            
            # Atama değişikliği yorumu ekle
            if old_assigned:
                message = f"👤 Atama değiştirildi: {old_assigned.username} → {assigned_user.username}"
            else:
                message = f"👤 Talep atandı: {assigned_user.username}"
                
            Comment.objects.create(
                talep=ticket,
                user=request.user,
                message=message
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f'Talep {assigned_user.username} kullanıcısına atandı.',
                'assigned_to': assigned_user.username
            })
        else:
            old_assigned = ticket.assigned_to
            ticket.assigned_to = None
            ticket.save()
            
            if old_assigned:
                Comment.objects.create(
                    talep=ticket,
                    user=request.user,
                    message=f"👤 Atama kaldırıldı: {old_assigned.username}"
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Talep ataması kaldırıldı.',
                'assigned_to': None
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Geçersiz JSON verisi.'
        }, status=400)
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Kullanıcı bulunamadı.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Bir hata oluştu: {str(e)}'
        }, status=500)

# ================================================================================
# Ticket Admin Yönetimi
# ================================================================================

@login_required
def tickets_admin_view(request):
    """Ticket admin yönetimi sayfası"""
    user_role = getattr(request.user, 'role', '').lower()
    if user_role not in ['admin', 'support']:
        return redirect('/accounts/login/')
    
    # Ticket istatistikleri
    ticket_stats = {
        'total_tickets': Ticket.objects.count(),
        'open_tickets': Ticket.objects.filter(status='open').count(),
        'in_progress_tickets': Ticket.objects.filter(status='in_progress').count(),
        'closed_tickets': Ticket.objects.filter(status='closed').count(),
        'tickets_by_priority': Ticket.objects.values('priority').annotate(count=Count('id')),
        'tickets_by_category': Ticket.objects.values('category__name').annotate(count=Count('id')),
    }
    
    # Son ticket'lar
    recent_tickets = Ticket.objects.select_related('user', 'assigned_to', 'category').order_by('-created_at')[:10]
    
    context = {
        'current_user': request.user,
        'user_role': user_role,
        'ticket_stats': ticket_stats,
        'recent_tickets': recent_tickets,
        'panel_title': 'Ticket Yönetimi',
        'page_title': 'Ticket Yönetimi'
    }
    return render(request, 'tickets/tickets_admin.html', context)

@login_required
def ticket_categories_view(request):
    """Ticket kategorileri yönetimi sayfası"""
    user_role = getattr(request.user, 'role', '').lower()
    if user_role not in ['admin', 'support']:
        return redirect('/accounts/login/')
    
    categories = Category.objects.annotate(ticket_count=Count('talep')).order_by('name')
    
    # Ortalama ticket sayısını hesapla
    total_tickets = sum(category.ticket_count for category in categories)
    average_tickets = round(total_tickets / len(categories), 1) if categories else 0
    
    context = {
        'current_user': request.user,
        'user_role': user_role,
        'categories': categories,
        'total_tickets': total_tickets,
        'average_tickets': average_tickets,
        'panel_title': 'Kategori Yönetimi',
        'page_title': 'Kategori Yönetimi'
    }
    return render(request, 'tickets/ticket_categories.html', context)

@login_required
@require_POST
def update_ticket_status(request):
    """
    Admin ve Support kullanıcıları için ticket durumu güncelleme
    AJAX endpoint
    """
    # Yetki kontrolü
    if not hasattr(request.user, 'role') or request.user.role not in ['admin', 'support']:
        return JsonResponse({'success': False, 'message': 'Bu işlemi yapmaya yetkiniz yok.'}, status=403)
    
    try:
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')
        new_status = data.get('new_status')
        
        if not ticket_id or not new_status:
            return JsonResponse({'success': False, 'message': 'Eksik bilgi gönderildi.'}, status=400)
        
        # Ticket'ı bul
        ticket = get_object_or_404(Talep, pk=ticket_id)
        
        # Geçerli status seçenekleri
        valid_statuses = [choice[0] for choice in Talep.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'message': 'Geçersiz durum.'}, status=400)
        
        # Eski durum
        old_status = ticket.get_status_display()
        
        # Durumu güncelle
        ticket.status = new_status
        ticket.save()
        
        # Yeni durum
        new_status_display = ticket.get_status_display()
        
        # Başarılı response
        return JsonResponse({
            'success': True,
            'message': f'Ticket durumu "{old_status}" → "{new_status_display}" olarak güncellendi.',
            'new_status': new_status,
            'new_status_display': new_status_display,
            'ticket_id': ticket_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Geçersiz JSON verisi.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Bir hata oluştu: {str(e)}'}, status=500)