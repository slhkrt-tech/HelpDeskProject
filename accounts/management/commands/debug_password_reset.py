# accounts/management/commands/debug_password_reset.py
# ================================================================================
# Django Management Command - Password Reset Debug
# Web form'daki password reset sorununu debug eder
# ================================================================================

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()

class Command(BaseCommand):
    help = 'Password reset web form debug'
    
    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Test edilecek email adresi')
    
    def handle(self, *args, **options):
        email = options['email']
        
        # Test client oluştur
        client = Client()
        
        self.stdout.write('🌐 Web form test başlıyor...')
        
        try:
            # Password reset form sayfasını al
            response = client.get('/auth/password_reset/')
            self.stdout.write(f'📄 Password reset form status: {response.status_code}')
            
            if response.status_code == 200:
                self.stdout.write('✅ Password reset form sayfası yüklendi')
                
                # Form POST test et
                post_data = {'email': email}
                response = client.post('/auth/password_reset/', post_data)
                
                self.stdout.write(f'📤 Form POST status: {response.status_code}')
                
                if response.status_code == 302:
                    self.stdout.write('✅ Form başarıyla gönderildi (redirect aldı)')
                    self.stdout.write(f'🔗 Redirect URL: {response.url}')
                else:
                    self.stdout.write('❌ Form POST başarısız')
                    if hasattr(response, 'context') and response.context:
                        form = response.context.get('form')
                        if form and form.errors:
                            self.stdout.write(f'Form hataları: {form.errors}')
            else:
                self.stdout.write('❌ Password reset form sayfası yüklenemedi')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Test hatası: {str(e)}')
            )
            
        # URL'leri kontrol et
        self.stdout.write('\n🔗 URL Kontrolü:')
        try:
            reset_url = reverse('password_reset')
            self.stdout.write(f'✅ password_reset URL: {reset_url}')
            
            done_url = reverse('password_reset_done') 
            self.stdout.write(f'✅ password_reset_done URL: {done_url}')
            
        except Exception as e:
            self.stdout.write(f'❌ URL reverse hatası: {str(e)}')