from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Token yönetimi - token oluşturma, silme, yenileme'

    def add_arguments(self, parser):
        parser.add_argument(
            '--refresh-all',
            action='store_true',
            help='Tüm kullanıcıların token\'larını yenile',
        )
        parser.add_argument(
            '--delete-expired',
            action='store_true',
            help='Eski token\'ları sil (30 günden eski)',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Belirli bir kullanıcının token\'ını yenile',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='Tüm token\'ları listele',
        )

    def handle(self, *args, **options):
        if options['refresh_all']:
            self.refresh_all_tokens()
        elif options['delete_expired']:
            self.delete_expired_tokens()
        elif options['user']:
            self.refresh_user_token(options['user'])
        elif options['list']:
            self.list_tokens()
        else:
            self.stdout.write(
                self.style.WARNING('Kullanım: --refresh-all, --delete-expired, --user <username>, --list')
            )

    def refresh_all_tokens(self):
        """Tüm kullanıcıların token'larını yenile"""
        users = User.objects.all()
        
        for user in users:
            # Eski token'ı sil
            Token.objects.filter(user=user).delete()
            # Yeni token oluştur
            Token.objects.create(user=user)
            
        self.stdout.write(
            self.style.SUCCESS(f'{users.count()} kullanıcının token\'ı yenilendi.')
        )

    def delete_expired_tokens(self):
        """30 günden eski token'ları sil"""
        expire_date = timezone.now() - timedelta(days=30)
        expired_tokens = Token.objects.filter(created__lt=expire_date)
        count = expired_tokens.count()
        expired_tokens.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'{count} eski token silindi.')
        )

    def refresh_user_token(self, username):
        """Belirli bir kullanıcının token'ını yenile"""
        try:
            user = User.objects.get(username=username)
            Token.objects.filter(user=user).delete()
            Token.objects.create(user=user)
            
            self.stdout.write(
                self.style.SUCCESS(f'{username} kullanıcısının token\'ı yenilendi.')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'{username} kullanıcısı bulunamadı.')
            )

    def list_tokens(self):
        """Tüm token'ları listele"""
        tokens = Token.objects.select_related('user').all()
        
        self.stdout.write('Token Listesi:')
        self.stdout.write('-' * 60)
        
        for token in tokens:
            self.stdout.write(
                f'{token.user.username:<20} | {token.key[:20]}... | {token.created}'
            )
        
        self.stdout.write(f'\nToplam: {tokens.count()} token')