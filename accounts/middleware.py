# accounts/middleware.py
# ================================================================================
# Custom Middleware - Token Authentication
# HTTP isteklerini yakalayıp token tabanlı kimlik doğrulama sağlar
# ================================================================================

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model, login
from rest_framework.authtoken.models import Token
from .models import CustomAuthToken
import logging

User = get_user_model()  # CustomUser modelini dinamik olarak al
logger = logging.getLogger(__name__)  # Logging sistemi

class TokenAuthMiddleware(MiddlewareMixin):
    """
    Gelişmiş Token-based authentication middleware
    - Cookie ve header'dan token okuma
    - Custom token desteği
    - Session integration
    """
    
    def process_request(self, request):
        """
        Her HTTP isteğinde çalışan ana metod
        Token tabanlı kimlik doğrulama yapar
        """
        # Zaten authenticated ise işlem yapma
        if request.user.is_authenticated:
            return None
            
        # API endpoint'lerde DRF'nin kendi auth'unu kullan
        if request.path.startswith('/accounts/api/'):
            return None
        
        user = None
        token_source = None
            
        # 1. Authorization header'ından token'ı al
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            user = self.get_user_by_token(token_key)
            if user:
                token_source = 'header'
        
        # 2. Cookie'den token'ı al (header'da yoksa)
        if not user:
            token_key = request.COOKIES.get('auth_token')
            if token_key:
                user = self.get_user_by_token(token_key)
                if user:
                    token_source = 'cookie'
        
        # Kullanıcı bulunduysa session'a ekle
        if user:
            request.user = user
            # Session'a kullanıcıyı eklemek için özel backend kullan
            # Bu sayede request.user.is_authenticated True olur
            if not hasattr(request, '_dont_enforce_csrf_checks'):
                request._dont_enforce_csrf_checks = True
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            logger.info(f"User {user.username} authenticated via {token_source}")
        
        return None
    
    def get_user_by_token(self, token_key):
        """
        Token key ile kullanıcı bulma ve doğrulama
        Önce custom token, sonra DRF token kontrol eder
        """
        if not token_key:
            return None
            
        # 1. Custom token kontrolü (öncelikli)
        try:
            custom_token = CustomAuthToken.objects.get(key=token_key)
            if not custom_token.is_expired():
                custom_token.use_token()  # Son kullanım zamanını güncelle
                return custom_token.user
            else:
                # Token süresi dolmuş, otomatik yenile
                custom_token.refresh_token()
                custom_token.use_token()
                return custom_token.user
        except CustomAuthToken.DoesNotExist:
            pass
            
        # 2. Fallback: Normal DRF token kontrolü
        try:
            normal_token = Token.objects.get(key=token_key)
            return normal_token.user
        except Token.DoesNotExist:
            pass
        
        return None