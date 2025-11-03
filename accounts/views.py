# accounts/views.py
"""
HelpDesk Kullanıcı Yönetimi - Düzenlenmiş ve Yorumlu
========================================
Session tabanlı kimlik doğrulama, modern UI/UX, role bazlı erişim
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
from datetime import timedelta

import logging
logger = logging.getLogger(__name__)

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import LoginSerializer, UserSerializer
from .models import CustomAuthToken, CustomUser

# Tickets modelini import et
try:
    from tickets.models import Ticket
except ImportError:
    Ticket = None

# =========================
# Yardımcı Fonksiyonlar
# =========================

def get_user_by_token(token_key):
    """Token ile kullanıcı getir, süresi dolmuşsa sil"""
    try:
        token = CustomAuthToken.objects.select_related('user').get(key=token_key)
        if token.is_expired():
            token.delete()
            return None
        return token.user
    except CustomAuthToken.DoesNotExist:
        return None

# =========================
# Ana Sayfa & Panel View'ları
# =========================

def home_view(request):
    """Ana sayfa, role göre yönlendirme"""
    if request.user.is_authenticated:
        role = getattr(request.user, 'role', 'customer').lower()
        if role == 'admin':
            return redirect('/accounts/admin-panel/')
        elif role == 'support':
            return redirect('/accounts/support-panel/')
        return redirect('/accounts/customer-panel/')

    return render(request, 'tickets/home.html', {'page_title': 'HelpDesk Sistemi', 'is_home': True})

def custom_login_view(request):
    """Login sayfası"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user and user.is_active:
                login(request, user)
                token, created = CustomAuthToken.objects.get_or_create(user=user)
                if not created:
                    token.created = timezone.now()
                    token.save()

                redirect_map = {'admin': '/accounts/admin-panel/',
                                'support': '/accounts/support-panel/',
                                'customer': '/accounts/customer-panel/'}
                return redirect(redirect_map.get(user.role, '/accounts/customer-panel/'))
            messages.error(request, 'Kullanıcı adı veya şifre hatalı / Hesap aktif değil.')
        else:
            messages.error(request, 'Kullanıcı adı ve şifre gerekli.')

    return render(request, 'accounts/login.html')

