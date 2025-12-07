import os
import shutil
import subprocess
import gzip
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from .models import BackupRecord
from .encryption import SecureFileHandler
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """Handle system backups and restoration"""
    
    def __init__(self):
        self.backup_dir = getattr(settings, 'BACKUP_DIR', os.path.join(settings.BASE_DIR, 'backups'))
        self.secure_handler = SecureFileHandler()
        self.ensure_backup_directory()
    
    def ensure_backup_directory(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_database_backup(self, user=None):
        """Create database backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"database_backup_{timestamp}.sql"
        filepath = os.path.join(self.backup_dir, filename)
        
        try:
            # Get database settings
            db_settings = settings.DATABASES['default']
            
            if db_settings['ENGINE'] == 'django.db.backends.sqlite3':
                # SQLite backup
                db_path = db_settings['NAME']
                shutil.copy2(db_path, filepath.replace('.sql', '.sqlite3'))
                filepath = filepath.replace('.sql', '.sqlite3')
            
            elif db_settings['ENGINE'] == 'django.db.backends.mysql':
                # MySQL backup
                cmd = [
                    'mysqldump',
                    f"--host={db_settings['HOST']}",
                    f"--user={db_settings['USER']}",
                    f"--password={db_settings['PASSWORD']}",
                    db_settings['NAME']
                ]
                
                with open(filepath, 'w') as f:
                    subprocess.run(cmd, stdout=f, check=True)
            
            elif db_settings['ENGINE'] == 'django.db.backends.postgresql':
                # PostgreSQL backup
                env = os.environ.copy()
                env['PGPASSWORD'] = db_settings['PASSWORD']
                
                cmd = [
                    'pg_dump',
                    f"--host={db_settings['HOST']}",
                    f"--username={db_settings['USER']}",
                    f"--dbname={db_settings['NAME']}",
                    '--no-password'
                ]
                
                with open(filepath, 'w') as f:
                    subprocess.run(cmd, stdout=f, env=env, check=True)
            
            # Compress the backup
            compressed_filepath = f"{filepath}.gz"
            with open(filepath, 'rb') as f_in:
                with gzip.open(compressed_filepath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed file
            os.remove(filepath)
            filepath = compressed_filepath
            
            # Encrypt the backup
            encrypted_filepath = f"{filepath}.enc"
            checksum = self.secure_handler.encrypt_file(filepath, encrypted_filepath)
            
            # Remove unencrypted file
            os.remove(filepath)
            
            # Get file size
            file_size = os.path.getsize(encrypted_filepath)
            
            # Create backup record
            backup_record = BackupRecord.objects.create(
                backup_type='database',
                file_path=encrypted_filepath,
                file_size=file_size,
                created_by=user,
                checksum=checksum,
                is_encrypted=True,
                retention_date=datetime.now() + timedelta(days=30)
            )
            
            logger.info(f"Database backup created: {encrypted_filepath}")
            return backup_record
            
        except Exception as e:
            logger.error(f"Database backup failed: {str(e)}")
            raise
    
    def create_media_backup(self, user=None):
        """Create media files backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"media_backup_{timestamp}.tar.gz"
        filepath = os.path.join(self.backup_dir, filename)
        
        try:
            # Create tar.gz archive of media files
            media_root = settings.MEDIA_ROOT
            if os.path.exists(media_root):
                shutil.make_archive(
                    filepath.replace('.tar.gz', ''),
                    'gztar',
                    media_root
                )
                
                # Encrypt the backup
                encrypted_filepath = f"{filepath}.enc"
                checksum = self.secure_handler.encrypt_file(filepath, encrypted_filepath)
                
                # Remove unencrypted file
                os.remove(filepath)
                
                # Get file size
                file_size = os.path.getsize(encrypted_filepath)
                
                # Create backup record
                backup_record = BackupRecord.objects.create(
                    backup_type='media',
                    file_path=encrypted_filepath,
                    file_size=file_size,
                    created_by=user,
                    checksum=checksum,
                    is_encrypted=True,
                    retention_date=datetime.now() + timedelta(days=30)
                )
                
                logger.info(f"Media backup created: {encrypted_filepath}")
                return backup_record
            
        except Exception as e:
            logger.error(f"Media backup failed: {str(e)}")
            raise
    
    def create_logs_backup(self, user=None):
        """Create logs backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"logs_backup_{timestamp}.tar.gz"
        filepath = os.path.join(self.backup_dir, filename)
        
        try:
            # Create tar.gz archive of log files
            logs_dir = os.path.join(settings.BASE_DIR, 'logs')
            if os.path.exists(logs_dir):
                shutil.make_archive(
                    filepath.replace('.tar.gz', ''),
                    'gztar',
                    logs_dir
                )
                
                # Encrypt the backup
                encrypted_filepath = f"{filepath}.enc"
                checksum = self.secure_handler.encrypt_file(filepath, encrypted_filepath)
                
                # Remove unencrypted file
                os.remove(filepath)
                
                # Get file size
                file_size = os.path.getsize(encrypted_filepath)
                
                # Create backup record
                backup_record = BackupRecord.objects.create(
                    backup_type='logs',
                    file_path=encrypted_filepath,
                    file_size=file_size,
                    created_by=user,
                    checksum=checksum,
                    is_encrypted=True,
                    retention_date=datetime.now() + timedelta(days=90)
                )
                
                logger.info(f"Logs backup created: {encrypted_filepath}")
                return backup_record
            
        except Exception as e:
            logger.error(f"Logs backup failed: {str(e)}")
            raise
    
    def create_full_backup(self, user=None):
        """Create full system backup"""
        backups = []
        
        try:
            # Create individual backups
            db_backup = self.create_database_backup(user)
            backups.append(db_backup)
            
            media_backup = self.create_media_backup(user)
            if media_backup:
                backups.append(media_backup)
            
            logs_backup = self.create_logs_backup(user)
            if logs_backup:
                backups.append(logs_backup)
            
            # Create full backup record
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            total_size = sum(backup.file_size for backup in backups)
            
            full_backup = BackupRecord.objects.create(
                backup_type='full',
                file_path=f"full_backup_{timestamp}",
                file_size=total_size,
                created_by=user,
                checksum='',  # No single file for full backup
                is_encrypted=True,
                retention_date=datetime.now() + timedelta(days=90)
            )
            
            logger.info(f"Full backup created with {len(backups)} components")
            return full_backup
            
        except Exception as e:
            logger.error(f"Full backup failed: {str(e)}")
            raise
    
    def restore_database_backup(self, backup_record, user=None):
        """Restore database from backup"""
        try:
            # Decrypt backup file
            encrypted_path = backup_record.file_path
            decrypted_path = encrypted_path.replace('.enc', '')
            
            self.secure_handler.decrypt_file(encrypted_path, decrypted_path)
            
            # Decompress if needed
            if decrypted_path.endswith('.gz'):
                with gzip.open(decrypted_path, 'rb') as f_in:
                    with open(decrypted_path.replace('.gz', ''), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(decrypted_path)
                decrypted_path = decrypted_path.replace('.gz', '')
            
            # Restore based on database type
            db_settings = settings.DATABASES['default']
            
            if db_settings['ENGINE'] == 'django.db.backends.sqlite3':
                # SQLite restore
                db_path = db_settings['NAME']
                shutil.copy2(decrypted_path, db_path)
            
            elif db_settings['ENGINE'] == 'django.db.backends.mysql':
                # MySQL restore
                cmd = [
                    'mysql',
                    f"--host={db_settings['HOST']}",
                    f"--user={db_settings['USER']}",
                    f"--password={db_settings['PASSWORD']}",
                    db_settings['NAME']
                ]
                
                with open(decrypted_path, 'r') as f:
                    subprocess.run(cmd, stdin=f, check=True)
            
            elif db_settings['ENGINE'] == 'django.db.backends.postgresql':
                # PostgreSQL restore
                env = os.environ.copy()
                env['PGPASSWORD'] = db_settings['PASSWORD']
                
                cmd = [
                    'psql',
                    f"--host={db_settings['HOST']}",
                    f"--username={db_settings['USER']}",
                    f"--dbname={db_settings['NAME']}",
                    '--no-password'
                ]
                
                with open(decrypted_path, 'r') as f:
                    subprocess.run(cmd, stdin=f, env=env, check=True)
            
            # Clean up decrypted file
            os.remove(decrypted_path)
            
            logger.info(f"Database restored from backup: {backup_record.id}")
            
        except Exception as e:
            logger.error(f"Database restore failed: {str(e)}")
            raise
    
    def cleanup_old_backups(self):
        """Remove expired backups"""
        expired_backups = BackupRecord.objects.filter(
            retention_date__lt=datetime.now()
        )
        
        for backup in expired_backups:
            try:
                if os.path.exists(backup.file_path):
                    os.remove(backup.file_path)
                backup.delete()
                logger.info(f"Removed expired backup: {backup.id}")
            except Exception as e:
                logger.error(f"Failed to remove backup {backup.id}: {str(e)}")
    
    def get_backup_status(self):
        """Get backup system status"""
        recent_backups = BackupRecord.objects.filter(
            created_at__gte=datetime.now() - timedelta(days=7)
        ).order_by('-created_at')
        
        total_size = sum(backup.file_size for backup in recent_backups)
        
        return {
            'recent_backups_count': recent_backups.count(),
            'total_backup_size': total_size,
            'last_backup': recent_backups.first().created_at if recent_backups.exists() else None,
            'backup_directory': self.backup_dir,
            'available_space': shutil.disk_usage(self.backup_dir).free
        }