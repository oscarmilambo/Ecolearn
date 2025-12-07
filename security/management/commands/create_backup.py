from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()
from security.backup import BackupManager

class Command(BaseCommand):
    help = 'Create system backup'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['full', 'database', 'media', 'logs'],
            default='full',
            help='Type of backup to create'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username of the user creating the backup'
        )
    
    def handle(self, *args, **options):
        backup_type = options['type']
        username = options.get('user')
        
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'User {username} not found, creating backup without user')
                )
        
        backup_manager = BackupManager()
        
        try:
            if backup_type == 'full':
                backup = backup_manager.create_full_backup(user)
            elif backup_type == 'database':
                backup = backup_manager.create_database_backup(user)
            elif backup_type == 'media':
                backup = backup_manager.create_media_backup(user)
            elif backup_type == 'logs':
                backup = backup_manager.create_logs_backup(user)
            
            self.stdout.write(
                self.style.SUCCESS(f'{backup_type.title()} backup created successfully: {backup.id}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Backup failed: {str(e)}')
            )