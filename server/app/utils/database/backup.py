import os
import gzip
import shutil
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import subprocess
import json

from app.utils.logging import logger

class DatabaseBackupManager:
    """Database backup and recovery management"""
    
    def __init__(self, database_url: str, backup_dir: str = "/backups"):
        self.database_url = database_url
        self.backup_dir = backup_dir
        self.db_type = self._detect_db_type()
        
        # Ensure backup directory exists
        os.makedirs(backup_dir, exist_ok=True)
    
    def _detect_db_type(self) -> str:
        """Detect database type from URL"""
        if 'postgresql' in self.database_url:
            return 'postgresql'
        elif 'mysql' in self.database_url:
            return 'mysql'
        elif 'sqlite' in self.database_url:
            return 'sqlite'
        else:
            raise ValueError(f"Unsupported database type: {self.database_url}")
    
    def create_backup(self, backup_name: Optional[str] = None, compress: bool = True) -> str:
        """Create database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"backup_{timestamp}"
        
        if compress:
            backup_file = os.path.join(self.backup_dir, f"{backup_name}.sql.gz")
        else:
            backup_file = os.path.join(self.backup_dir, f"{backup_name}.sql")
        
        try:
            if self.db_type == 'postgresql':
                self._backup_postgresql(backup_file, compress)
            elif self.db_type == 'mysql':
                self._backup_mysql(backup_file, compress)
            elif self.db_type == 'sqlite':
                self._backup_sqlite(backup_file, compress)
            
            # Create metadata file
            self._create_backup_metadata(backup_file)
            
            logger.info(f"Backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise
    
    def _backup_postgresql(self, backup_file: str, compress: bool):
        """Backup PostgreSQL database"""
        # Parse connection string
        import urllib.parse
        parsed = urllib.parse.urlparse(self.database_url)
        
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password
        
        cmd = [
            'pg_dump',
            '-h', parsed.hostname,
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path[1:],  # Remove leading slash
            '--no-password',
            '--verbose',
            '--format=plain',
            '--no-owner',
            '--no-privileges'
        ]
        
        if compress:
            # Use pipe to compress
            dump_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env)
            with gzip.open(backup_file, 'wb') as f:
                f.write(dump_proc.stdout.read())
            dump_proc.wait()
        else:
            cmd.extend(['-f', backup_file])
            subprocess.run(cmd, env=env, check=True)
    
    def _backup_mysql(self, backup_file: str, compress: bool):
        """Backup MySQL database"""
        # Parse connection string
        import urllib.parse
        parsed = urllib.parse.urlparse(self.database_url)
        
        cmd = [
            'mysqldump',
            f'--host={parsed.hostname}',
            f'--port={parsed.port or 3306}',
            f'--user={parsed.username}',
            f'--password={parsed.password}',
            '--single-transaction',
            '--routines',
            '--triggers',
            parsed.path[1:]  # Database name
        ]
        
        if compress:
            dump_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            with gzip.open(backup_file, 'wb') as f:
                f.write(dump_proc.stdout.read())
            dump_proc.wait()
        else:
            with open(backup_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
    
    def _backup_sqlite(self, backup_file: str, compress: bool):
        """Backup SQLite database"""
        db_file = self.database_url.replace('sqlite:///', '')
        
        if compress:
            with open(db_file, 'rb') as f_in:
                with gzip.open(backup_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy2(db_file, backup_file)
    
    def restore_backup(self, backup_file: str) -> bool:
        """Restore database from backup"""
        try:
            # Check if file is compressed
            is_compressed = backup_file.endswith('.gz')
            
            if self.db_type == 'postgresql':
                self._restore_postgresql(backup_file, is_compressed)
            elif self.db_type == 'mysql':
                self._restore_mysql(backup_file, is_compressed)
            elif self.db_type == 'sqlite':
                self._restore_sqlite(backup_file, is_compressed)
            
            logger.info(f"Backup restored: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def _restore_postgresql(self, backup_file: str, is_compressed: bool):
        """Restore PostgreSQL database"""
        import urllib.parse
        parsed = urllib.parse.urlparse(self.database_url)
        
        env = os.environ.copy()
        env['PGPASSWORD'] = parsed.password
        
        cmd = [
            'psql',
            '-h', parsed.hostname,
            '-p', str(parsed.port or 5432),
            '-U', parsed.username,
            '-d', parsed.path[1:],
            '--no-password'
        ]
        
        if is_compressed:
            with gzip.open(backup_file, 'rb') as f:
                subprocess.run(cmd, input=f.read(), env=env, check=True)
        else:
            cmd.extend(['-f', backup_file])
            subprocess.run(cmd, env=env, check=True)
    
    def _restore_mysql(self, backup_file: str, is_compressed: bool):
        """Restore MySQL database"""
        import urllib.parse
        parsed = urllib.parse.urlparse(self.database_url)
        
        cmd = [
            'mysql',
            f'--host={parsed.hostname}',
            f'--port={parsed.port or 3306}',
            f'--user={parsed.username}',
            f'--password={parsed.password}',
            parsed.path[1:]
        ]
        
        if is_compressed:
            with gzip.open(backup_file, 'rb') as f:
                subprocess.run(cmd, input=f.read(), check=True)
        else:
            with open(backup_file, 'r') as f:
                subprocess.run(cmd, stdin=f, check=True)
    
    def _restore_sqlite(self, backup_file: str, is_compressed: bool):
        """Restore SQLite database"""
        db_file = self.database_url.replace('sqlite:///', '')
        
        # Backup current database
        shutil.copy2(db_file, f"{db_file}.bak")
        
        try:
            if is_compressed:
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(db_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_file, db_file)
        except Exception as e:
            # Restore from backup on failure
            shutil.move(f"{db_file}.bak", db_file)
            raise
    
    def _create_backup_metadata(self, backup_file: str):
        """Create metadata file for backup"""
        metadata = {
            'backup_file': os.path.basename(backup_file),
            'created_at': datetime.now().isoformat(),
            'database_type': self.db_type,
            'database_url': self._sanitize_db_url(),
            'file_size': os.path.getsize(backup_file),
            'compressed': backup_file.endswith('.gz')
        }
        
        metadata_file = f"{backup_file}.meta"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _sanitize_db_url(self) -> str:
        """Remove password from database URL"""
        import urllib.parse
        parsed = urllib.parse.urlparse(self.database_url)
        
        # Replace password with asterisks
        if parsed.password:
            sanitized = self.database_url.replace(parsed.password, '****')
        else:
            sanitized = self.database_url
        
        return sanitized
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.sql') or filename.endswith('.sql.gz'):
                file_path = os.path.join(self.backup_dir, filename)
                meta_path = f"{file_path}.meta"
                
                backup_info = {
                    'filename': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'created_at': datetime.fromtimestamp(os.path.getctime(file_path))
                }
                
                # Load metadata if available
                if os.path.exists(meta_path):
                    with open(meta_path, 'r') as f:
                        metadata = json.load(f)
                        backup_info.update(metadata)
                
                backups.append(backup_info)
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups
    
    def cleanup_old_backups(self, retention_days: int = 30):
        """Remove backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        removed_count = 0
        
        for backup in self.list_backups():
            created_at = backup['created_at']
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            
            if created_at < cutoff_date:
                try:
                    os.remove(backup['path'])
                    meta_path = f"{backup['path']}.meta"
                    if os.path.exists(meta_path):
                        os.remove(meta_path)
                    
                    logger.info(f"Removed old backup: {backup['filename']}")
                    removed_count += 1
                except Exception as e:
                    logger.error(f"Error removing backup {backup['filename']}: {e}")
        
        logger.info(f"Cleaned up {removed_count} old backups")
        return removed_count
    
    def verify_backup(self, backup_file: str) -> bool:
        """Verify backup integrity"""
        try:
            if backup_file.endswith('.gz'):
                # Test gzip integrity
                with gzip.open(backup_file, 'rb') as f:
                    f.read(1024)  # Read first chunk to verify
            else:
                # Check file exists and is readable
                with open(backup_file, 'r') as f:
                    f.read(1024)
            
            # Check for metadata file
            meta_path = f"{backup_file}.meta"
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    json.load(f)
            
            return True
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            return False
    
    def schedule_backup(self, schedule: str = "0 2 * * *"):
        """Create cron job for scheduled backups"""
        cron_command = f"cd {os.path.dirname(__file__)} && python -m backup create"
        
        # Add to crontab
        try:
            # Get current crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            current_crontab = result.stdout
            
            # Add new job if not exists
            if cron_command not in current_crontab:
                new_crontab = current_crontab + f"\n{schedule} {cron_command}\n"
                
                # Update crontab
                process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
                process.communicate(new_crontab.encode())
                
                logger.info(f"Scheduled backup: {schedule}")
        except Exception as e:
            logger.error(f"Failed to schedule backup: {e}")


if __name__ == "__main__":
    import sys
    
    # Example CLI usage
    if len(sys.argv) < 2:
        print("Usage: python backup.py [create|restore|list|cleanup|verify] [options]")
        sys.exit(1)
    
    manager = DatabaseBackupManager('postgresql://user:pass@localhost/bdc')
    
    command = sys.argv[1]
    
    if command == 'create':
        backup_file = manager.create_backup()
        print(f"Backup created: {backup_file}")
    
    elif command == 'restore' and len(sys.argv) > 2:
        backup_file = sys.argv[2]
        if manager.restore_backup(backup_file):
            print(f"Backup restored: {backup_file}")
        else:
            print("Restore failed")
    
    elif command == 'list':
        backups = manager.list_backups()
        for backup in backups:
            print(f"{backup['filename']} - {backup['created_at']} - {backup['size']} bytes")
    
    elif command == 'cleanup':
        retention_days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        removed = manager.cleanup_old_backups(retention_days)
        print(f"Removed {removed} old backups")
    
    elif command == 'verify' and len(sys.argv) > 2:
        backup_file = sys.argv[2]
        if manager.verify_backup(backup_file):
            print("Backup is valid")
        else:
            print("Backup is corrupted or invalid") 