@login_required
def admin_panel_view(request):
    """Admin paneli"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')

    # Kullanıcı istatistikleri
    total_users = CustomUser.objects.count()
    admin_users = CustomUser.objects.filter(role='admin').count()
    support_users = CustomUser.objects.filter(role='support').count()
    customer_users = CustomUser.objects.filter(role='customer').count()
    
    # Talep istatistikleri
    try:
        from tickets.models import Talep
        total_tickets = Talep.objects.count()
        open_tickets = Talep.objects.filter(status='open').count()
        in_progress_tickets = Talep.objects.filter(status='in_progress').count()
        resolved_tickets = Talep.objects.filter(status='resolved').count()
        
        # Son talepler
        recent_tickets = Talep.objects.order_by('-created_at')[:5]
        
        # Bu hafta/ay talepler
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        month_ago = timezone.now() - timedelta(days=30)
        
        tickets_this_week = Talep.objects.filter(created_at__gte=week_ago).count()
        tickets_this_month = Talep.objects.filter(created_at__gte=month_ago).count()
        
    except ImportError:
        # Tickets app yoksa default değerler
        total_tickets = 0
        open_tickets = 0
        in_progress_tickets = 0
        resolved_tickets = 0
        recent_tickets = []
        tickets_this_week = 0
        tickets_this_month = 0

    # Token istatistikleri
    from django.utils import timezone
    active_tokens = CustomAuthToken.objects.filter(created__gte=timezone.now() - timedelta(days=30)).count()
    expired_tokens = CustomAuthToken.objects.filter(created__lt=timezone.now() - timedelta(days=30)).count()
    
    # Grup sayısı
    from django.contrib.auth.models import Group
    total_groups = Group.objects.count()
    
    # Son kullanıcılar
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]

    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Yönetim Paneli',
        'page_title': 'Admin Panel',
        
        # Kullanıcı istatistikleri
        'total_users': total_users,
        'admin_users': admin_users,
        'support_users': support_users,
        'customer_users': customer_users,
        'recent_users': recent_users,
        
        # Talep istatistikleri
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'recent_tickets': recent_tickets,
        'tickets_this_week': tickets_this_week,
        'tickets_this_month': tickets_this_month,
        
        # Token ve grup istatistikleri
        'active_tokens': active_tokens,
        'expired_tokens': expired_tokens,
        'total_groups': total_groups,
    }
    return render(request, 'accounts/admin_panel.html', context)

@login_required
def support_panel_view(request):
    """Support panel"""
    if getattr(request.user, 'role', '').lower() not in ['admin', 'support']:
        return redirect('/accounts/login/')
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Support Panel',
        'page_title': 'Support Panel'
    }
    return render(request, 'accounts/support_panel.html', context)

@login_required
def customer_panel_view(request):
    """Customer panel"""
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Müşteri Panel',
        'page_title': 'Müşteri Panel'
    }
    return render(request, 'accounts/customer_panel_modern.html', context)

# =========================
# Admin Kullanıcı Yönetimi
# =========================

@login_required
def admin_users_view(request):
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'accounts/admin_users.html', {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'users': users,
        'panel_title': 'Kullanıcı Yönetimi',
        'page_title': 'Kullanıcı Yönetimi'
    })

@login_required
def admin_user_create_view(request):
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')

    if request.method == 'POST':
        data = {k: request.POST.get(k) for k in ['username', 'email', 'password', 'role']}
        data['is_active'] = request.POST.get('is_active') == 'on'
        try:
            CustomUser.objects.create_user(**data)
            messages.success(request, f'Kullanıcı "{data["username"]}" oluşturuldu.')
            return redirect('admin_users')
        except Exception as e:
            messages.error(request, f'Hata: {e}')

    return render(request, 'accounts/admin_user_create.html', {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Yeni Kullanıcı',
        'page_title': 'Yeni Kullanıcı'
    })

# =========================
# Customer Profil
# =========================

@login_required
def customer_profile_view(request):
    return render(request, 'accounts/customer_profile.html', {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'page_title': 'Profil'
    })

@login_required
def customer_profile_edit_view(request):
    if request.method == 'POST':
        for field in ['email', 'first_name', 'last_name']:
            setattr(request.user, field, request.POST.get(field, getattr(request.user, field)))
        try:
            request.user.save()
            messages.success(request, 'Profil güncellendi.')
        except Exception as e:
            messages.error(request, f'Hata: {e}')
        return redirect('customer_profile')
    return render(request, 'accounts/customer_profile_edit.html', {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'page_title': 'Profil Düzenle'
    })

@login_required
def customer_change_password_view(request):
    if request.method == 'POST':
        old = request.POST.get('old_password')
        new = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        if not request.user.check_password(old):
            messages.error(request, 'Mevcut şifre hatalı.')
        elif new != confirm:
            messages.error(request, 'Yeni şifreler eşleşmiyor.')
        elif len(new) < 6:
            messages.error(request, 'Şifre en az 6 karakter.')
        else:
            request.user.set_password(new)
            request.user.save()
            messages.success(request, 'Şifre değiştirildi.')
            return redirect('customer_profile')
    return render(request, 'accounts/customer_change_password.html', {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'page_title': 'Şifre Değiştir'
    })

# =========================
# Logout & Signup
# =========================

def custom_logout_view(request):
    if request.user.is_authenticated:
        CustomAuthToken.objects.filter(user=request.user).delete()
    logout(request)
    messages.success(request, 'Başarıyla çıkış yapıldı.')
    return redirect('/accounts/login/')

def signup_view(request):
    return render(request, 'registration/signup.html')

# =========================
# Admin User Management (CRUD)
# =========================

@login_required
def admin_user_edit_view(request, user_id):
    """Admin - Kullanıcı düzenleme"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Kullanıcı bulunamadı.')
        return redirect('admin_users')
    
    if request.method == 'POST':
        # Form verilerini güncelle
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        
        # Superuser'ların role'ünü değiştirmeyi engelle
        if not user.is_superuser:
            user.role = request.POST.get('role', user.role)
        else:
            user.role = 'admin'  # Superuser'lar her zaman admin olmalı
        
        user.is_active = request.POST.get('is_active') == 'on'
        
        # Şifre değişikliği
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
        
        try:
            user.save()
            messages.success(request, f'Kullanıcı "{user.username}" güncellendi.')
            return redirect('admin_users')
        except Exception as e:
            messages.error(request, f'Hata: {e}')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'edit_user': user,
        'panel_title': 'Kullanıcı Düzenle',
        'page_title': f'Kullanıcı Düzenle - {user.username}'
    }
    return render(request, 'accounts/admin_user_edit.html', context)

