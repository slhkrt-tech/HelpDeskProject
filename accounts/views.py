# accounts/views.py
"""
HelpDesk Kullanıcı Yönetimi - Ana View'lar
========================================

Token-based authentication, role-based access control, user management
Kullanıcı rolleri: admin, support, customer
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import logging

# Django REST Framework
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

# Local imports
from .serializers import LoginSerializer, UserSerializer
from .models import CustomAuthToken, CustomUser
from .security import (
    rate_limit_login, sanitize_input, validate_password_strength, 
    admin_required, get_client_ip
)

# ================================================================================
# Global Configuration
# ================================================================================

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """API endpoint'ler için CSRF kontrolünü devre dışı bırakan authentication sınıfı"""
    def enforce_csrf(self, request):
        return

# Global değişkenler
User = get_user_model()
logger = logging.getLogger(__name__)


# ================================================================================
# Yardımcı Fonksiyonlar
# ================================================================================

def _redirect_user_by_role(user, preferred_redirect=None):
    """
    Kullanıcıyı rolüne göre yönlendir
    
    Args:
        user: CustomUser objesi
        preferred_redirect: Tercih edilen yönlendirme
        
    Returns:
        HttpResponseRedirect: Yönlendirme objesi
    """
    # Tercih edilen yönlendirme varsa ve yetki kontrolü
    if preferred_redirect == 'admin-panel' and (user.is_superuser or user.role == 'admin'):
        return redirect('/accounts/admin-panel/')
    elif preferred_redirect == 'support-panel' and user.role in ['admin', 'support']:
        return redirect('/accounts/support-panel/')
    elif preferred_redirect == 'customer-panel':
        return redirect('/accounts/customer-panel/')
    
    # Varsayılan rol bazlı yönlendirme
    if user.is_superuser or user.role == 'admin':
        return redirect('/accounts/admin-panel/')
    elif user.role == 'support':
        return redirect('/accounts/support-panel/')
    else:
        return redirect('/accounts/customer-panel/')


def home_view(request):
    """
    Ana sayfa - token kontrolü yapıp kullanıcıyı rolüne göre yönlendirir
    
    Args:
        request: HTTP request objesi
        
    Returns:
        HttpResponse: Yönlendirme veya login sayfası
    """
    # Token tabanlı kimlik doğrulama kontrolü
    user = verify_token_auth(request)
    
    if user:
        # Kullanıcı giriş yapmış, redirect parametresine göre yönlendir
        redirect_to = request.GET.get('redirect')
        return _redirect_user_by_role(user, redirect_to)
    
    # Kullanıcı giriş yapmamış - login sayfasına yönlendir
    redirect_to = request.GET.get('redirect')
    if redirect_to:
        return redirect(f'/accounts/login/?next={redirect_to}')
    
    # Normal ana sayfa
    return render(request, 'tickets/home.html')


