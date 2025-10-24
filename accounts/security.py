from django.core.cache import cache
from django.http import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class HttpResponseTooManyRequests(HttpResponse):
    status_code = 429

def rate_limit_login(max_attempts=5, window_minutes=15):
    """
    Login denemelerini sınırla
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # IP adresini al
            ip_address = get_client_ip(request)
            cache_key = f"login_attempts_{ip_address}"
            
            # Mevcut deneme sayısını kontrol et
            attempts = cache.get(cache_key, 0)
            
            if attempts >= max_attempts:
                logger.warning(f"Rate limit exceeded for IP: {ip_address}")
                return HttpResponseTooManyRequests(
                    "Too many login attempts. Please try again later."
                )
            
            # View'ı çalıştır
            response = view_func(request, *args, **kwargs)
            
            # Başarısız login denemelerini say
            if hasattr(response, 'status_code') and response.status_code == 400:
                cache.set(cache_key, attempts + 1, timeout=window_minutes * 60)
                logger.info(f"Failed login attempt from IP: {ip_address}, attempt: {attempts + 1}")
            elif hasattr(response, 'status_code') and response.status_code == 200:
                # Başarılı login, cache'i temizle
                cache.delete(cache_key)
                logger.info(f"Successful login from IP: {ip_address}")
            
            return response
        return wrapper
    return decorator

def get_client_ip(request):
    """
    Client IP adresini güvenli şekilde al
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def sanitize_input(input_string, max_length=255):
    """
    Kullanıcı girdilerini temizle
    """
    if not input_string:
        return ""
    
    # HTML karakterlerini escape et (sadece genel input'lar için)
    import html
    cleaned = html.escape(str(input_string))
    
    # Uzunluğu sınırla
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    # Boşlukları temizle
    cleaned = cleaned.strip()
    
    return cleaned

def sanitize_username(username, max_length=150):
    """
    Username'leri temizle - HTML escape yapmadan
    """
    if not username:
        return ""
    
    # Sadece string'e çevir ve boşlukları temizle
    cleaned = str(username).strip()
    
    # Uzunluğu sınırla
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned

def validate_password_strength(password):
    """
    Şifre güçlülüğünü kontrol et
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter.")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter.")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit.")
    
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        errors.append("Password must contain at least one special character.")
    
    return errors

def admin_required(view_func):
    """
    Admin yetkisi gerektiren view'lar için decorator
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .views import verify_token_auth
        
        user = verify_token_auth(request)
        
        if not user:
            logger.warning(f"Unauthorized access attempt to admin view from IP: {get_client_ip(request)}")
            return HttpResponse("Authentication required", status=401)
        
        if not (user.is_superuser or user.role == 'admin'):
            logger.warning(f"Non-admin user {user.username} attempted to access admin view")
            return HttpResponse("Admin access required", status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper

class SecurityMiddleware:
    """
    Güvenlik middleware'i
    """
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Request processing
        self.process_request(request)
        
        response = self.get_response(request)
        
        # Response processing
        self.process_response(request, response)
        
        return response
    
    def process_request(self, request):
        """
        Request'i işle
        """
        # Suspicious patterns check
        suspicious_patterns = [
            'script', 'javascript:', 'vbscript:', 'onload', 'onerror',
            'eval(', 'document.cookie', '<script', '</script>',
            'union select', 'drop table', 'delete from', '--',
            '/*', '*/', 'xp_cmdshell', 'sp_executesql'
        ]
        
        for key, value in request.GET.items():
            if any(pattern in str(value).lower() for pattern in suspicious_patterns):
                logger.warning(f"Suspicious GET parameter detected from IP {get_client_ip(request)}: {key}={value}")
        
        for key, value in request.POST.items():
            if any(pattern in str(value).lower() for pattern in suspicious_patterns):
                logger.warning(f"Suspicious POST parameter detected from IP {get_client_ip(request)}: {key}={value}")
    
    def process_response(self, request, response):
        """
        Response'u işle
        """
        # Security headers ekle
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response