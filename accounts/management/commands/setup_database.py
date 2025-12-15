from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Set up database with proper tables and admin user'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Setting up database...")
        
        # Check database configuration
        db_config = settings.DATABASES['default']
        self.stdout.write(f"Database engine: {db_config['ENGINE']}")
        
        if 'sqlite' in db_config['ENGINE']:
            self.stdout.write(
                self.style.WARNING('⚠️  Using SQLite - should be PostgreSQL in production!')
            )
        elif 'postgresql' in db_config['ENGINE']:
            self.stdout.write(
                self.style.SUCCESS('✅ Using PostgreSQL (correct)')
            )
        
        # Test database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(
                self.style.SUCCESS('✅ Database connection successful')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Database connection failed: {e}')
            )
            return
        
        # Run migrations
        self.stdout.write("🔧 Running migrations...")
        try:
            call_command('makemigrations', verbosity=0, interactive=False)
            call_command('migrate', verbosity=0, interactive=False)
            self.stdout.write(
                self.style.SUCCESS('✅ Migrations completed')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Migration failed: {e}')
            )
            return
        
        # Create admin user
        User = get_user_model()
        try:
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    password='admin123'
                )
                self.stdout.write(
                    self.style.SUCCESS('✅ Admin user created (admin/admin123)')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ Admin user already exists')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Admin user creation failed: {e}')
            )
        
        # Test CustomUser table
        try:
            user_count = User.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'✅ CustomUser table working - {user_count} users found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ CustomUser table issue: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Database setup completed!')
        )