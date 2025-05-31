"""Comprehensive tests for backup manager."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call, mock_open
from datetime import datetime, timezone, timedelta
import os
import json
import gzip
import shutil


class TestBackupManager:
    """Test cases for backup manager."""
    
    @pytest.fixture
    def backup_config(self):
        """Create backup configuration."""
        return {
            'backup_dir': '/tmp/backups',
            'retention_days': 30,
            'compression': True,
            'encryption': False,
            'storage_backends': ['local', 's3'],
            'schedule': {
                'daily': True,
                'weekly': True,
                'monthly': True
            }
        }
    
    @pytest.fixture
    def mock_db_config(self):
        """Create mock database configuration."""
        return {
            'host': 'localhost',
            'port': 5432,
            'database': 'bdc',
            'username': 'postgres',
            'password': 'password'
        }
    
    def test_backup_manager_init(self, backup_config):
        """Test backup manager initialization."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        assert manager.config == backup_config
        assert manager.backup_dir == '/tmp/backups'
        assert manager.retention_days == 30
    
    @patch('os.makedirs')
    def test_create_backup_directory(self, mock_makedirs, backup_config):
        """Test backup directory creation."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        manager.create_backup_directory()
        
        mock_makedirs.assert_called_with('/tmp/backups', exist_ok=True)
    
    @patch('subprocess.run')
    def test_backup_database(self, mock_subprocess, backup_config, mock_db_config):
        """Test database backup."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Mock successful backup
        mock_subprocess.return_value = Mock(returncode=0)
        
        backup_file = manager.backup_database(mock_db_config)
        
        assert backup_file is not None
        assert 'bdc_backup' in backup_file
        assert '.sql' in backup_file
        mock_subprocess.assert_called_once()
    
    @patch('subprocess.run')
    def test_backup_database_failure(self, mock_subprocess, backup_config, mock_db_config):
        """Test database backup failure."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Mock failed backup
        mock_subprocess.return_value = Mock(returncode=1, stderr='Error')
        
        with pytest.raises(Exception):
            manager.backup_database(mock_db_config)
    
    def test_compress_backup(self, backup_config):
        """Test backup compression."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Create mock file
        test_content = b'Test backup content'
        source_file = '/tmp/test_backup.sql'
        
        with patch('builtins.open', mock_open(read_data=test_content)):
            with patch('gzip.open', mock_open()) as mock_gzip:
                compressed_file = manager.compress_backup(source_file)
                
                assert compressed_file.endswith('.gz')
                mock_gzip.assert_called_once()
    
    def test_encrypt_backup(self, backup_config):
        """Test backup encryption."""
        from app.utils.backup_manager import BackupManager
        
        backup_config['encryption'] = True
        manager = BackupManager(backup_config)
        
        with patch('app.utils.backup_manager.encrypt_file') as mock_encrypt:
            mock_encrypt.return_value = '/tmp/backup.enc'
            
            encrypted_file = manager.encrypt_backup('/tmp/backup.sql')
            
            assert encrypted_file.endswith('.enc')
            mock_encrypt.assert_called_once()
    
    @patch('shutil.copy2')
    def test_store_backup_local(self, mock_copy, backup_config):
        """Test storing backup locally."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        source_file = '/tmp/backup.sql.gz'
        destination = manager.store_backup_local(source_file)
        
        assert destination is not None
        mock_copy.assert_called_once()
    
    @patch('boto3.client')
    def test_store_backup_s3(self, mock_boto3, backup_config):
        """Test storing backup to S3."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Mock S3 client
        mock_s3 = Mock()
        mock_boto3.return_value = mock_s3
        
        source_file = '/tmp/backup.sql.gz'
        s3_key = manager.store_backup_s3(source_file, 'my-bucket')
        
        assert s3_key is not None
        mock_s3.upload_file.assert_called_once()
    
    @patch('os.listdir')
    @patch('os.path.getmtime')
    @patch('os.remove')
    def test_cleanup_old_backups(self, mock_remove, mock_getmtime, mock_listdir, backup_config):
        """Test cleaning up old backups."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Mock old backup files
        mock_listdir.return_value = [
            'backup_2023_01_01.sql.gz',
            'backup_2023_12_01.sql.gz'
        ]
        
        # Set modification times
        old_time = (datetime.now() - timedelta(days=40)).timestamp()
        recent_time = (datetime.now() - timedelta(days=5)).timestamp()
        mock_getmtime.side_effect = [old_time, recent_time]
        
        manager.cleanup_old_backups()
        
        # Should remove only the old backup
        mock_remove.assert_called_once()
    
    def test_restore_database(self, backup_config, mock_db_config):
        """Test database restoration."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0)
            
            manager.restore_database('/tmp/backup.sql', mock_db_config)
            
            mock_subprocess.assert_called_once()
    
    def test_verify_backup(self, backup_config):
        """Test backup verification."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        with patch('os.path.exists', return_value=True):
            with patch('os.path.getsize', return_value=1024000):
                is_valid = manager.verify_backup('/tmp/backup.sql.gz')
                
                assert is_valid is True
    
    def test_get_backup_list(self, backup_config):
        """Test getting backup list."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = [
                'backup_2024_01_01.sql.gz',
                'backup_2024_01_02.sql.gz'
            ]
            
            with patch('os.path.getsize', return_value=1024000):
                with patch('os.path.getmtime', return_value=datetime.now().timestamp()):
                    backups = manager.get_backup_list()
                    
                    assert len(backups) == 2
                    assert all('filename' in b for b in backups)
                    assert all('size' in b for b in backups)
    
    def test_backup_metadata(self, backup_config):
        """Test backup metadata generation."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        metadata = manager.create_backup_metadata(
            filename='backup.sql.gz',
            size=1024000,
            checksum='abc123'
        )
        
        assert metadata['filename'] == 'backup.sql.gz'
        assert metadata['size'] == 1024000
        assert metadata['checksum'] == 'abc123'
        assert 'created_at' in metadata
        assert 'backup_type' in metadata
    
    def test_incremental_backup(self, backup_config, mock_db_config):
        """Test incremental backup."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=0)
            
            # Mock last backup info
            with patch.object(manager, 'get_last_backup_info') as mock_last:
                mock_last.return_value = {
                    'timestamp': datetime.now() - timedelta(days=1),
                    'lsn': '1234567890'
                }
                
                backup_file = manager.incremental_backup(mock_db_config)
                
                assert backup_file is not None
                assert 'incremental' in backup_file
    
    def test_backup_rotation(self, backup_config):
        """Test backup rotation policy."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        with patch('os.listdir') as mock_listdir:
            # Mock many backup files
            mock_listdir.return_value = [
                f'backup_daily_{i:02d}.sql.gz' for i in range(40)
            ]
            
            with patch('os.remove') as mock_remove:
                manager.apply_rotation_policy()
                
                # Should keep only recent backups according to policy
                assert mock_remove.call_count > 0
    
    def test_backup_scheduling(self, backup_config):
        """Test backup scheduling."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Test if backup is due
        assert manager.is_backup_due('daily') is True
        
        # Test after recent backup
        with patch.object(manager, 'get_last_backup_time') as mock_last:
            mock_last.return_value = datetime.now() - timedelta(hours=1)
            assert manager.is_backup_due('daily') is False
    
    @patch('smtplib.SMTP')
    def test_backup_notifications(self, mock_smtp, backup_config):
        """Test backup notifications."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Test success notification
        manager.send_backup_notification(
            status='success',
            backup_file='backup.sql.gz',
            size=1024000
        )
        
        mock_smtp.assert_called_once()
    
    def test_backup_integrity_check(self, backup_config):
        """Test backup integrity check."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        with patch('subprocess.run') as mock_subprocess:
            # Mock successful integrity check
            mock_subprocess.return_value = Mock(
                returncode=0,
                stdout='Backup is valid'
            )
            
            is_valid = manager.check_backup_integrity('/tmp/backup.sql')
            
            assert is_valid is True
    
    def test_parallel_backup(self, backup_config):
        """Test parallel backup of multiple databases."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        databases = ['db1', 'db2', 'db3']
        
        with patch.object(manager, 'backup_database') as mock_backup:
            mock_backup.return_value = 'backup.sql'
            
            with patch('concurrent.futures.ThreadPoolExecutor'):
                results = manager.parallel_backup(databases)
                
                assert len(results) == 3
    
    def test_backup_to_multiple_destinations(self, backup_config):
        """Test backing up to multiple destinations."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        backup_file = '/tmp/backup.sql.gz'
        
        with patch.object(manager, 'store_backup_local') as mock_local:
            with patch.object(manager, 'store_backup_s3') as mock_s3:
                mock_local.return_value = '/backups/backup.sql.gz'
                mock_s3.return_value = 's3://bucket/backup.sql.gz'
                
                destinations = manager.store_backup_all(backup_file)
                
                assert len(destinations) == 2
                assert 'local' in destinations
                assert 's3' in destinations
    
    def test_backup_monitoring(self, backup_config):
        """Test backup monitoring and alerting."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        # Test monitoring check
        with patch.object(manager, 'get_last_backup_time') as mock_last:
            # Backup is overdue
            mock_last.return_value = datetime.now() - timedelta(days=2)
            
            alerts = manager.check_backup_health()
            
            assert len(alerts) > 0
            assert any('overdue' in alert['message'] for alert in alerts)
    
    def test_disaster_recovery_plan(self, backup_config):
        """Test disaster recovery plan execution."""
        from app.utils.backup_manager import BackupManager
        
        manager = BackupManager(backup_config)
        
        with patch.object(manager, 'get_latest_backup') as mock_latest:
            with patch.object(manager, 'restore_database') as mock_restore:
                mock_latest.return_value = '/backups/latest.sql'
                
                manager.execute_disaster_recovery()
                
                mock_restore.assert_called_once()
    
    def test_backup_api_endpoints(self, backup_config):
        """Test backup API endpoints."""
        from app.utils.backup_manager import BackupManager, BackupAPI
        
        api = BackupAPI(BackupManager(backup_config))
        
        # Test list backups endpoint
        with patch.object(api.manager, 'get_backup_list') as mock_list:
            mock_list.return_value = [
                {'filename': 'backup1.sql.gz', 'size': 1024000}
            ]
            
            backups = api.list_backups()
            assert len(backups) == 1
        
        # Test create backup endpoint
        with patch.object(api.manager, 'backup_database') as mock_backup:
            mock_backup.return_value = 'backup.sql.gz'
            
            result = api.create_backup()
            assert 'backup_file' in result