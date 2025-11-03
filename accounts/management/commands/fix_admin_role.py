from django.core.management.base import BaseCommand
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Fix admin user role to admin'

    def handle(self, *args, **options):
        try:
            # Admin kullanıcısını bul
            admin_user = CustomUser.objects.get(username='admin')
            
            # Role'unu admin olarak ayarla
            admin_user.role = 'admin'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Admin kullanıcısının role\'u başarıyla admin olarak güncellendi.\n'
                    f'Username: {admin_user.username}\n'
                    f'Role: {admin_user.role}\n'
                    f'Is Staff: {admin_user.is_staff}\n'
                    f'Is Superuser: {admin_user.is_superuser}'
                )
            )
            
        except CustomUser.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Admin kullanıcısı bulunamadı!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Hata oluştu: {str(e)}')
            )