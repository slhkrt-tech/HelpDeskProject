# accounts/management/commands/update_user_email.py
# ================================================================================
# Django Management Command - Kullanıcı Email Güncelleme
# Password reset test etmek için kullanıcıya email adresi ekleme
# ================================================================================

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Kullanıcıya email adresi ekler (password reset test için)'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Kullanıcı adı')
        parser.add_argument('email', type=str, help='Email adresi')
    
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        
        try:
            user = User.objects.get(username=username)
            user.email = email
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Kullanıcı "{username}" için email "{email}" başarıyla güncellendi.'
                )
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Kullanıcı "{username}" bulunamadı.'
                )
            )
            
            # Mevcut kullanıcıları listele
            users = User.objects.all()
            if users.exists():
                self.stdout.write('\n📋 Mevcut kullanıcılar:')
                for user in users:
                    email_info = f' ({user.email})' if user.email else ' (email yok)'
                    self.stdout.write(f'  • {user.username}{email_info}')
            else:
                self.stdout.write('❌ Hiç kullanıcı bulunamadı.')