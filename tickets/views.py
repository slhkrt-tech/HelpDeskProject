# tickets/views.py
# ================================================================================
# HelpDesk Ticket Yönetimi - Ana View'lar
# Ticket CRUD işlemleri, yetkilendirme ve durum yönetimi
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

User = get_user_model()  # Dinamik olarak CustomUser modelini al

# ================================================================================
# Yardımcı Fonksiyonlar - Kullanıcı Yetki Kontrolü
# ================================================================================

def is_admin_user(user):
    """
    Admin kullanıcı kontrolü
    Args:
        user: Kullanıcı objesi
    Returns:
        bool: Admin yetkisi var mı?
    """
    return user.is_superuser or user.role == 'admin'


def is_support_user(user):
    """
    Support kullanıcı kontrolü
    Args:
        user: Kullanıcı objesi
    Returns:
        bool: Support yetkisi var mı?
    """
    return user.is_superuser or user.role in ['admin', 'support']


# ================================================================================
# Ticket List View
# ================================================================================
@login_required
def ticket_list(request):
    """
    Ticket listesi:
    - Admin: Tüm talepler
    - Support: Tüm talepler (kısıtlı değişiklik)
    - Normal kullanıcı: Sadece kendi veya grubundaki talepler
    """
    user = request.user

    if is_admin_user(user):
        tickets = Talep.objects.all().order_by('-created_at')
        user_role = 'admin'
    elif is_support_user(user):
        tickets = Talep.objects.all().order_by('-created_at')
        user_role = 'support'
    else:
        # Normal kullanıcılar: kendi talepleri + grup talepleri
        if user.groups.exists():
            user_groups = user.groups.all()
            group_categories = Category.objects.filter(
                name__in=user_groups.values_list('name', flat=True)
            )
            tickets = Talep.objects.filter(
                Q(user=user) | Q(category__in=group_categories)
            ).distinct().order_by('-created_at')
        else:
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


# ================================================================================
# Ticket Durum Değiştirme (Admin/Support)
# ================================================================================
@login_required
@require_POST
def change_ticket_status(request, pk):
    ticket = get_object_or_404(Talep, pk=pk)
    new_status = request.POST.get('status')

    # Yetki kontrolü
    if not is_support_user(request.user):
        return JsonResponse({'success': False, 'error': 'Bu işlem için yetkiniz yok.'}, status=403)

    # Geçerli status kontrolü
    valid_statuses = [choice[0] for choice in Talep.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'error': 'Geçersiz durum.'}, status=400)

    # Admin olmayan kullanıcılar bazı durumlara geçemez
    if not is_admin_user(request.user) and new_status in ['wrong_section']:
        return JsonResponse({'success': False, 'error': 'Bu duruma geçiş için admin yetkisi gerekli.'}, status=403)

    old_status = ticket.status
    ticket.status = new_status

    # Ticket atanmamışsa ve support/admin değişiklik yapıyorsa otomatik ata
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


# ================================================================================
# Ticket Detay View
# ================================================================================
@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Talep, pk=pk)
    user = request.user

    # Yetki kontrolü
    if not is_admin_user(user) and not is_support_user(user):
        if user.groups.exists():
            group_users = User.objects.filter(groups__in=user.groups.all()).distinct()
            if ticket.user not in group_users:
                messages.error(request, 'Bu talebe erişim yetkiniz yok.')
                return redirect('ticket_list')
        else:
            if ticket.user != user:
                messages.error(request, 'Bu talebe erişim yetkiniz yok.')
                return redirect('ticket_list')

    # Yorumlar
    comments = ticket.yorumlar.all().order_by('created_at')

    # Yeni yorum ekleme
    if request.method == 'POST' and 'add_comment' in request.POST:
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            Comment.objects.create(talep=ticket, user=user, message=comment_text)
            messages.success(request, 'Yorum başarıyla eklendi.')
            return redirect('ticket_detail', pk=pk)
        else:
            messages.error(request, 'Yorum boş olamaz.')

    context = {
        'ticket': ticket,
        'comments': comments,
        'is_admin': is_admin_user(user),
        'is_support': is_support_user(user),
        'status_choices': Talep.STATUS_CHOICES,
        'priority_choices': Talep.PRIORITY_CHOICES,
    }

    return render(request, 'tickets/ticket_detail.html', context)


# ================================================================================
# Ticket Oluşturma View
# ================================================================================
@login_required
def ticket_create(request):
    """
    Yeni ticket oluşturma view'ı.
    - POST: Form verilerini kaydeder
    - GET: Boş form gösterir
    """
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            talep = form.save(commit=False)
            talep.user = request.user

            # Grup kategorisi otomatik ata
            if request.user.groups.exists():
                group_name = request.user.groups.first().name
                category = Category.objects.filter(name=group_name).first()
                if category:
                    talep.category = category

            talep.save()

            # Kullanıcı rolüne göre yönlendir
            if request.user.role == 'admin':
                return redirect('admin_panel')
            elif request.user.role == 'support':
                return redirect('support_panel')
            else:
                return redirect('customer_panel')
    else:
        form = TicketForm()

    return render(request, 'tickets/ticket_create.html', {'form': form})


# ================================================================================
# DEPRECATED FUNCTIONS
# Accounts app'ine taşındı, burada gereksiz
# ================================================================================
# signup ve add_user_to_group artık accounts.views içinde