@api_view(['POST'])
@permission_classes([AllowAny])
@rate_limit_login(max_attempts=5, window_minutes=15)
def api_login(request):
    """
    Gelişmiş token-based login endpoint - rate limited ve güvenli
    
    Args:
        request: HTTP request objesi
        
    Returns:
        Response: Login sonucu ve token bilgisi
    """
    # Input sanitization
    username = sanitize_input(request.data.get('username', ''), max_length=150)
    password = request.data.get('password', '')
    
    # Temel validasyon
    if not username or not password:
        logger.warning(f"Login attempt with missing credentials from IP: {get_client_ip(request)}")
        return Response({
            'error': 'Username and password are required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Kullanıcı doğrulama
    serializer = LoginSerializer(data={'username': username, 'password': password})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Eski session temizleme
        if request.user.is_authenticated and request.user != user:
            logout(request)
        
        logger.info(f"Successful login for user: {user.username} from IP: {get_client_ip(request)}")
        
        # Token yönetimi - eski token'ları temizle
        CustomAuthToken.objects.filter(user=user).delete()
        
        # Yeni custom token oluştur
        custom_token = CustomAuthToken.objects.create(
            user=user,
            username=user.username
        )
        custom_token.set_password_hash(password)
        custom_token.save()
        
        # Backward compatibility için normal token
        normal_token, created = Token.objects.get_or_create(user=user)
        
        # Response hazırlama
        user_serializer = UserSerializer(user)
        
        # Kullanıcı rolüne göre yönlendirme URL'i
        if user.is_superuser or user.role == 'admin':
            redirect_url = '/accounts/admin-panel/'
        elif user.role == 'support':
            redirect_url = '/accounts/support-panel/'
        else:
            redirect_url = '/accounts/customer-panel/'
        
        response = Response({
            'token': custom_token.key,
            'backup_token': normal_token.key,
            'user': user_serializer.data,
            'redirect_url': redirect_url,
            'token_expires': custom_token.expires_at.isoformat(),
            'message': 'Başarıyla giriş yapıldı.'
        })
        
        # Önce eski cookie'leri temizle (farklı kullanıcı girişi için)
        response.delete_cookie('auth_token')
        response.delete_cookie('user_id')
        response.delete_cookie('user_role')
        response.delete_cookie('sessionid')  # Django session cookie'sini de temizle
        
        # Token'ı çerezlere kaydet (browser için)
        response.set_cookie(
            'auth_token',
            custom_token.key,
            max_age=7*24*60*60,  # 7 gün
            httponly=True,  # XSS koruması
            secure=False,  # Development için False, production'da True olmalı
            samesite='Lax'  # CSRF koruması
        )
        
        # Kullanıcı ID'sini de çerezlere kaydet
        response.set_cookie(
            'user_id',
            str(user.id),
            max_age=7*24*60*60,
            httponly=False,  # JavaScript'ten erişebilir
            secure=False,
            samesite='Lax'
        )
        
        # Kullanıcı rolünü de çerezlere kaydet
        response.set_cookie(
            'user_role',
            user.role,
            max_age=7*24*60*60,
            httponly=False,
            secure=False,
            samesite='Lax'
        )
        
        return response
    
    # Log failed login attempt
    logger.warning(f"Failed login attempt for username: {username} from IP: {get_client_ip(request)}")
    return Response({
        'error': 'Invalid username or password.'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def api_logout(request):
    """
    Gelişmiş token-based logout endpoint
    """
    try:
        # Session'ı temizle
        if request.user.is_authenticated:
            from django.contrib.auth import logout
            logout(request)
        
        # Custom token'ı sil
        user = verify_token_auth(request)
        if user and hasattr(user, 'custom_auth_token'):
            user.custom_auth_token.delete()
        
        # Normal token'ı da sil (backward compatibility)
        if user and hasattr(user, 'auth_token'):
            user.auth_token.delete()
            
        response = Response({
            'message': 'Başarıyla çıkış yapıldı.'
        })
        
        # Çerezleri temizle
        response.delete_cookie('auth_token')
        response.delete_cookie('user_id')
        response.delete_cookie('user_role')
        response.delete_cookie('sessionid')  # Django session cookie'sini de temizle
        
        return response
    except Exception as e:
        response = Response({
            'error': f'Çıkış yapılırken hata oluştu: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
        
        # Hata durumunda da çerezleri temizle
        response.delete_cookie('auth_token')
        response.delete_cookie('user_id')
        response.delete_cookie('user_role')
        response.delete_cookie('sessionid')
        
        return response

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def api_safe_logout(request):
    """
    Güvenli çıkış - Tüm kullanıcı verilerini temizler ve login sayfasına yönlendirir
    Signup sonrası role karışıklığını önlemek için kullanılır
    """
    try:
        logger.info(f"Safe logout requested from IP: {get_client_ip(request)}")
        
        # Mevcut kullanıcı bilgilerini al
        user = verify_token_auth(request)
        if user:
            logger.info(f"Safe logout for user: {user.username} (role: {user.role})")
        
        # Session'ı tamamen temizle
        if request.user.is_authenticated:
            from django.contrib.auth import logout
            logout(request)
        
        # Kullanıcının tüm token'larını sil
        if user:
            # Custom token'ları sil
            CustomAuthToken.objects.filter(user=user).delete()
            
            # Normal token'ları da sil
            Token.objects.filter(user=user).delete()
        
        response = Response({
            'message': 'Güvenli çıkış yapıldı. Lütfen tekrar giriş yapın.',
            'redirect_url': '/accounts/login/',
            'action': 'safe_logout_complete'
        })
        
        # Tüm authentication çerezlerini temizle
        response.delete_cookie('auth_token')
        response.delete_cookie('user_id')
        response.delete_cookie('user_role')
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        
        logger.info("Safe logout completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Safe logout error: {str(e)}")
        response = Response({
            'message': 'Güvenli çıkış tamamlandı.',
            'redirect_url': '/accounts/login/',
            'action': 'safe_logout_complete'
        })
        
        # Hata durumunda da tüm çerezleri temizle
        response.delete_cookie('auth_token')
        response.delete_cookie('user_id')
        response.delete_cookie('user_role')
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        
        return response

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication, TokenAuthentication])
@permission_classes([AllowAny])
def api_debug_tokens(request):
    """
    Debug endpoint - Mevcut kullanıcının token durumunu gösterir
    """
    try:
        logger.info(f"Debug tokens request from IP: {get_client_ip(request)}")
        
        # Cookie'den token al
        cookie_token = request.COOKIES.get('auth_token')
        
        # Header'dan token al
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        header_token = None
        if auth_header.startswith('Token '):
            header_token = auth_header.split(' ')[1]
            
        # LocalStorage'dan gelen token (frontend'den gönderilir)
        localStorage_token = request.GET.get('localStorage_token')
        
        debug_info = {
            'cookie_token': cookie_token[-8:] + '...' if cookie_token else None,
            'header_token': header_token[-8:] + '...' if header_token else None,
            'localStorage_token': localStorage_token[-8:] + '...' if localStorage_token else None,
            'authenticated_user': None,
            'token_validation': {}
        }
        
        # Token'ları validate et
        tokens_to_check = [
            ('cookie', cookie_token),
            ('header', header_token),
            ('localStorage', localStorage_token)
        ]
        
        for token_type, token_value in tokens_to_check:
            if token_value:
                user = get_user_by_token(token_value)
                debug_info['token_validation'][token_type] = {
                    'valid': bool(user),
                    'user': user.username if user else None,
                    'user_role': user.role if user else None
                }
                if user and not debug_info['authenticated_user']:
                    debug_info['authenticated_user'] = {
                        'username': user.username,
                        'role': user.role,
                        'is_staff': user.is_staff,
                        'token_source': token_type
                    }
        
        return Response(debug_info)
        
    except Exception as e:
        logger.error(f"Debug tokens error: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([CsrfExemptSessionAuthentication, TokenAuthentication])
@permission_classes([AllowAny])  # Kendi auth kontrolümüzü yapıyoruz
def api_user_profile(request):
    """
    Mevcut kullanıcının profil bilgilerini ve hesap istatistiklerini getir - Hybrid authentication (Session + Token)
    """
    logger.info(f"api_user_profile called from IP: {get_client_ip(request)}")
    logger.info(f"Request user: {request.user}, authenticated: {request.user.is_authenticated}")
    logger.info(f"Authorization header: {request.META.get('HTTP_AUTHORIZATION', 'None')}")
    logger.info(f"Cookies: {list(request.COOKIES.keys())}")
    
    # Önce session-based authentication kontrol et
    if request.user.is_authenticated:
        user = request.user
        logger.info(f"User authenticated via Django session: {user.username}")
    else:
        # Token tabanlı kimlik doğrulama
        user = verify_token_auth(request)
        logger.info(f"verify_token_auth result: {user}")
    
    if not user:
        logger.warning(f"api_user_profile: No authenticated user found")
        return Response({
            'error': 'Authentication required'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Import ticket models for statistics
    from tickets.models import Talep, Comment
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    serializer = UserSerializer(user)
    
    # Token bilgilerini de ekle
    token_info = {}
    try:
        if hasattr(user, 'custom_auth_token'):
            custom_token = user.custom_auth_token
            token_info = {
                'token_created': custom_token.created.isoformat(),
                'token_expires': custom_token.expires_at.isoformat(),
                'last_used': custom_token.last_used.isoformat() if custom_token.last_used else None,
                'is_expired': custom_token.is_expired()
            }
    except:
        pass
    
    # Hesap istatistikleri hesapla
    statistics = {}
    
    try:
        # Genel istatistikler
        if user.role == 'admin':
            # Admin için tüm sistem istatistikleri
            statistics = {
                'total_tickets': Talep.objects.count(),
                'open_tickets': Talep.objects.filter(status='open').count(),
                'in_progress_tickets': Talep.objects.filter(status='in_progress').count(),
                'resolved_tickets': Talep.objects.filter(status='resolved').count(),
                'closed_tickets': Talep.objects.filter(status='closed').count(),
                'total_users': CustomUser.objects.count(),
                'admin_users': CustomUser.objects.filter(role='admin').count(),
                'support_users': CustomUser.objects.filter(role='support').count(),
                'customer_users': CustomUser.objects.filter(role='customer').count(),
                'tickets_this_week': Talep.objects.filter(
                    created_at__gte=datetime.now() - timedelta(days=7)
                ).count(),
                'tickets_this_month': Talep.objects.filter(
                    created_at__gte=datetime.now() - timedelta(days=30)
                ).count(),
                'my_assigned_tickets': Talep.objects.filter(assigned_to=user).count(),
                'my_comments': Comment.objects.filter(user=user).count(),
            }
        elif user.role == 'support':
            # Support için kendi ve genel istatistikler
            statistics = {
                'total_tickets': Talep.objects.count(),
                'open_tickets': Talep.objects.filter(status='open').count(),
                'in_progress_tickets': Talep.objects.filter(status='in_progress').count(),
                'resolved_tickets': Talep.objects.filter(status='resolved').count(),
                'closed_tickets': Talep.objects.filter(status='closed').count(),
                'my_assigned_tickets': Talep.objects.filter(assigned_to=user).count(),
                'my_resolved_tickets': Talep.objects.filter(
                    assigned_to=user, status='resolved'
                ).count(),
                'my_comments': Comment.objects.filter(user=user).count(),
                'tickets_this_week': Talep.objects.filter(
                    created_at__gte=datetime.now() - timedelta(days=7)
                ).count(),
                'tickets_this_month': Talep.objects.filter(
                    created_at__gte=datetime.now() - timedelta(days=30)
                ).count(),
            }
        else:
            # Customer için kendi istatistikleri
            user_group = user.groups.first()
            group_tickets = Talep.objects.filter(
                user__groups=user_group
            ) if user_group else Talep.objects.filter(user=user)
            
            statistics = {
                'my_tickets': Talep.objects.filter(user=user).count(),
                'my_open_tickets': Talep.objects.filter(user=user, status='open').count(),
                'my_in_progress_tickets': Talep.objects.filter(user=user, status='in_progress').count(),
                'my_resolved_tickets': Talep.objects.filter(user=user, status='resolved').count(),
                'my_closed_tickets': Talep.objects.filter(user=user, status='closed').count(),
                'my_comments': Comment.objects.filter(user=user).count(),
                'group_tickets': group_tickets.count(),
                'tickets_this_week': Talep.objects.filter(
                    user=user, created_at__gte=datetime.now() - timedelta(days=7)
                ).count(),
                'tickets_this_month': Talep.objects.filter(
                    user=user, created_at__gte=datetime.now() - timedelta(days=30)
                ).count(),
            }
        
        # Son aktivite bilgileri
        latest_ticket = Talep.objects.filter(user=user).order_by('-created_at').first()
        latest_comment = Comment.objects.filter(user=user).order_by('-created_at').first()
        
        activity_info = {
            'latest_ticket': {
                'id': latest_ticket.id,
                'title': latest_ticket.title,
                'created_at': latest_ticket.created_at.isoformat(),
                'status': latest_ticket.get_status_display()
            } if latest_ticket else None,
            'latest_comment': {
                'ticket_id': latest_comment.talep.id,
                'ticket_title': latest_comment.talep.title,
                'created_at': latest_comment.created_at.isoformat(),
                'message': latest_comment.message[:100] + '...' if len(latest_comment.message) > 100 else latest_comment.message
            } if latest_comment else None,
            'account_created': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }
        
    except Exception as e:
        logger.error(f"Error calculating user statistics: {e}")
        statistics = {}
        activity_info = {}
    
    return Response({
        'user': serializer.data,
        'token_info': token_info,
        'statistics': statistics,
        'activity': activity_info
    })

@csrf_exempt
@api_view(['POST'])  # Tekrar sadece POST
@permission_classes([AllowAny])
@authentication_classes([CsrfExemptSessionAuthentication, TokenAuthentication])
@rate_limit_login(max_attempts=3, window_minutes=30)  # Signup için daha kısıtlayıcı
def api_signup(request):
    """
    Token-based signup endpoint - Enhanced security
    """
    logger.info(f"api_signup called from IP: {get_client_ip(request)}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request data: {request.data}")
    
    try:
        # Input sanitization
        username = sanitize_input(request.data.get('username', ''), max_length=150)
        email = sanitize_input(request.data.get('email', ''), max_length=254)
        password1 = request.data.get('password1', '')
        password2 = request.data.get('password2', '')
        
        logger.info(f"Sanitized data - username: {username}, email: {email}")
        
        # Validations
        if not all([username, email, password1, password2]):
            logger.warning(f"Missing fields - username: {bool(username)}, email: {bool(email)}, password1: {bool(password1)}, password2: {bool(password2)}")
            return Response({
                'error': 'Tüm alanlar doldurulmalıdır.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Username length validation
        if len(username) < 3:
            return Response({
                'error': 'Kullanıcı adı en az 3 karakter olmalıdır.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Username character validation
        if not username.replace('_', '').replace('-', '').isalnum():
            return Response({
                'error': 'Kullanıcı adı sadece harf, rakam, alt çizgi (_) ve tire (-) içerebilir.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if password1 != password2:
            return Response({
                'error': 'Parolalar eşleşmiyor.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Password strength validation
        password_errors = validate_password_strength(password1)
        if password_errors:
            return Response({
                'error': 'Parola yeterince güçlü değil: ' + ', '.join(password_errors)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Bu kullanıcı adı zaten kullanılıyor.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Bu e-posta adresi zaten kullanılıyor.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kullanıcı oluştur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        # Yeni kullanıcıları customer role'ü ile kaydet ve güvenlik ayarları
        user.role = 'customer'
        user.is_staff = False  # Güvenlik: Yeni kullanıcılar staff değil
        user.is_superuser = False  # Güvenlik: Yeni kullanıcılar superuser değil
        user.save()
        
        # Log user creation
        logger.info(f"New user created: {username} from IP: {get_client_ip(request)}")
        
        # ÖNEMLI: Signup öncesi tüm session/token temizliği
        # Eğer tarayıcıda başka bir kullanıcının token'ı varsa temizle
        existing_token = request.COOKIES.get('auth_token')
        if existing_token:
            logger.info(f"Found existing token during signup, cleaning up: {existing_token[-8:]}")
            # Eski token'ı geçersiz kıl
            try:
                old_custom_token = CustomAuthToken.objects.get(key=existing_token)
                old_user = old_custom_token.user
                logger.info(f"Deleting old tokens for user: {old_user.username}")
                # O kullanıcının tüm token'larını sil
                CustomAuthToken.objects.filter(user=old_user).delete()
                Token.objects.filter(user=old_user).delete()
            except CustomAuthToken.DoesNotExist:
                logger.info("Old token not found in CustomAuthToken, skipping cleanup")
        
        # Yeni kullanıcı için temiz token oluştur
        # Önce varsa eski token'ları temizle (güvenlik için)
        CustomAuthToken.objects.filter(user=user).delete()
        Token.objects.filter(user=user).delete()
        
        # Custom token oluştur
        custom_token = CustomAuthToken.objects.create(
            user=user,
            username=user.username
        )
        custom_token.set_password_hash(password1)
        custom_token.save()
        
        # Normal token da oluştur (backward compatibility)
        normal_token = Token.objects.create(user=user)
        
        # Kullanıcı bilgilerini serialize et
        user_serializer = UserSerializer(user)
        
        # Yeni kullanıcıları customer role'ü ile kaydet ve customer paneline yönlendir
        user.role = 'customer'
        user.save()
        
        redirect_url = '/accounts/customer-panel/'
        
        response = Response({
            'token': custom_token.key,
            'backup_token': normal_token.key,
            'user': user_serializer.data,
            'redirect_url': redirect_url,
            'token_expires': custom_token.expires_at.isoformat(),
            'message': 'Hesap başarıyla oluşturuldu ve giriş yapıldı.'
        }, status=status.HTTP_201_CREATED)
        
        # ÖNCE: Tüm eski authentication cookie'lerini temizle
        response.delete_cookie('auth_token')
        response.delete_cookie('user_id')
        response.delete_cookie('user_role')
        response.delete_cookie('sessionid')  # Django session cookie
        response.delete_cookie('csrftoken')  # CSRF token
        logger.info("Cleared all old authentication cookies before setting new ones")
        
        # YENİ: Token'ı çerezlere kaydet (browser için)
        response.set_cookie(
            'auth_token',
            custom_token.key,
            max_age=7*24*60*60,  # 7 gün
            httponly=True,  # XSS koruması
            secure=False,  # Development için False, production'da True olmalı
            samesite='Lax'  # CSRF koruması
        )
        
        # Kullanıcı ID'sini de çerezlere kaydet
        response.set_cookie(
            'user_id',
            str(user.id),
            max_age=7*24*60*60,
            httponly=False,  # JavaScript'ten erişebilir
            secure=False,
            samesite='Lax'
        )
        
        # Kullanıcı rolünü de çerezlere kaydet
        response.set_cookie(
            'user_role',
            user.role,
            max_age=7*24*60*60,
            httponly=False,
            secure=False,
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Signup error from IP {get_client_ip(request)}: {str(e)}")
        return Response({
            'error': 'Bir hata oluştu: ' + str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def signup_view(request):
    """
    Template-based signup view
    """
    return render(request, 'registration/signup_new.html')

# TOKEN TABANLI ÖZELLEŞTIRILMIŞ ADMIN PANELLERİ

def verify_token_auth(request):
    """
    Gelişmiş token tabanlı kimlik doğrulama kontrolü
    - Token authentication'a öncelik verir
    - Session authentication fallback olarak kullanılır
    - Token yenileme özelliği
    - Çerez tabanlı token yönetimi
    """
    user = None
    
    logger.info(f"verify_token_auth called for path: {request.path}")
    
    # 1. Authorization header'dan token kontrolü (EN ÖNCELİKLİ)
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Token '):
        token_key = auth_header.split(' ')[1]
        user = get_user_by_token(token_key)
        if user:
            logger.info(f"User authenticated via header token: {user.username} (role: {user.role})")
            return user
    
    # 2. Cookie'den token kontrolü (İKİNCİ ÖNCELİK)
    token_key = request.COOKIES.get('auth_token')
    if token_key:
        logger.info(f"Found auth_token in cookies: {token_key[-8:]}...")
        user = get_user_by_token(token_key)
        if user:
            logger.info(f"User authenticated via cookie token: {user.username} (role: {user.role})")
            
            # Çerezlerdeki kullanıcı bilgilerini doğrula
            cookie_user_id = request.COOKIES.get('user_id')
            cookie_user_role = request.COOKIES.get('user_role')
            
            if cookie_user_id and str(user.id) != cookie_user_id:
                logger.warning(f"User ID mismatch in cookies: token user {user.id} vs cookie {cookie_user_id}")
            
            if cookie_user_role and user.role != cookie_user_role:
                logger.warning(f"User role mismatch in cookies: token user {user.role} vs cookie {cookie_user_role}")
                
            return user
        else:
            logger.warning(f"Cookie token {token_key[-8:]}... is invalid or expired")
    else:
        logger.info("No auth_token found in cookies")
    
    # 3. POST/GET parametrelerinden token kontrolü
    token_key = request.POST.get('token') or request.GET.get('token')
    if token_key:
        user = get_user_by_token(token_key)
        if user:
            logger.info(f"User authenticated via parameter token: {user.username} (role: {user.role})")
            return user
    
    # 4. Django session authentication (FALLBACK)
    if request.user.is_authenticated:
        logger.info(f"Fallback to session authentication: {request.user.username} (role: {getattr(request.user, 'role', 'unknown')})")
        return request.user
    
    logger.info("No valid authentication found")
    return None

def get_user_by_token(token_key):
    """
    Token key ile kullanıcı bulma ve token güncelleme
    """
    if not token_key:
        logger.info("No token key provided")
        return None
    
    logger.info(f"Looking up token: {token_key[-8:]}...")
        
    # Custom token kontrolü
    try:
        custom_token = CustomAuthToken.objects.get(key=token_key)
        if not custom_token.is_expired():
            custom_token.use_token()  # Son kullanım zamanını güncelle
            logger.info(f"Valid custom token found for user: {custom_token.user.username} (role: {custom_token.user.role})")
            return custom_token.user
        else:
            # Token süresi dolmuş, otomatik yenile
            logger.info(f"Custom token expired for user: {custom_token.user.username}, refreshing...")
            custom_token.refresh_token()
            custom_token.use_token()
            return custom_token.user
    except CustomAuthToken.DoesNotExist:
        logger.warning(f"Custom token not found: {token_key[-8:]}...")
        logger.info(f"Custom token not found: {token_key[-8:]}...")
        pass
        
    # Fallback: Normal DRF token kontrolü
    try:
        normal_token = Token.objects.get(key=token_key)
        logger.info(f"Valid DRF token found for user: {normal_token.user.username}")
        return normal_token.user
    except Token.DoesNotExist:
        logger.warning(f"No valid token found: {token_key[-8:]}...")
        pass
    
    return None

def get_user_token_info(user):
    """
    Kullanıcının token bilgilerini getir
    """
    try:
        custom_token = CustomAuthToken.objects.get(user=user)
        return {
            'token_key': custom_token.key[-8:],  # Son 8 karakter
            'created': custom_token.created,
            'expires_at': custom_token.expires_at,
            'last_used': custom_token.last_used,
            'is_expired': custom_token.is_expired(),
            'days_until_expiry': (custom_token.expires_at - timezone.now()).days if custom_token.expires_at > timezone.now() else 0
        }
    except CustomAuthToken.DoesNotExist:
        return None

@admin_required
def admin_panel_view(request):
    """
    Admin Panel - Sadece admin ve superuser'lar erişebilir
    Gelişmiş yetki kontrolü ve token yönetimi
    """
    logger.info(f"Admin panel access attempt from {request.user}")
    
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    logger.info(f"Token auth result: {user}")
    
    if not user:
        # Ana sayfaya yönlendir (home_view token kontrolü yapacak)
        logger.warning("No user found, redirecting to home with admin-panel redirect")
        return redirect('/?redirect=admin-panel')
    
    # Admin yetki kontrolü - Katı güvenlik
    if not (user.is_superuser or (user.role == 'admin' and user.is_staff)):
        # Yetkisiz erişim - kullanıcı rolüne göre doğru panele yönlendir
        logger.warning(f"User {user.username} (role: {user.role}, is_staff: {user.is_staff}) does not have admin access, redirecting to customer panel")
        # Tüm non-admin kullanıcılar customer panel'e gitsin
        return redirect('/accounts/customer-panel/')
    
    logger.info(f"Admin panel access granted for {user.username}")
    
    # Admin panel context'i hazırla
    context = {
        'panel_title': 'Admin Paneli',
        'user_role': 'Admin',
        'current_user': user,
        'panel_type': 'admin',
        'has_admin_access': True
    }
    
    return render(request, 'accounts/admin_panel.html', context)

def support_panel_view(request):
    """
    Support Panel - Support ve üst yetkiler erişebilir
    Gelişmiş yetki kontrolü ve token yönetimi
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        # Direkt login sayfasına yönlendir
        return redirect('/accounts/login/')
    
    # Support yetki kontrolü - Katı güvenlik
    if not (user.is_superuser or (user.role in ['admin', 'support'] and user.is_staff)):
        # Yetkisiz erişim - customer paneline yönlendir
        logger.warning(f"User {user.username} (role: {user.role}, is_staff: {user.is_staff}) does not have support access, redirecting to customer panel")
        return redirect('/accounts/customer-panel/')
    
    context = {
        'panel_title': 'Destek Paneli',
        'user_role': 'Support',
        'current_user': user,
        'panel_type': 'support',
        'has_support_access': True
    }
    
    return render(request, 'accounts/support_panel.html', context)

def customer_panel_view(request):
    """
    Customer Panel - Tüm kullanıcılar erişebilir
    Gelişmiş token kontrolü ve kullanıcı deneyimi
    """
    from tickets.models import Talep, Category
    from django.db.models import Q
    
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        # Direkt login sayfasına yönlendir (home_view bypass)
        return redirect('/accounts/login/')
    
    # Güvenlik: Sadece customer/support/admin kullanıcılar customer panel'e erişebilir
    # Ama öncelikle customer panel'i herkesin görebilmesi için bu kontrolü gevşetelim
    
    # Kullanıcının kendi talepleri
    my_tickets = Talep.objects.filter(user=user).order_by('-created_at')
    
    # Kullanıcının gruplarının talepleri
    group_tickets = []
    if user.groups.exists():
        user_groups = user.groups.all()
        # Grup adına göre kategorileri bul
        group_categories = Category.objects.filter(name__in=user_groups.values_list('name', flat=True))
        # Bu kategorilerdeki tüm talepleri getir (kendi talepleri hariç)
        group_tickets = Talep.objects.filter(
            category__in=group_categories
        ).exclude(user=user).order_by('-created_at')
    
    # İstatistikler
    my_open_tickets = my_tickets.filter(status__in=['open', 'in_progress'])
    my_closed_tickets = my_tickets.filter(status='closed')
    
    context = {
        'panel_title': 'Müşteri Paneli',
        'user_role': 'Customer',
        'current_user': user,
        'panel_type': 'customer',
        'has_customer_access': True,
        'my_tickets': my_tickets,
        'group_tickets': group_tickets,
        'my_open_tickets_count': my_open_tickets.count(),
        'my_closed_tickets_count': my_closed_tickets.count(),
        'total_tickets_count': my_tickets.count(),
        'user_groups': user.groups.all() if user.groups.exists() else None
    }
    
    return render(request, 'accounts/customer_panel.html', context)

# ================================
# ADMİN KULLANICI YÖNETİMİ VIEW'LARI
# ================================

def admin_users_view(request):
    """
    Admin Kullanıcı Listesi - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=admin-users')
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")
    
    # Tüm kullanıcıları getir
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'current_user': user,
        'user_role': 'Admin',
        'page_title': 'Kullanıcı Yönetimi'
    }
    
    return render(request, 'accounts/admin_users.html', context)

def admin_user_create_view(request):
    """
    Yeni Kullanıcı Oluşturma - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=admin-user-create')
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'customer')
        is_active = request.POST.get('is_active') == 'on'
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        try:
            # Yeni kullanıcı oluştur
            new_user = User.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                role=role,
                is_active=is_active,
                first_name=first_name,
                last_name=last_name
            )
            
            logger.info(f"Admin {user.username} tarafından yeni kullanıcı oluşturuldu: {new_user.username}")
            return redirect('/accounts/admin/users/')
            
        except Exception as e:
            logger.error(f"Kullanıcı oluşturma hatası: {str(e)}")
            context = {
                'error': 'Kullanıcı oluşturulurken bir hata oluştu. Kullanıcı adı zaten mevcut olabilir.',
                'current_user': user,
                'user_role': 'Admin',
                'page_title': 'Yeni Kullanıcı'
            }
            return render(request, 'accounts/admin_user_create.html', context)
    
    context = {
        'current_user': user,
        'user_role': 'Admin',
        'page_title': 'Yeni Kullanıcı'
    }
    
    return render(request, 'accounts/admin_user_create.html', context)

def admin_user_edit_view(request, user_id):
    """
    Kullanıcı Düzenleme - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=admin-user-edit')
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('/accounts/admin/users/')
    
    if request.method == 'POST':
        try:
            # Form verilerini al
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            role = request.POST.get('role', target_user.role)
            is_active = request.POST.get('is_active') == 'on'
            new_password = request.POST.get('password', '').strip()
            
            # Validasyon
            if not username:
                messages.error(request, 'Kullanıcı adı boş olamaz.')
                return render(request, 'accounts/admin_user_edit.html', {
                    'target_user': target_user,
                    'current_user': user,
                    'user_role': 'Admin',
                    'page_title': f'Kullanıcı Düzenle: {target_user.username}'
                })
            
            if not email:
                messages.error(request, 'E-posta adresi boş olamaz.')
                return render(request, 'accounts/admin_user_edit.html', {
                    'target_user': target_user,
                    'current_user': user,
                    'user_role': 'Admin',
                    'page_title': f'Kullanıcı Düzenle: {target_user.username}'
                })
            
            # Username unique kontrolü (kendisi hariç)
            if User.objects.exclude(id=target_user.id).filter(username=username).exists():
                messages.error(request, 'Bu kullanıcı adı zaten kullanılıyor.')
                return render(request, 'accounts/admin_user_edit.html', {
                    'target_user': target_user,
                    'current_user': user,
                    'user_role': 'Admin',
                    'page_title': f'Kullanıcı Düzenle: {target_user.username}'
                })
            
            # Email unique kontrolü (kendisi hariç)
            if User.objects.exclude(id=target_user.id).filter(email=email).exists():
                messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
                return render(request, 'accounts/admin_user_edit.html', {
                    'target_user': target_user,
                    'current_user': user,
                    'user_role': 'Admin',
                    'page_title': f'Kullanıcı Düzenle: {target_user.username}'
                })
            
            # Verileri güncelle
            target_user.username = username
            target_user.email = email
            target_user.first_name = first_name
            target_user.last_name = last_name
            target_user.role = role
            target_user.is_active = is_active
            
            # Şifre değiştirilmişse güncelle
            if new_password:
                target_user.password = make_password(new_password)
            
            target_user.save()
            
            logger.info(f"Admin {user.username} tarafından kullanıcı güncellendi: {target_user.username}")
            messages.success(request, f'{target_user.username} kullanıcısı başarıyla güncellendi.')
            return redirect('/accounts/admin/users/')
            
        except Exception as e:
            logger.error(f"Kullanıcı güncellenirken hata: {str(e)}")
            messages.error(request, 'Kullanıcı güncellenirken bir hata oluştu.')
            return render(request, 'accounts/admin_user_edit.html', {
                'target_user': target_user,
                'current_user': user,
                'user_role': 'Admin',
                'page_title': f'Kullanıcı Düzenle: {target_user.username}'
            })
    
    context = {
        'target_user': target_user,
        'current_user': user,
        'user_role': 'Admin',
        'page_title': f'Kullanıcı Düzenle: {target_user.username}'
    }
    
    return render(request, 'accounts/admin_user_edit.html', context)

def admin_user_delete_view(request, user_id):
    """
    Kullanıcı Silme - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=admin-user-delete')
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")
    
    try:
        target_user = User.objects.get(id=user_id)
        
        # Kendi hesabını silmeye izin verme
        if target_user.id == user.id:
            return HttpResponseForbidden("Kendi hesabınızı silemezsiniz.")
        
        if request.method == 'POST':
            username = target_user.username
            target_user.delete()
            
            logger.info(f"Admin {user.username} tarafından kullanıcı silindi: {username}")
            return redirect('/accounts/admin/users/')
            
    except User.DoesNotExist:
        return redirect('/accounts/admin/users/')
    
    context = {
        'target_user': target_user,
        'current_user': user,
        'user_role': 'Admin',
        'page_title': f'Kullanıcı Sil: {target_user.username}'
    }
    
    return render(request, 'accounts/admin_user_delete.html', context)

# ================================
# GRUP YÖNETİMİ VIEW'LARI
# ================================

def admin_groups_view(request):
    """
    Admin Grup Listesi - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=admin-groups')
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")
    
    # Tüm grupları getir
    groups = Group.objects.all().order_by('name')
    
    context = {
        'groups': groups,
        'current_user': user,
        'user_role': 'Admin',
        'page_title': 'Grup Yönetimi'
    }
    
    return render(request, 'accounts/admin_groups.html', context)

def admin_group_create_view(request):
    """
    Yeni Grup Oluşturma - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=admin-group-create')
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")
    
    if request.method == 'POST':
        group_name = request.POST.get('name')
        
        try:
            # Yeni grup oluştur
            new_group = Group.objects.create(name=group_name)
            
            logger.info(f"Admin {user.username} tarafından yeni grup oluşturuldu: {new_group.name}")
            return redirect('/accounts/admin/groups/')
            
        except Exception as e:
            logger.error(f"Grup oluşturma hatası: {str(e)}")
            context = {
                'error': 'Grup oluşturulurken bir hata oluştu.',
                'current_user': user,
                'user_role': 'Admin',
                'page_title': 'Yeni Grup'
            }
            return render(request, 'accounts/admin_group_create.html', context)
    
    context = {
        'current_user': user,
        'user_role': 'Admin',
        'page_title': 'Yeni Grup'
    }
    
    return render(request, 'accounts/admin_group_create.html', context)

def admin_group_delete_view(request, group_id):
    """
    Grup Silme - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return JsonResponse({'error': 'Kimlik doğrulama gerekli'}, status=401)
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return JsonResponse({'error': 'Bu işlem için yetkiniz yok'}, status=403)
    
    try:
        group = Group.objects.get(id=group_id)
        group_name = group.name
        user_count = group.customuser_set.count()
        
        # Grup silme işlemi
        group.delete()
        
        logger.info(f"Admin {user.username} tarafından '{group_name}' grubu silindi (önceki kullanıcı sayısı: {user_count})")
        
        return JsonResponse({
            'success': True,
            'message': f'"{group_name}" grubu başarıyla silindi.',
            'deleted_group': {
                'id': group_id,
                'name': group_name,
                'user_count': user_count
            }
        })
        
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Grup bulunamadı'}, status=404)
    
    except Exception as e:
        logger.error(f"Grup silme hatası: {str(e)}")
        return JsonResponse({'error': f'Grup silinirken hata oluştu: {str(e)}'}, status=500)

def admin_user_assign_groups_view(request, user_id):
    """
    Kullanıcıya Grup Atama - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=admin-user-assign-groups')
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('/accounts/admin/users/')
    
    # Tüm grupları getir
    all_groups = Group.objects.all().order_by('name')
    user_groups = target_user.groups.all()
    
    if request.method == 'POST':
        selected_groups = request.POST.getlist('groups')
        
        # Kullanıcının gruplarını güncelle
        target_user.groups.clear()
        for group_id in selected_groups:
            try:
                group = Group.objects.get(id=group_id)
                target_user.groups.add(group)
            except Group.DoesNotExist:
                continue
        
        logger.info(f"Admin {user.username} tarafından {target_user.username} kullanıcısının grupları güncellendi")
        return redirect('/accounts/admin/users/')
    
    context = {
        'target_user': target_user,
        'all_groups': all_groups,
        'user_groups': user_groups,
        'current_user': user,
        'user_role': 'Admin',
        'page_title': f'Grup Atama: {target_user.username}'
    }
    
    return render(request, 'accounts/admin_user_assign_groups.html', context)


# ================================
# Additional Admin Management Views
# ================================

def admin_settings_view(request):
    """
    Sistem Ayarları - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=admin-settings')
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")
    
    context = {
        'current_user': user,
        'user_role': 'Admin',
        'page_title': 'Sistem Ayarları'
    }
    
    return render(request, 'accounts/admin_settings.html', context)

def admin_reports_view(request):
    """
    Raporlar - Sadece admin erişebilir
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=admin-reports')
    
    # Admin kontrolü
    if not (user.is_superuser or user.role == 'admin'):
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")
    
    context = {
        'current_user': user,
        'user_role': 'Admin',
        'page_title': 'Raporlar'
    }
    
    return render(request, 'accounts/admin_reports.html', context)


# ================================
# Customer Management Views
# ================================

def customer_profile_view(request):
    """
    Müşteri Profil Görüntüleme
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=customer-profile')
    
    context = {
        'current_user': user,
        'user_role': user.get_role_display(),
        'page_title': 'Profil Bilgileri'
    }
    
    return render(request, 'accounts/customer_profile.html', context)

def customer_profile_edit_view(request):
    """
    Müşteri Profil Düzenleme
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=customer-profile-edit')
    
    if request.method == 'POST':
        try:
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', user.email)
            user.save()
            
            logger.info(f"Kullanıcı {user.username} profil bilgilerini güncelledi")
            return redirect('/accounts/customer/profile/')
            
        except Exception as e:
            logger.error(f"Profil güncelleme hatası: {str(e)}")
            context = {
                'error': 'Profil güncellenirken bir hata oluştu.',
                'current_user': user,
                'user_role': user.get_role_display(),
                'page_title': 'Profil Düzenle'
            }
            return render(request, 'accounts/customer_profile_edit.html', context)
    
    context = {
        'current_user': user,
        'user_role': user.get_role_display(),
        'page_title': 'Profil Düzenle'
    }
    
    return render(request, 'accounts/customer_profile_edit.html', context)

def customer_change_password_view(request):
    """
    Müşteri Şifre Değiştirme
    """
    # Token tabanlı kimlik doğrulama
    user = verify_token_auth(request)
    
    if not user:
        return redirect('/accounts/login/?next=customer-change-password')
    
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Şifre kontrolü
        if not user.check_password(old_password):
            context = {
                'error': 'Mevcut şifreniz yanlış.',
                'current_user': user,
                'user_role': user.get_role_display(),
                'page_title': 'Şifre Değiştir'
            }
            return render(request, 'accounts/customer_change_password.html', context)
        
        # Yeni şifre kontrolü
        if new_password != confirm_password:
            context = {
                'error': 'Yeni şifreler eşleşmiyor.',
                'current_user': user,
                'user_role': user.get_role_display(),
                'page_title': 'Şifre Değiştir'
            }
            return render(request, 'accounts/customer_change_password.html', context)
        
        # Şifre uzunluk kontrolü
        if len(new_password) < 6:
            context = {
                'error': 'Yeni şifre en az 6 karakter olmalıdır.',
                'current_user': user,
                'user_role': user.get_role_display(),
                'page_title': 'Şifre Değiştir'
            }
            return render(request, 'accounts/customer_change_password.html', context)
        
        try:
            user.set_password(new_password)
            user.save()
            
            logger.info(f"Kullanıcı {user.username} şifresini değiştirdi")
            return redirect('/accounts/customer/profile/')
            
        except Exception as e:
            logger.error(f"Şifre değiştirme hatası: {str(e)}")
            context = {
                'error': 'Şifre değiştirilirken bir hata oluştu.',
                'current_user': user,
                'user_role': user.get_role_display(),
                'page_title': 'Şifre Değiştir'
            }
            return render(request, 'accounts/customer_change_password.html', context)
    
    context = {
        'current_user': user,
        'user_role': user.get_role_display(),
        'page_title': 'Şifre Değiştir'
    }
    
    return render(request, 'accounts/customer_change_password.html', context)
