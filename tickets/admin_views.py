from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Talep, Category
import logging
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Comment

User = get_user_model()

logger = logging.getLogger('helpdesk.admin_actions')


# Basit bir staff-only panel: Supervisor/staff veya superuser kullanabilir
def staff_required(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name='Supervisor').exists()


@user_passes_test(staff_required)
def panel_list(request):
    """Talepleri listeleyen ve seçilen taleplere toplu işlem uygulayan görünüm.

    Özellikler:
    - Filtreleme: status ve category
    - Metin arama: title veya description içinde
    - Sayfalama
    - Toplu işlem (POST ile)
    """
    qs = Talep.objects.filter(is_deleted=False).order_by('-created_at')

    # Filtreler
    status = request.GET.get('status')
    category_id = request.GET.get('category')
    q = request.GET.get('q')

    if status:
        qs = qs.filter(status=status)
    if category_id:
        qs = qs.filter(category_id=category_id)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

    # POST: toplu işlemler
    if request.method == 'POST':
        action = request.POST.get('action')
        selected = request.POST.getlist('selected')
        if selected and action:
            sel_qs = Talep.objects.filter(pk__in=selected)
            # delete eylemi yalnızca Supervisor grubuna veya superuser'a izinli
            if action == 'delete' and not (request.user.is_superuser or request.user.groups.filter(name='Supervisor').exists()):
                # yetkisiz silme denemesi
                logger.warning(f"Unauthorized delete attempt by user={request.user.pk} on ids={selected}")
                messages.error(request, "Bu işlemi gerçekleştirmek için yetkiniz yok.")
            else:
                if action == 'close':
                    count = sel_qs.update(status='closed')
                    logger.info(f"User {request.user.pk} set {count} tickets to closed: ids={selected}")
                    messages.success(request, f"{count} talep kapatıldı.")
                elif action == 'pending':
                    count = sel_qs.update(status='pending')
                    logger.info(f"User {request.user.pk} set {count} tickets to pending: ids={selected}")
                    messages.success(request, f"{count} talep beklemeye alındı.")
                elif action == 'open':
                    count = sel_qs.update(status='open')
                    logger.info(f"User {request.user.pk} set {count} tickets to open: ids={selected}")
                    messages.success(request, f"{count} talep açık olarak işaretlendi.")
                elif action == 'wrong_section':
                    count = sel_qs.update(status='wrong_section')
                    logger.info(f"User {request.user.pk} set {count} tickets to wrong_section: ids={selected}")
                    messages.success(request, f"{count} talep 'Yanlış Bölüm / Kapatıldı' olarak işaretlendi.")
                elif action == 'delete':
                    # soft-delete: is_deleted=True
                    count = sel_qs.update(is_deleted=True)
                    logger.info(f"User {request.user.pk} soft-deleted {count} tickets: ids={selected}")
                    messages.success(request, f"{count} talep arşivlendi (silindi).")
        return redirect('admin_panel')

    # Sayfalama
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    context = {
        'tickets': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'categories': categories,
        'filters': {'status': status, 'category': category_id, 'q': q},
        'can_delete': request.user.is_superuser or request.user.groups.filter(name='Supervisor').exists(),
    }
    return render(request, 'tickets/admin_panel/list.html', context)


@user_passes_test(staff_required)
def panel_detail(request, pk):
    """Tek bir talep için detay ve hızlı işlem görünümü.

    - POST: tekil işlem (status değiştirme veya silme) uygular.
    """
    ticket = get_object_or_404(Talep, pk=pk, is_deleted=False)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ('close', 'pending', 'open', 'wrong_section'):
            ticket.status = action if action != 'close' else 'closed'
            ticket.save()
            logger.info(f"User {request.user.pk} set ticket {ticket.pk} to {ticket.status}")
            messages.success(request, f"Talep durumu '{ticket.get_status_display()}' olarak güncellendi.")
        elif action == 'delete':
            # soft-delete: is_deleted flag set; delete yalnızca Supervisor veya superuser
            if not (request.user.is_superuser or request.user.groups.filter(name='Supervisor').exists()):
                logger.warning(f"Unauthorized delete attempt on ticket {ticket.pk} by user {request.user.pk}")
                messages.error(request, "Bu talebi silmek için yetkiniz yok.")
            else:
                ticket.is_deleted = True
                ticket.save()
                logger.info(f"User {request.user.pk} soft-deleted ticket {ticket.pk}")
                messages.success(request, "Talep arşivlendi (silindi).")
                return redirect('admin_panel')
        return redirect('admin_panel_detail', pk=pk)

    return render(request, 'tickets/admin_panel/detail.html', {'ticket': ticket})


@user_passes_test(staff_required)
def admin_index(request):
    """Özel admin panelinin ana sayfası - sekmeli gezinme için küçük index."""
    counts = {
        'tickets': Talep.objects.filter(is_deleted=False).count(),
        'users': User.objects.count(),
        'groups': Group.objects.count(),
        'comments': Comment.objects.count(),
    }
    return render(request, 'tickets/admin_panel/index.html', {'counts': counts})


@user_passes_test(staff_required)
def users_list(request):
    users = User.objects.all().order_by('id')
    return render(request, 'tickets/admin_panel/users.html', {'users': users})


@user_passes_test(staff_required)
def groups_list(request):
    groups = Group.objects.all().order_by('id')
    return render(request, 'tickets/admin_panel/groups.html', {'groups': groups})


@user_passes_test(staff_required)
def comments_list(request):
    comments = Comment.objects.select_related('talep', 'user').order_by('-created_at')
    return render(request, 'tickets/admin_panel/comments.html', {'comments': comments})
