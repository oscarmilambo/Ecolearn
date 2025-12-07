from django.core.management.base import BaseCommand
from security.backup import BackupManager

class Command(BaseCommand):
    help = 'Clean up expired backups'
    
    def handle(self, *args, **options):
        backup_manager = BackupManager()
        
        try:
            backup_manager.cleanup_old_backups()
            self.stdout.write(
                self.style.SUCCESS('Expired backups cleaned up successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Cleanup failed: {str(e)}')
            )