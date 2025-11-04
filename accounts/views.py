# accounts/views.py
"""
Yardım Masası Kullanıcı Yönetimi - Düzenlenmiş ve Yorumlu
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

    return render(request, 'tickets/home.html', {'page_title': 'Yardım Masası Sistemi', 'is_home': True})

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
    """Admin paneli - Güncel dinamik veriler"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')

    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count, Q
    
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Kullanıcı istatistikleri (güncel)
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    admin_users = CustomUser.objects.filter(role='admin').count()
    support_users = CustomUser.objects.filter(role='support').count()
    customer_users = CustomUser.objects.filter(role='customer').count()
    
    # Bugün katılan kullanıcılar
    users_today = CustomUser.objects.filter(date_joined__date=today).count()
    users_yesterday = CustomUser.objects.filter(date_joined__date=yesterday).count()
    users_this_week = CustomUser.objects.filter(date_joined__gte=week_ago).count()
    users_this_month = CustomUser.objects.filter(date_joined__gte=month_ago).count()
    
    # Talep istatistikleri (güncel)
    try:
        from tickets.models import Talep
        total_tickets = Talep.objects.count()
        
        # Status bazlı sayımlar
        open_tickets = Talep.objects.filter(status='open').count()
        in_progress_tickets = Talep.objects.filter(status='in_progress').count()
        resolved_tickets = Talep.objects.filter(status='resolved').count()
        closed_tickets = Talep.objects.filter(status='closed').count()
        pending_tickets = Talep.objects.filter(status='pending').count()
        
        # Priority bazlı sayımlar
        high_priority = Talep.objects.filter(priority='high').count()
        medium_priority = Talep.objects.filter(priority='medium').count()
        low_priority = Talep.objects.filter(priority='low').count()
        
        # Zaman bazlı talepler
        tickets_today = Talep.objects.filter(created_at__date=today).count()
        tickets_yesterday = Talep.objects.filter(created_at__date=yesterday).count()
        tickets_this_week = Talep.objects.filter(created_at__gte=week_ago).count()
        tickets_this_month = Talep.objects.filter(created_at__gte=month_ago).count()
        
        # Büyüme oranları
        ticket_daily_growth = ((tickets_today - tickets_yesterday) / max(tickets_yesterday, 1)) * 100
        
        # Son talepler (güncel)
        recent_tickets = Talep.objects.select_related('user', 'category').order_by('-created_at')[:10]
        
        # Kritik talepler (yüksek öncelikli ve açık)
        critical_tickets = Talep.objects.filter(
            priority='high',
            status__in=['open', 'in_progress']
        ).select_related('user').order_by('-created_at')[:5]
        
        # Kategori dağılımı
        category_stats = Talep.objects.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Günlük aktivite (son 7 gün)
        daily_activity = []
        for i in range(7):
            day = today - timedelta(days=i)
            day_tickets = Talep.objects.filter(created_at__date=day).count()
            daily_activity.append({
                'date': day.strftime('%d/%m'),
                'tickets': day_tickets
            })
        daily_activity.reverse()
        
    except ImportError:
        # Tickets app yoksa default değerler
        total_tickets = 0
        open_tickets = 0
        in_progress_tickets = 0
        resolved_tickets = 0
        closed_tickets = 0
        pending_tickets = 0
        high_priority = 0
        medium_priority = 0
        low_priority = 0
        tickets_today = 0
        tickets_yesterday = 0
        tickets_this_week = 0
        tickets_this_month = 0
        ticket_daily_growth = 0
        recent_tickets = []
        critical_tickets = []
        category_stats = []
        daily_activity = []

    # Token istatistikleri (güncel)
    active_tokens = CustomAuthToken.objects.filter(created__gte=month_ago).count()
    expired_tokens = CustomAuthToken.objects.filter(created__lt=month_ago).count()
    tokens_today = CustomAuthToken.objects.filter(created__date=today).count()
    
    # Grup sayısı ve kullanıcı dağılımı
    from django.contrib.auth.models import Group
    total_groups = Group.objects.count()
    
    # Grup başına kullanıcı sayısı
    group_user_counts = Group.objects.annotate(
        user_count=Count('customuser_set')
    ).order_by('-user_count')[:10]
    
    # System health metrikleri
    system_health = {
        'total_users': total_users,
        'active_users': active_users,
        'total_tickets': total_tickets,
        'active_tickets': open_tickets + in_progress_tickets + pending_tickets,
        'critical_tickets': high_priority,
        'user_activity_score': min(100, (users_this_week / max(total_users, 1)) * 1000),  # 0-100 skala
        'ticket_activity_score': min(100, (tickets_this_week / max(tickets_this_month/4, 1)) * 100),
    }
    
    # Performance indicators
    performance_indicators = {
        'resolution_rate': round((resolved_tickets + closed_tickets) / max(total_tickets, 1) * 100, 1),
        'daily_growth': round(ticket_daily_growth, 1),
        'user_engagement': round(tickets_this_month / max(active_users, 1), 2),
        'support_load': round(open_tickets / max(support_users, 1), 2) if support_users > 0 else 0,
    }
    
    # Son kullanıcılar (güncel)
    recent_users = CustomUser.objects.select_related().order_by('-date_joined')[:10]

    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Yönetim Paneli',
        'page_title': 'Admin Panel',
        
        # Kullanıcı istatistikleri (güncel)
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'support_users': support_users,
        'customer_users': customer_users,
        'users_today': users_today,
        'users_this_week': users_this_week,
        'users_this_month': users_this_month,
        'recent_users': recent_users,
        
        # Talep istatistikleri (güncel)
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'pending_tickets': pending_tickets,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'tickets_today': tickets_today,
        'tickets_this_week': tickets_this_week,
        'tickets_this_month': tickets_this_month,
        'ticket_daily_growth': round(ticket_daily_growth, 2),
        'recent_tickets': recent_tickets,
        'critical_tickets': critical_tickets,
        'category_stats': category_stats,
        'daily_activity': daily_activity,
        
        # Token ve grup istatistikleri (güncel)
        'active_tokens': active_tokens,
        'expired_tokens': expired_tokens,
        'tokens_today': tokens_today,
        'total_groups': total_groups,
        'group_user_counts': group_user_counts,
        
        # System health ve performance
        'system_health': system_health,
        'performance_indicators': performance_indicators,
        
        # Metadata
        'last_updated': now.strftime('%d/%m/%Y %H:%M:%S'),
        'dashboard_period': f"Son 30 gün ({month_ago.strftime('%d/%m')} - {now.strftime('%d/%m')})"
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
    from tickets.models import Talep
    from django.db.models import Count, Q
    
    # Aynı gruptaki kullanıcıların taleplerini de al
    user_groups = request.user.groups.all()
    if user_groups.exists():
        # Aynı grupta olan kullanıcıları bul
        group_users = CustomUser.objects.filter(groups__in=user_groups).distinct()
        # Bu kullanıcıların son 5 talebini al
        recent_tickets = Talep.objects.filter(user__in=group_users).order_by('-created_at')[:5]
        # Ticket istatistiklerini hesapla
        ticket_stats = Talep.objects.filter(user__in=group_users).aggregate(
            total=Count('id'),
            open=Count('id', filter=Q(status='open')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            resolved=Count('id', filter=Q(status='resolved')),
            closed=Count('id', filter=Q(status='closed'))
        )
    else:
        # Grubu yoksa sadece kendi taleplerini göster
        recent_tickets = Talep.objects.filter(user=request.user).order_by('-created_at')[:5]
        ticket_stats = Talep.objects.filter(user=request.user).aggregate(
            total=Count('id'),
            open=Count('id', filter=Q(status='open')),
            in_progress=Count('id', filter=Q(status='in_progress')),
            resolved=Count('id', filter=Q(status='resolved')),
            closed=Count('id', filter=Q(status='closed'))
        )
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Müşteri Paneli',
        'page_title': 'Müşteri Paneli',
        'tickets': recent_tickets,
        'ticket_stats': ticket_stats,
    }
    return render(request, 'accounts/customer_panel_modern.html', context)