@login_required
def admin_user_delete_view(request, user_id):
    """Admin - Kullanıcı silme"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Kullanıcı bulunamadı.')
        return redirect('admin_users')
    
    # Super admin silinemez
    if user.is_superuser:
        messages.error(request, 'Super admin kullanıcı silinemez.')
        return redirect('admin_users')
    
    # Kendini silememez
    if user.id == request.user.id:
        messages.error(request, 'Kendi hesabınızı silemezsiniz.')
        return redirect('admin_users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'Kullanıcı "{username}" silindi.')
        return redirect('admin_users')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'delete_user': user,
        'panel_title': 'Kullanıcı Sil',
        'page_title': f'Kullanıcı Sil - {user.username}'
    }
    return render(request, 'accounts/admin_user_delete.html', context)

# =========================
# Yeni Admin İşlevleri
# =========================

@login_required
def admin_groups_view(request):
    """Grup yönetimi sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    from django.contrib.auth.models import Group
    groups = Group.objects.all().order_by('name')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'groups': groups,
        'panel_title': 'Grup Yönetimi',
        'page_title': 'Grup Yönetimi'
    }
    return render(request, 'accounts/admin_groups.html', context)

@login_required
def admin_group_create_view(request):
    """Yeni grup oluşturma sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    if request.method == 'POST':
        group_name = request.POST.get('name', '').strip()
        permissions_ids = request.POST.getlist('permissions')
        
        if group_name:
            try:
                # Yeni grup oluştur
                group = Group.objects.create(name=group_name)
                
                # İzinleri ekle
                if permissions_ids:
                    permissions = Permission.objects.filter(id__in=permissions_ids)
                    group.permissions.set(permissions)
                
                messages.success(request, f'"{group_name}" grubu başarıyla oluşturuldu!')
                return redirect('admin_groups')
            except Exception as e:
                messages.error(request, f'Grup oluşturulurken hata: {str(e)}')
        else:
            messages.error(request, 'Grup adı gereklidir!')
    
    # Tüm izinleri getir
    permissions = Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'permissions': permissions,
        'panel_title': 'Yeni Grup Oluştur',
        'page_title': 'Yeni Grup Oluştur'
    }
    return render(request, 'accounts/admin_group_create.html', context)

@login_required
def admin_group_edit_view(request, group_id):
    """Grup düzenleme sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        messages.error(request, 'Grup bulunamadı!')
        return redirect('admin_groups')
    
    if request.method == 'POST':
        group_name = request.POST.get('name', '').strip()
        permissions_ids = request.POST.getlist('permissions')
        
        if group_name:
            try:
                group.name = group_name
                group.save()
                
                # İzinleri güncelle
                if permissions_ids:
                    permissions = Permission.objects.filter(id__in=permissions_ids)
                    group.permissions.set(permissions)
                else:
                    group.permissions.clear()
                
                messages.success(request, f'"{group_name}" grubu başarıyla güncellendi!')
                return redirect('admin_groups')
            except Exception as e:
                messages.error(request, f'Grup güncellenirken hata: {str(e)}')
        else:
            messages.error(request, 'Grup adı gereklidir!')
    
    # Tüm izinleri getir
    permissions = Permission.objects.select_related('content_type').order_by('content_type__app_label', 'codename')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'group': group,
        'permissions': permissions,
        'panel_title': f'Grup Düzenle: {group.name}',
        'page_title': f'Grup Düzenle: {group.name}'
    }
    return render(request, 'accounts/admin_group_edit.html', context)

@login_required
def admin_group_delete_view(request, group_id):
    """Grup silme işlemi"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    try:
        group = Group.objects.get(id=group_id)
        group_name = group.name
        group.delete()
        messages.success(request, f'"{group_name}" grubu başarıyla silindi!')
    except Group.DoesNotExist:
        messages.error(request, 'Grup bulunamadı!')
    except Exception as e:
        messages.error(request, f'Grup silinirken hata: {str(e)}')
    
    return redirect('admin_groups')

@login_required
def admin_permissions_view(request):
    """Yetki yönetimi sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    from django.contrib.auth.models import Permission
    permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'permissions': permissions,
        'panel_title': 'Yetki Yönetimi',
        'page_title': 'Yetki Yönetimi'
    }
    return render(request, 'accounts/admin_permissions.html', context)

@login_required
@login_required
def admin_reports_view(request):
    """Rapor sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    # Ticket modeli varsa raporları oluştur
    if Ticket:
        from datetime import datetime
        
        # Rapor verileri
        now = datetime.now()
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)
        
        report_data = {
            'total_users': CustomUser.objects.count(),
            'total_tickets': Ticket.objects.count(),
            'tickets_last_week': Ticket.objects.filter(created_at__gte=last_week).count(),
            'tickets_last_month': Ticket.objects.filter(created_at__gte=last_month).count(),
            'tickets_by_status': Ticket.objects.values('status').annotate(count=Count('id')),
            'tickets_by_priority': Ticket.objects.values('priority').annotate(count=Count('id')),
            'users_by_role': CustomUser.objects.values('role').annotate(count=Count('id')),
        }
    else:
        # Ticket modeli yoksa temel raporlar
        report_data = {
            'total_users': CustomUser.objects.count(),
            'total_tickets': 0,
            'tickets_last_week': 0,
            'tickets_last_month': 0,
            'tickets_by_status': [],
            'tickets_by_priority': [],
            'users_by_role': CustomUser.objects.values('role').annotate(count=Count('id')),
        }
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'report_data': report_data,
        'panel_title': 'Sistem Raporları',
        'page_title': 'Sistem Raporları'
    }
    return render(request, 'accounts/admin_reports.html', context)

@login_required
def admin_analytics_view(request):
    """Analitik sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Sistem Analitikleri',
        'page_title': 'Sistem Analitikleri'
    }
    return render(request, 'accounts/admin_analytics.html', context)

