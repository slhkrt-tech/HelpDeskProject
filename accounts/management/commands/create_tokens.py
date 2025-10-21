from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

class Command(BaseCommand):
    help = 'Mevcut kullanıcılar için token oluştur'

    def handle(self, *args, **options):
        users_without_tokens = User.objects.filter(auth_token__isnull=True)
        
        for user in users_without_tokens:
            Token.objects.create(user=user)
            self.stdout.write(
                self.style.SUCCESS(f'Token oluşturuldu: {user.username}')
            )
        
        if users_without_tokens.count() == 0:
            self.stdout.write(
                self.style.WARNING('Tüm kullanıcıların zaten token\'ı var.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'{users_without_tokens.count()} kullanıcı için token oluşturuldu.')
            )