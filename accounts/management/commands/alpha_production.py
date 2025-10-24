"""
Alpha Production Management Command
HelpDesk Alpha Release - Production utilities
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model
from accounts.models import CustomAuthToken
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Alpha Production setup and management utilities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--setup',
            action='store_true',
            help='Run alpha production setup',
        )
        parser.add_argument(
            '--status',
            action='store_true',
            help='Show alpha production status',
        )
        parser.add_argument(
            '--create-admin',
            action='store_true',
            help='Create admin user for alpha',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up tokens and sessions',
        )
        parser.add_argument(
            '--start-server',
            action='store_true',
            help='Start Gunicorn production server',
        )
        parser.add_argument(
            '--server-status',
            action='store_true',
            help='Check server status',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 HelpDesk Alpha Production Manager'))
        self.stdout.write('=' * 50)
        
        if options['setup']:
            self.setup_alpha()
        elif options['status']:
            self.show_status()
        elif options['create_admin']:
            self.create_admin()
        elif options['cleanup']:
            self.cleanup_system()
        elif options['start_server']:
            self.start_production_server()
        elif options['server_status']:
            self.check_server_status()
        else:
            self.show_help()

    def setup_alpha(self):
        """Alpha production kurulumu"""
        self.stdout.write('📋 Alpha Production Setup Starting...')
        
        # Check environment
        self.stdout.write('🔍 Checking environment...')
        self.stdout.write(f'   DEBUG: {settings.DEBUG}')
        self.stdout.write(f'   ALPHA_MODE: {getattr(settings, "ALPHA_MODE", False)}')
        self.stdout.write(f'   SECRET_KEY: {"✅ Set" if settings.SECRET_KEY else "❌ Missing"}')
        
        # Create logs directory
        logs_dir = settings.BASE_DIR / 'logs'
        if not logs_dir.exists():
            logs_dir.mkdir()
            self.stdout.write('📁 Created logs directory')
        
        # Create admin user if not exists
        if not User.objects.filter(is_superuser=True).exists():
            self.create_admin()
        else:
            self.stdout.write('👤 Admin user already exists')
        
        self.stdout.write(self.style.SUCCESS('✅ Alpha Production setup completed!'))

    def show_status(self):
        """Alpha production durumunu göster"""
        self.stdout.write('📊 Alpha Production Status')
        self.stdout.write('-' * 30)
        
        # Environment info
        self.stdout.write(f'Environment: {"Alpha Production" if not settings.DEBUG else "Development"}')
        self.stdout.write(f'Alpha Mode: {getattr(settings, "ALPHA_MODE", False)}')
        self.stdout.write(f'Debug: {settings.DEBUG}')
        self.stdout.write('')
        
        # Database info
        self.stdout.write('📊 Database Statistics:')
        user_count = User.objects.count()
        admin_count = User.objects.filter(role='admin').count()
        support_count = User.objects.filter(role='support').count()
        customer_count = User.objects.filter(role='customer').count()
        
        self.stdout.write(f'   Total Users: {user_count}')
        self.stdout.write(f'   Admins: {admin_count}')
        self.stdout.write(f'   Support: {support_count}')
        self.stdout.write(f'   Customers: {customer_count}')
        
        # Token info
        token_count = CustomAuthToken.objects.count()
        self.stdout.write(f'   Active Tokens: {token_count}')
        
        # Ticket info
        try:
            from tickets.models import Talep
            ticket_count = Talep.objects.count()
            open_tickets = Talep.objects.filter(status__in=['Açık', 'Devam ediyor']).count()
            self.stdout.write(f'   Total Tickets: {ticket_count}')
            self.stdout.write(f'   Open Tickets: {open_tickets}')
        except:
            self.stdout.write('   Tickets: N/A')

    def create_admin(self):
        """Alpha admin kullanıcısı oluştur"""
        self.stdout.write('👤 Creating alpha admin user...')
        
        try:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@helpdesk-alpha.local',
                password='alpha123!',
                role='admin',
                first_name='Alpha',
                last_name='Administrator'
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Admin user created: {admin_user.username}'))
            self.stdout.write('🔑 Credentials: admin / alpha123!')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating admin: {e}'))

    def cleanup_system(self):
        """Sistem temizliği"""
        self.stdout.write('🧹 System cleanup starting...')
        
        # Clean expired tokens
        from django.utils import timezone
        from datetime import timedelta
        
        expired_tokens = CustomAuthToken.objects.filter(
            last_used__lt=timezone.now() - timedelta(days=7)
        )
        expired_count = expired_tokens.count()
        expired_tokens.delete()
        
        self.stdout.write(f'🗑️  Cleaned {expired_count} expired tokens')
        
        # Clear cache
        from django.core.cache import cache
        cache.clear()
        self.stdout.write('🗑️  Cleared cache')
        
        self.stdout.write(self.style.SUCCESS('✅ System cleanup completed!'))

    def start_production_server(self):
        """Windows için Waitress production server başlat"""
        self.stdout.write('🚀 Starting Waitress Production Server (Windows)...')
        
        import subprocess
        import os
        
        # Waitress kurulu mu kontrol et
        try:
            import waitress
        except ImportError:
            self.stdout.write(self.style.ERROR('❌ Waitress not installed. Run: pip install waitress'))
            return
        
        # Logs klasörü oluştur
        logs_dir = settings.BASE_DIR / 'logs'
        if not logs_dir.exists():
            logs_dir.mkdir()
            
        self.stdout.write('📊 Server Info:')
        self.stdout.write(f'   Host: 0.0.0.0:8000')
        self.stdout.write(f'   Threads: 6 (Windows optimized)')
        self.stdout.write(f'   Server: Waitress (Windows compatible)')
        self.stdout.write('🔑 Admin: admin / alpha123!')
        self.stdout.write('')
        self.stdout.write('🛑 Stop server: Ctrl+C')
        self.stdout.write('')
        
        # Waitress başlat
        try:
            os.chdir(settings.BASE_DIR)
            subprocess.run(['python', 'production_server.py'])
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\n🛑 Production server stopped.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Server error: {e}'))

    def check_server_status(self):
        """Server durumunu kontrol et"""
        self.stdout.write('🔍 Checking server status...')
        
        import socket
        import requests
        from urllib.parse import urljoin
        
        # Port kontrolü
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            self.stdout.write(self.style.SUCCESS('✅ Port 8000 is open'))
            
            # HTTP isteği test et
            try:
                response = requests.get('http://localhost:8000/', timeout=5)
                self.stdout.write(f'✅ HTTP Response: {response.status_code}')
                if response.status_code == 200:
                    self.stdout.write(self.style.SUCCESS('🌐 Server is running successfully!'))
                    self.stdout.write('📍 Access: http://localhost:8000')
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Server responding but status: {response.status_code}'))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'❌ HTTP request failed: {e}'))
        else:
            self.stdout.write(self.style.ERROR('❌ Port 8000 is closed - server not running'))
            self.stdout.write('💡 Start server with: python manage.py alpha_production --start-server')

        self.stdout.write(self.style.SUCCESS('✅ System cleanup completed!'))

    def show_help(self):
        """Yardım göster"""
        self.stdout.write('Available commands:')
        self.stdout.write('  --setup        : Run alpha production setup')
        self.stdout.write('  --status       : Show system status')
        self.stdout.write('  --create-admin : Create admin user')
        self.stdout.write('  --cleanup      : Clean up system')
        self.stdout.write('  --start-server : Start Gunicorn production server')
        self.stdout.write('  --server-status: Check if server is running')
        self.stdout.write('')
        self.stdout.write('Examples:')
        self.stdout.write('  python manage.py alpha_production --setup')
        self.stdout.write('  python manage.py alpha_production --start-server')