@login_required
def admin_settings_view(request):
    """Sistem ayarları sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Sistem Ayarları',
        'page_title': 'Sistem Ayarları'
    }
    return render(request, 'accounts/admin_settings.html', context)

@login_required
def admin_logs_view(request):
    """Sistem logları sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Sistem Logları',
        'page_title': 'Sistem Logları'
    }
    return render(request, 'accounts/admin_logs.html', context)

@login_required
def admin_tokens_view(request):
    """API token yönetimi sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    tokens = CustomAuthToken.objects.all().order_by('-created')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'tokens': tokens,
        'panel_title': 'API Token Yönetimi',
        'page_title': 'API Token Yönetimi'
    }
    return render(request, 'accounts/admin_tokens.html', context)

@login_required
def admin_backup_view(request):
    """Sistem yedekleme sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Sistem Yedekleme',
        'page_title': 'Sistem Yedekleme'
    }
    return render(request, 'accounts/admin_backup.html', context)

@login_required
def admin_maintenance_view(request):
    """Sistem bakım sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Sistem Bakım',
        'page_title': 'Sistem Bakım'
    }
    return render(request, 'accounts/admin_maintenance.html', context)

@login_required
def admin_bulk_import_view(request):
    """Toplu kullanıcı içe aktarma sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Toplu İçe Aktarma',
        'page_title': 'Toplu İçe Aktarma'
    }
    return render(request, 'accounts/admin_bulk_import.html', context)

@login_required
def admin_notifications_view(request):
    """Bildirim gönderme sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Bildirim Yönetimi',
        'page_title': 'Bildirim Yönetimi'
    }
    return render(request, 'accounts/admin_notifications.html', context)

@login_required
def admin_cache_view(request):
    """Cache yönetimi sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Cache Yönetimi',
        'page_title': 'Cache Yönetimi'
    }
    return render(request, 'accounts/admin_cache.html', context)

@login_required
def admin_export_view(request):
    """Veri dışa aktarma sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Veri Dışa Aktarma',
        'page_title': 'Veri Dışa Aktarma'
    }
    return render(request, 'accounts/admin_export.html', context)

# =========================
# API Endpoints
# =========================

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def signup_api_view(request):
    """Kullanıcı kayıt API endpoint'i"""
    try:
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '')
        confirm_password = request.data.get('confirm_password', '')
        
        # Validasyon
        if not all([username, email, password, confirm_password]):
            logger.debug(f"Signup validation failed: Missing fields - IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
            return Response({
                'success': False,
                'message': 'Tüm alanları doldurun.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if password != confirm_password:
            logger.debug(f"Signup validation failed: Password mismatch for user '{username}' - IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
            return Response({
                'success': False,
                'message': 'Şifreler eşleşmiyor.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 8:
            logger.debug(f"Signup validation failed: Password too short for user '{username}' - IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
            return Response({
                'success': False,
                'message': 'Şifre en az 8 karakter olmalıdır.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kullanıcı adı kontrolü
        if CustomUser.objects.filter(username=username).exists():
            logger.debug(f"Signup validation failed: Duplicate username '{username}' - IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
            return Response({
                'success': False,
                'message': 'Bu kullanıcı adı zaten kullanılıyor.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Email kontrolü
        if CustomUser.objects.filter(email=email).exists():
            logger.debug(f"Signup validation failed: Duplicate email '{email}' - IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
            return Response({
                'success': False,
                'message': 'Bu e-posta adresi zaten kayıtlı.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kullanıcı oluştur
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='customer'  # Varsayılan olarak customer
        )
        
        # Otomatik giriş yap
        login(request, user)
        
        logger.info(f"New user registered and logged in successfully: '{username}' ({email}) - IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
        return Response({
            'success': True,
            'message': 'Hesabınız başarıyla oluşturuldu ve giriş yapıldı!',
            'redirect_url': '/accounts/customer-panel/'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Signup API error: {str(e)} - IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
        return Response({
            'success': False,
            'message': 'Bir hata oluştu. Lütfen tekrar deneyin.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