# =========================
# Admin Kullanıcı Yönetimi
# =========================

@login_required
def admin_users_view(request):
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    users = CustomUser.objects.prefetch_related('groups').all().order_by('-date_joined')
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
        # Form verilerini al
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        role = request.POST.get('role', 'customer')
        is_active = request.POST.get('is_active') == 'on'
        
        # Basit validasyonlar
        errors = []
        if not username:
            errors.append('Kullanıcı adı gerekli.')
        if not password:
            errors.append('Şifre gerekli.')
        if password != password_confirm:
            errors.append('Şifreler eşleşmiyor.')
        if len(password) < 6:
            errors.append('Şifre en az 6 karakter olmalı.')
        if CustomUser.objects.filter(username=username).exists():
            errors.append('Bu kullanıcı adı zaten kullanılıyor.')
        if email and CustomUser.objects.filter(email=email).exists():
            errors.append('Bu e-posta adresi zaten kullanılıyor.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                user_data = {
                    'username': username,
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'is_active': is_active
                }
                
                user = CustomUser.objects.create_user(**user_data)
                
                full_name = f"{first_name} {last_name}".strip()
                display_name = full_name if full_name else username
                
                messages.success(request, f'Kullanıcı "{display_name}" ({username}) başarıyla oluşturuldu.')
                return redirect('admin_users')
                
            except Exception as e:
                messages.error(request, f'Kullanıcı oluşturulurken hata: {str(e)}')

    return render(request, 'accounts/admin_user_create.html', {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Yeni Kullanıcı',
        'page_title': 'Yeni Kullanıcı Oluştur'
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
    return redirect('/accounts/login/')

def signup_view(request):
    return render(request, 'registration/signup.html')

# =========================
# Password Reset Views
# =========================

def password_reset_view(request):
    """Parolamı unuttum - E-posta gönderme sayfası"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if email:
            try:
                user = CustomUser.objects.get(email=email)
                # Burada normalde e-posta gönderilir, şimdilik basit bir çözüm
                messages.success(request, f'Şifre sıfırlama talimatları {email} adresine gönderildi.')
                return redirect('password_reset_done')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Bu e-posta adresi ile kayıtlı kullanıcı bulunamadı.')
        else:
            messages.error(request, 'Lütfen geçerli bir e-posta adresi girin.')
    
    return render(request, 'accounts/password_reset.html')

def password_reset_done_view(request):
    """Şifre sıfırlama e-postası gönderildi sayfası"""
    return render(request, 'accounts/password_reset_done.html')

def password_reset_confirm_view(request, uidb64, token):
    """Şifre sıfırlama onaylama sayfası"""
    # Şimdilik basit bir implementasyon
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 and password2:
            if password1 == password2:
                # Normalde token kontrolü yapılır
                messages.success(request, 'Şifreniz başarıyla değiştirildi.')
                return redirect('password_reset_complete')
            else:
                messages.error(request, 'Şifreler eşleşmiyor.')
        else:
            messages.error(request, 'Lütfen tüm alanları doldurun.')
    
    return render(request, 'accounts/password_reset_confirm.html', {
        'uidb64': uidb64,
        'token': token
    })

def password_reset_complete_view(request):
    """Şifre sıfırlama tamamlandı sayfası"""
    return render(request, 'accounts/password_reset_complete.html')

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

@login_required
def admin_user_assign_groups_view(request, user_id):
    """Admin - Kullanıcı grup atama"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Kullanıcı bulunamadı.')
        return redirect('admin_users')
    
    # Super admin'in grupları değiştirilemez
    if user.is_superuser and user.id != request.user.id:
        messages.error(request, 'Super admin kullanıcının grupları değiştirilemez.')
        return redirect('admin_users')
    
    from django.contrib.auth.models import Group
    all_groups = Group.objects.all()
    user_groups = user.groups.all()
    
    if request.method == 'POST':
        # Seçilen grupları al
        selected_group_ids = request.POST.getlist('groups')
        selected_groups = Group.objects.filter(id__in=selected_group_ids)
        
        # Kullanıcının mevcut gruplarını temizle ve yenilerini ata
        user.groups.clear()
        user.groups.set(selected_groups)
        
        group_names = [group.name for group in selected_groups]
        if group_names:
            messages.success(request, f'Kullanıcı "{user.username}" şu gruplara atandı: {", ".join(group_names)}')
        else:
            messages.success(request, f'Kullanıcı "{user.username}" tüm gruplardan çıkarıldı.')
        
        return redirect('admin_users')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'target_user': user,
        'all_groups': all_groups,
        'user_groups': user_groups,
        'panel_title': 'Grup Atama',
        'page_title': f'Grup Atama - {user.username}'
    }
    return render(request, 'accounts/admin_user_assign_groups.html', context)

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
def admin_group_users_api(request, group_id):
    """Grup kullanıcılarını JSON formatında döndür"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return JsonResponse({'error': 'Yetkiniz yok'}, status=403)
    
    try:
        from django.contrib.auth.models import Group
        group = Group.objects.get(id=group_id)
        users = group.customuser_set.all().order_by('username')
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'email': user.email or '',
                'role': user.role,
                'is_active': user.is_active,
                'date_joined': user.date_joined.strftime('%d.%m.%Y'),
                'last_login': user.last_login.strftime('%d.%m.%Y %H:%M') if user.last_login else 'Henüz giriş yapılmamış'
            })
        
        return JsonResponse({
            'success': True,
            'group_name': group.name,
            'user_count': len(users_data),
            'users': users_data
        })
        
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Grup bulunamadı'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def admin_permissions_view(request):
    """Yetki yönetimi sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    from django.contrib.auth.models import Permission
    from django.contrib.contenttypes.models import ContentType
    
    permissions = Permission.objects.all().order_by('content_type__app_label', 'codename')
    content_types = ContentType.objects.filter(permission__isnull=False).distinct()
    
    # İzin adlarını Türkçeleştir
    permission_translations = {
        'add_': 'Ekle - ',
        'change_': 'Değiştir - ',
        'delete_': 'Sil - ',
        'view_': 'Görüntüle - ',
        'Can add': 'Ekleyebilir',
        'Can change': 'Değiştirebilir', 
        'Can delete': 'Silebilir',
        'Can view': 'Görüntüleyebilir',
        'user': 'Kullanıcı',
        'group': 'Grup',
        'permission': 'İzin',
        'content type': 'İçerik Türü',
        'session': 'Oturum',
        'log entry': 'Günlük Kaydı',
        'talep': 'Talep',
        'ticket': 'Talep',
        'comment': 'Yorum',
        'category': 'Kategori',
        'sla': 'Hizmet Seviyesi',
        'customuser': 'Kullanıcı',
        'customauthtoken': 'Kimlik Doğrulama Token',
    }
    
    # Permissions'lara Türkçe adlar ekle
    for permission in permissions:
        # İzin adını Türkçeleştir
        turkish_name = permission.name
        for eng, tr in permission_translations.items():
            turkish_name = turkish_name.replace(eng, tr)
        permission.turkish_name = turkish_name
        
        # Model adını Türkçeleştir
        model_name = permission.content_type.model
        if model_name in permission_translations:
            permission.turkish_model = permission_translations[model_name]
        else:
            permission.turkish_model = model_name.title()
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'permissions': permissions,
        'content_types': content_types,
        'panel_title': 'Yetki Yönetimi',
        'page_title': 'Yetki Yönetimi'
    }
    return render(request, 'accounts/admin_permissions.html', context)

