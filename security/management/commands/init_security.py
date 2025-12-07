from django.core.management.base import BaseCommand
from security.models import Role
from security.permissions import DEFAULT_ROLE_PERMISSIONS

class Command(BaseCommand):
    help = 'Initialize security roles and permissions'
    
    def handle(self, *args, **options):
        try:
            created_count = 0
            updated_count = 0
            
            for role_name, permissions in DEFAULT_ROLE_PERMISSIONS.items():
                role, created = Role.objects.get_or_create(
                    name=role_name,
                    defaults={
                        'description': f'Default {role_name} role',
                        'permissions': permissions
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'Created role: {role_name}')
                else:
                    role.permissions = permissions
                    role.save()
                    updated_count += 1
                    self.stdout.write(f'Updated role: {role_name}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Security initialization complete. '
                    f'Created: {created_count}, Updated: {updated_count}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Security initialization failed: {str(e)}')
            )