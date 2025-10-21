# accounts/management/commands/test_password_reset.py
# ================================================================================
# Django Management Command - Password Reset Test
# Password reset sisteminin çalışıp çalışmadığını test eder
# ================================================================================

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Password reset sistemini test eder'
    
    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Test edilecek email adresi')
    
    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Token generate et
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Reset URL oluştur
            reset_url = f"http://127.0.0.1:8000/auth/reset/{uid}/{token}/"
            
            self.stdout.write(f'👤 Kullanıcı: {user.username}')
            self.stdout.write(f'📧 Email: {user.email}')
            self.stdout.write(f'🔗 Reset URL: {reset_url}')
            
            # Email gönderim testi
            subject = 'Password Reset Test'
            message = f'''
Merhaba {user.username},

Password reset test mesajı.

Reset linki: {reset_url}

Bu link 24 saat geçerlidir.
'''
            
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            
            self.stdout.write('\n📤 Email gönderim testi başlıyor...')
            
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=False,
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ Email başarıyla gönderildi! (Console backend kullanılıyor)')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Email gönderim hatası: {str(e)}')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ "{email}" adresine sahip kullanıcı bulunamadı.')
            )
            
            # Email'li kullanıcıları listele
            users_with_email = User.objects.exclude(email='')
            if users_with_email.exists():
                self.stdout.write('\n📋 Email adresine sahip kullanıcılar:')
                for user in users_with_email:
                    self.stdout.write(f'  • {user.username} ({user.email})')
            else:
                self.stdout.write('❌ Hiç kullanıcı email adresi bulunamadı.')