@login_required
@login_required
def admin_reports_view(request):
    """Rapor sayfası - Güncel dinamik veriler"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    from datetime import datetime, timedelta
    from django.db.models import Count, Q, Avg, Max, Min
    from tickets.models import Talep
    
    now = datetime.now()
    today = now.date()
    last_week = now - timedelta(days=7)
    last_month = now - timedelta(days=30)
    last_quarter = now - timedelta(days=90)
    last_year = now - timedelta(days=365)
    
    # Temel sayaçlar
    total_users = CustomUser.objects.count()
    total_tickets = Talep.objects.count()
    
    # Zaman bazlı ticket sayıları
    tickets_today = Talep.objects.filter(created_at__date=today).count()
    tickets_last_week = Talep.objects.filter(created_at__gte=last_week).count()
    tickets_last_month = Talep.objects.filter(created_at__gte=last_month).count()
    tickets_last_quarter = Talep.objects.filter(created_at__gte=last_quarter).count()
    tickets_last_year = Talep.objects.filter(created_at__gte=last_year).count()
    
    # Status bazlı analizler
    tickets_by_status = Talep.objects.values('status').annotate(
        count=Count('id'),
        percentage=Count('id') * 100.0 / max(total_tickets, 1)
    ).order_by('-count')
    
    # Priority bazlı analizler
    tickets_by_priority = Talep.objects.values('priority').annotate(
        count=Count('id'),
        percentage=Count('id') * 100.0 / max(total_tickets, 1)
    ).order_by('-count')
    
    # Kategori bazlı analizler
    tickets_by_category = Talep.objects.values('category__name').annotate(
        count=Count('id'),
        percentage=Count('id') * 100.0 / max(total_tickets, 1)
    ).order_by('-count')[:15]  # Top 15 kategori
    
    # Kullanıcı rolleri analizi
    users_by_role = CustomUser.objects.values('role').annotate(
        count=Count('id'),
        percentage=Count('id') * 100.0 / max(total_users, 1)
    ).order_by('-count')
    
    # Grup bazlı kullanıcı analizi
    users_by_group = CustomUser.objects.filter(groups__isnull=False)\
        .values('groups__name').annotate(
            count=Count('id')
        ).order_by('-count')
    
    # Günlük aktivite raporu (son 30 gün)
    daily_activity = []
    for i in range(30):
        day = today - timedelta(days=i)
        day_tickets = Talep.objects.filter(created_at__date=day).count()
        day_users_joined = CustomUser.objects.filter(date_joined__date=day).count()
        
        daily_activity.append({
            'date': day.strftime('%Y-%m-%d'),
            'date_display': day.strftime('%d/%m/%Y'),
            'tickets': day_tickets,
            'new_users': day_users_joined,
            'total_activity': day_tickets + day_users_joined
        })
    
    daily_activity.reverse()  # Eskiden yeniye sırala
    
    # Aylık özet rapor (son 12 ay)
    monthly_summary = []
    for i in range(12):
        month_start = now.replace(day=1) - timedelta(days=30*i)
        next_month = month_start.replace(day=28) + timedelta(days=4)
        next_month = next_month.replace(day=1)
        
        month_tickets = Talep.objects.filter(
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        month_users = CustomUser.objects.filter(
            date_joined__gte=month_start,
            date_joined__lt=next_month
        ).count()
        
        month_closed = Talep.objects.filter(
            updated_at__gte=month_start,
            updated_at__lt=next_month,
            status='closed'
        ).count()
        
        monthly_summary.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%B %Y'),
            'tickets_created': month_tickets,
            'users_joined': month_users,
            'tickets_closed': month_closed,
            'closure_rate': round((month_closed / max(month_tickets, 1)) * 100, 2)
        })
    
    monthly_summary.reverse()  # Eskiden yeniye sırala
    
    # En aktif kullanıcılar
    most_active_users = Talep.objects.values(
        'user__username', 
        'user__first_name', 
        'user__last_name',
        'user__email'
    ).annotate(
        ticket_count=Count('id')
    ).order_by('-ticket_count')[:20]
    
    # System health metrics
    system_health = {
        'total_users': total_users,
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'admin_users': CustomUser.objects.filter(role='admin').count(),
        'support_users': CustomUser.objects.filter(role='support').count(),
        'customer_users': CustomUser.objects.filter(role='customer').count(),
        'total_tickets': total_tickets,
        'open_tickets': Talep.objects.exclude(status='closed').count(),
        'closed_tickets': Talep.objects.filter(status='closed').count(),
        'high_priority_tickets': Talep.objects.filter(priority='high').count(),
        'overdue_tickets': 0,  # Gelecekte deadline alanı eklenirse güncellenebilir
    }
    
    # Performance indicators
    performance_indicators = {
        'daily_avg_tickets': round(tickets_last_month / 30, 2) if tickets_last_month > 0 else 0,
        'weekly_avg_tickets': round(tickets_last_month / 4, 2) if tickets_last_month > 0 else 0,
        'monthly_growth': round(((tickets_last_month - tickets_last_quarter/3) / max(tickets_last_quarter/3, 1)) * 100, 2),
        'user_engagement': round((total_tickets / max(total_users, 1)), 2),
        'tickets_per_user': round((total_tickets / max(total_users, 1)), 2),
        'resolution_rate': round((system_health['closed_tickets'] / max(total_tickets, 1)) * 100, 2),
    }
    
    report_data = {
        'total_users': total_users,
        'total_tickets': total_tickets,
        'tickets_today': tickets_today,
        'tickets_last_week': tickets_last_week,
        'tickets_last_month': tickets_last_month,
        'tickets_last_quarter': tickets_last_quarter,
        'tickets_last_year': tickets_last_year,
        'tickets_by_status': list(tickets_by_status),
        'tickets_by_priority': list(tickets_by_priority),
        'tickets_by_category': list(tickets_by_category),
        'users_by_role': list(users_by_role),
        'users_by_group': list(users_by_group),
        'daily_activity': daily_activity,
        'monthly_summary': monthly_summary,
        'most_active_users': list(most_active_users),
        'system_health': system_health,
        'performance_indicators': performance_indicators,
    }
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'report_data': report_data,
        'panel_title': 'Sistem Raporları',
        'page_title': 'Sistem Raporları',
        'generated_at': now.strftime('%d/%m/%Y %H:%M:%S'),
        'report_period': f"{last_month.strftime('%d/%m/%Y')} - {now.strftime('%d/%m/%Y')}"
    }
    return render(request, 'accounts/admin_reports.html', context)

@login_required
def admin_analytics_view(request):
    """Analitik sayfası - Gerçek zamanlı veriler"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    from datetime import datetime, timedelta
    from django.db.models import Count, Q, Avg
    from tickets.models import Talep
    
    now = datetime.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    last_week = now - timedelta(days=7)
    last_month = now - timedelta(days=30)
    last_year = now - timedelta(days=365)
    
    # Temel istatistikler
    total_tickets = Talep.objects.count()
    total_users = CustomUser.objects.count()
    active_tickets = Talep.objects.exclude(status='closed').count()
    closed_tickets = Talep.objects.filter(status='closed').count()
    
    # Zaman bazlı analizler
    tickets_today = Talep.objects.filter(created_at__date=today).count()
    tickets_yesterday = Talep.objects.filter(created_at__date=yesterday).count()
    tickets_this_week = Talep.objects.filter(created_at__gte=last_week).count()
    tickets_this_month = Talep.objects.filter(created_at__gte=last_month).count()
    
    # Büyüme oranları
    today_growth = ((tickets_today - tickets_yesterday) / max(tickets_yesterday, 1)) * 100 if tickets_yesterday > 0 else 0
    
    # Haftalık karşılaştırma
    previous_week_start = last_week - timedelta(days=7)
    tickets_previous_week = Talep.objects.filter(
        created_at__gte=previous_week_start, 
        created_at__lt=last_week
    ).count()
    weekly_growth = ((tickets_this_week - tickets_previous_week) / max(tickets_previous_week, 1)) * 100 if tickets_previous_week > 0 else 0
    
    # Status dağılımı
    status_distribution = Talep.objects.values('status').annotate(count=Count('id')).order_by('-count')
    
    # Priority dağılımı  
    priority_distribution = Talep.objects.values('priority').annotate(count=Count('id')).order_by('-count')
    
    # Kategori dağılımı
    category_distribution = Talep.objects.values('category__name').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Kullanıcı rolleri dağılımı
    user_roles = CustomUser.objects.values('role').annotate(count=Count('id'))
    
    # Aylık trend verisi (son 12 ay)
    monthly_data = []
    for i in range(12):
        month_start = now.replace(day=1) - timedelta(days=30*i)
        next_month = month_start.replace(day=28) + timedelta(days=4)
        next_month = next_month.replace(day=1)
        
        month_tickets = Talep.objects.filter(
            created_at__gte=month_start,
            created_at__lt=next_month
        ).count()
        
        monthly_data.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%B %Y'),
            'count': month_tickets
        })
    
    monthly_data.reverse()  # Eskiden yeniye sırala
    
    # Günlük trend (son 30 gün)
    daily_data = []
    for i in range(30):
        day = today - timedelta(days=i)
        day_tickets = Talep.objects.filter(created_at__date=day).count()
        daily_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'date_display': day.strftime('%d/%m'),
            'count': day_tickets
        })
    
    daily_data.reverse()  # Eskiden yeniye sırala
    
    # En aktif kullanıcılar (talep oluşturanlar)
    top_users = Talep.objects.values('user__username', 'user__first_name', 'user__last_name')\
        .annotate(ticket_count=Count('id'))\
        .order_by('-ticket_count')[:10]
    
    # Ortalama çözüm süresi (gün olarak)
    closed_tickets_with_time = Talep.objects.filter(
        status='closed',
        updated_at__isnull=False
    )
    
    avg_resolution_time = 0
    if closed_tickets_with_time.exists():
        total_resolution_time = 0
        count = 0
        for ticket in closed_tickets_with_time:
            resolution_time = (ticket.updated_at - ticket.created_at).total_seconds() / 86400  # gün cinsinden
            total_resolution_time += resolution_time
            count += 1
        avg_resolution_time = total_resolution_time / count if count > 0 else 0
    
    # Performance metrikleri
    performance_metrics = {
        'total_tickets': total_tickets,
        'active_tickets': active_tickets,
        'closed_tickets': closed_tickets,
        'total_users': total_users,
        'tickets_today': tickets_today,
        'tickets_this_week': tickets_this_week,
        'tickets_this_month': tickets_this_month,
        'today_growth': round(today_growth, 2),
        'weekly_growth': round(weekly_growth, 2),
        'avg_resolution_time': round(avg_resolution_time, 2),
        'closure_rate': round((closed_tickets / max(total_tickets, 1)) * 100, 2),
    }
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Sistem Analitikleri',
        'page_title': 'Sistem Analitikleri',
        'performance_metrics': performance_metrics,
        'status_distribution': list(status_distribution),
        'priority_distribution': list(priority_distribution),
        'category_distribution': list(category_distribution),
        'user_roles': list(user_roles),
        'monthly_data': monthly_data,
        'daily_data': daily_data,
        'top_users': list(top_users),
        'last_updated': now.strftime('%d/%m/%Y %H:%M')
    }
    return render(request, 'accounts/admin_analytics.html', context)

