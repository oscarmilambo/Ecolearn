from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate
from django.db import connection

class Command(BaseCommand):
    help = 'Reset admin credentials'

    def handle(self, *args, **options):
        User = get_user_model()
        
        self.stdout.write("🔧 Resetting admin credentials...")
        
        # Check database connection
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
        
        # Delete existing admin users
        try:
            admin_users = User.objects.filter(is_superuser=True)
            admin_count = admin_users.count()
            if admin_count > 0:
                admin_users.delete()
                self.stdout.write(f"🗑️  Deleted {admin_count} existing admin users")
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Could not delete existing admin users: {e}')
            )
        
        # Create new admin user
        try:
            admin_user = User.objects.create_superuser(
                username='admin',
                password='admin123',
                email='admin@ecolearn.com'
            )
            self.stdout.write(
                self.style.SUCCESS('✅ New admin user created successfully!')
            )
            self.stdout.write("   Username: admin")
            self.stdout.write("   Password: admin123")
            self.stdout.write("   Email: admin@ecolearn.com")
            
            # Verify the user was created
            if admin_user.check_password('admin123'):
                self.stdout.write(
                    self.style.SUCCESS('✅ Password verification successful')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Password verification failed')
                )
                return
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Admin user creation failed: {e}')
            )
            return
        
        # Test authentication
        try:
            user = authenticate(username='admin', password='admin123')
            if user:
                self.stdout.write(
                    self.style.SUCCESS('✅ Authentication test successful')
                )
                self.stdout.write(f"   User ID: {user.id}")
                self.stdout.write(f"   Is superuser: {user.is_superuser}")
                self.stdout.write(f"   Is staff: {user.is_staff}")
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Authentication test failed')
                )
                return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Authentication test error: {e}')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Admin credentials reset completed successfully!')
        )