@login_required
def admin_settings_view(request):
    """Sistem ayarları sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    # Mevcut ayarları al
    from .models import SystemSettings
    settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        tab = request.POST.get('tab', 'general')
        
        try:
            if tab == 'general':
                # Genel ayarları güncelle
                settings.site_name = request.POST.get('site_name', settings.site_name)
                settings.site_description = request.POST.get('site_description', settings.site_description)
                settings.admin_email = request.POST.get('admin_email', settings.admin_email)
                settings.timezone = request.POST.get('timezone', settings.timezone)
                settings.updated_by = request.user
                settings.save()
                messages.success(request, 'Genel ayarlar başarıyla güncellendi.')
                
            elif tab == 'email':
                # E-posta ayarları güncelle
                settings.smtp_host = request.POST.get('smtp_host', '')
                settings.smtp_port = int(request.POST.get('smtp_port', 587))
                settings.smtp_username = request.POST.get('smtp_username', '')
                smtp_password = request.POST.get('smtp_password', '')
                if smtp_password:  # Sadece yeni şifre girilmişse güncelle
                    settings.smtp_password = smtp_password
                settings.smtp_use_tls = 'smtp_use_tls' in request.POST
                settings.updated_by = request.user
                settings.save()
                messages.success(request, 'E-posta ayarları başarıyla güncellendi.')
                
            elif tab == 'security':
                # Güvenlik ayarları güncelle
                settings.token_expiry_days = int(request.POST.get('token_expiry_days', 30))
                settings.max_login_attempts = int(request.POST.get('max_login_attempts', 5))
                settings.session_timeout_minutes = int(request.POST.get('session_timeout_minutes', 30))
                settings.require_password_change = 'require_password_change' in request.POST
                settings.enable_2fa = 'enable_2fa' in request.POST
                settings.updated_by = request.user
                settings.save()
                messages.success(request, 'Güvenlik ayarları başarıyla güncellendi.')
                
        except ValueError as e:
            messages.error(request, f'Geçersiz değer girişi: {str(e)}')
        except Exception as e:
            messages.error(request, f'Ayarlar güncellenirken hata oluştu: {str(e)}')
        
        # Güncelleme sonrası aynı tab'a yönlendir
        return redirect(f"{request.path}?tab={tab}")
    
    # Hangi tab'ın aktif olacağını belirle
    active_tab = request.GET.get('tab', 'general')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Sistem Ayarları',
        'page_title': 'Sistem Ayarları',
        'settings': settings,
        'active_tab': active_tab,
        'last_updated': settings.updated_at,
        'last_updated_by': settings.updated_by,
    }
    return render(request, 'accounts/admin_settings.html', context)

@login_required
def admin_logs_view(request):
    """Sistem logları sayfası"""
    if getattr(request.user, 'role', '').lower() != 'admin':
        return redirect('/accounts/login/')
    
    from .models import SystemLog
    from django.core.paginator import Paginator
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Filtreleme parametreleri
    level_filter = request.GET.get('level', '')
    date_filter = request.GET.get('date_range', 'all')
    search_query = request.GET.get('search', '')
    
    # Log kayıtlarını filtrele
    logs = SystemLog.objects.all()
    
    if level_filter:
        logs = logs.filter(level=level_filter.upper())
    
    if date_filter == 'today':
        logs = logs.filter(timestamp__date=timezone.now().date())
    elif date_filter == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        logs = logs.filter(timestamp__gte=week_ago)
    elif date_filter == 'month':
        month_ago = timezone.now() - timedelta(days=30)
        logs = logs.filter(timestamp__gte=month_ago)
    
    if search_query:
        logs = logs.filter(
            Q(message__icontains=search_query) | 
            Q(action__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Sayfalama
    paginator = Paginator(logs, 20)  # Her sayfada 20 log
    page_number = request.GET.get('page')
    page_logs = paginator.get_page(page_number)
    
    # İstatistikler
    log_stats = SystemLog.objects.values('level').annotate(count=Count('id'))
    stats_dict = {stat['level']: stat['count'] for stat in log_stats}
    
    # AJAX istek kontrolü - log temizleme
    if request.method == 'POST' and request.POST.get('action') == 'clear_logs':
        if request.user.role == 'admin':
            # Eski logları sil (30 günden eski)
            old_date = timezone.now() - timedelta(days=30)
            deleted_count = SystemLog.objects.filter(timestamp__lt=old_date).delete()[0]
            
            # Yeni log kaydı oluştur
            SystemLog.log(
                level='INFO',
                action='LOG_CLEANUP',
                message=f'Admin tarafından {deleted_count} adet eski log kaydı temizlendi',
                user=request.user,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'{deleted_count} adet eski log kaydı temizlendi.')
            return redirect('admin_logs')
    
    context = {
        'current_user': request.user,
        'user_role': request.user.get_role_display(),
        'panel_title': 'Sistem Logları',
        'page_title': 'Sistem Logları',
        'logs': page_logs,
        'stats': {
            'DEBUG': stats_dict.get('DEBUG', 0),
            'INFO': stats_dict.get('INFO', 0),
            'WARNING': stats_dict.get('WARNING', 0),
            'ERROR': stats_dict.get('ERROR', 0),
            'CRITICAL': stats_dict.get('CRITICAL', 0),
        },
        'total_logs': logs.count(),
        'filters': {
            'level': level_filter,
            'date_range': date_filter,
            'search': search_query,
        }
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
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        
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
            first_name=first_name,
            last_name=last_name,
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
