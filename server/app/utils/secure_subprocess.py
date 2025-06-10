"""Secure subprocess utilities for safe command execution."""

import subprocess
import shlex
import logging
import os
import signal
from typing import List, Dict, Optional, Union, Tuple
from pathlib import Path
import tempfile
import time

logger = logging.getLogger(__name__)


class SecureSubprocessError(Exception):
    """Custom exception for subprocess security violations."""
    pass


class SecureSubprocess:
    """Secure wrapper for subprocess operations with safety constraints."""
    
    # Allowed executables with their security constraints
    ALLOWED_EXECUTABLES = {
        'pg_dump': {
            'allowed_args': ['-h', '--host', '-p', '--port', '-U', '--username', 
                           '-d', '--dbname', '--no-password', '--verbose', 
                           '--format', '--no-owner', '--no-privileges', '-f', '--file'],
            'forbidden_args': ['--command', '-c', '|', '&', ';', '`', '$'],
            'timeout': 3600,  # 1 hour
            'max_output_size': 50 * 1024 * 1024  # 50MB
        },
        'psql': {
            'allowed_args': ['-h', '--host', '-p', '--port', '-U', '--username',
                           '-d', '--dbname', '--no-password', '-f', '--file'],
            'forbidden_args': ['--command', '-c', '|', '&', ';', '`', '$'],
            'timeout': 3600,
            'max_output_size': 10 * 1024 * 1024  # 10MB
        },
        'mysqldump': {
            'allowed_args': ['--host', '--port', '--user', '--password',
                           '--single-transaction', '--routines', '--triggers'],
            'forbidden_args': ['--execute', '-e', '|', '&', ';', '`', '$'],
            'timeout': 3600,
            'max_output_size': 50 * 1024 * 1024
        },
        'mysql': {
            'allowed_args': ['--host', '--port', '--user', '--password'],
            'forbidden_args': ['--execute', '-e', '|', '&', ';', '`', '$'],
            'timeout': 3600,
            'max_output_size': 10 * 1024 * 1024
        },
        'clamdscan': {
            'allowed_args': ['--no-summary', '--fdpass', '--stream'],
            'forbidden_args': ['|', '&', ';', '`', '$', '--config'],
            'timeout': 600,  # 10 minutes
            'max_output_size': 1024 * 1024  # 1MB
        },
        'clamscan': {
            'allowed_args': ['--no-summary', '--infected', '--bell'],
            'forbidden_args': ['|', '&', ';', '`', '$', '--config'],
            'timeout': 600,
            'max_output_size': 1024 * 1024
        },
        'tar': {
            'allowed_args': ['-czf', '-xzf', '-tzf', '-C', '--exclude'],
            'forbidden_args': ['|', '&', ';', '`', '$', '--to-command'],
            'timeout': 1800,  # 30 minutes
            'max_output_size': 10 * 1024 * 1024
        },
        'gzip': {
            'allowed_args': ['-c', '-d', '-f', '-k', '-v'],
            'forbidden_args': ['|', '&', ';', '`', '$'],
            'timeout': 300,
            'max_output_size': 100 * 1024 * 1024  # 100MB
        },
        'gunzip': {
            'allowed_args': ['-c', '-f', '-k', '-v'],
            'forbidden_args': ['|', '&', ';', '`', '$'],
            'timeout': 300,
            'max_output_size': 100 * 1024 * 1024
        }
    }
    
    @classmethod
    def run_secure(cls, command: Union[str, List[str]], 
                   input_data: Optional[bytes] = None,
                   env: Optional[Dict[str, str]] = None,
                   cwd: Optional[str] = None,
                   timeout: Optional[int] = None,
                   check: bool = True) -> subprocess.CompletedProcess:
        """
        Execute a command securely with validation and constraints.
        
        Args:
            command: Command to execute (string or list)
            input_data: Input data to send to process
            env: Environment variables
            cwd: Working directory
            timeout: Timeout in seconds
            check: Raise exception on non-zero exit code
            
        Returns:
            CompletedProcess with stdout, stderr, and returncode
            
        Raises:
            SecureSubprocessError: If command is not allowed or violates security
        """
        # Parse command
        if isinstance(command, str):
            cmd_list = shlex.split(command)
        else:
            cmd_list = command.copy()
        
        if not cmd_list:
            raise SecureSubprocessError("Empty command not allowed")
        
        executable = cls._get_executable_name(cmd_list[0])
        
        # Validate executable
        if executable not in cls.ALLOWED_EXECUTABLES:
            raise SecureSubprocessError(f"Executable '{executable}' is not allowed")
        
        config = cls.ALLOWED_EXECUTABLES[executable]
        
        # Validate arguments
        cls._validate_arguments(cmd_list[1:], config)
        
        # Validate paths
        cls._validate_paths(cmd_list)
        
        # Set security constraints
        if timeout is None:
            timeout = config['timeout']
        
        # Prepare secure environment
        secure_env = cls._prepare_secure_environment(env)
        
        # Validate working directory
        if cwd:
            cls._validate_path(cwd)
        
        try:
            logger.info(f"Executing secure command: {executable} with {len(cmd_list)-1} arguments")
            
            # Execute with security constraints
            with tempfile.TemporaryDirectory() as temp_dir:
                result = subprocess.run(
                    cmd_list,
                    input=input_data,
                    capture_output=True,
                    env=secure_env,
                    cwd=cwd,
                    timeout=timeout,
                    check=False,  # We'll handle the check ourselves
                    preexec_fn=cls._security_preexec if os.name != 'nt' else None
                )
                
                # Validate output size
                if len(result.stdout) > config['max_output_size']:
                    raise SecureSubprocessError(
                        f"Command output exceeds maximum size ({config['max_output_size']} bytes)"
                    )
                
                if len(result.stderr) > config['max_output_size']:
                    raise SecureSubprocessError(
                        f"Command error output exceeds maximum size ({config['max_output_size']} bytes)"
                    )
                
                # Log execution details
                logger.info(f"Command completed with exit code: {result.returncode}")
                if result.stderr:
                    logger.warning(f"Command stderr: {result.stderr.decode('utf-8', errors='ignore')[:500]}")
                
                # Check exit code if requested
                if check and result.returncode != 0:
                    raise subprocess.CalledProcessError(
                        result.returncode, cmd_list, result.stdout, result.stderr
                    )
                
                return result
                
        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timeout after {timeout} seconds: {executable}")
            raise SecureSubprocessError(f"Command timeout: {executable}")
        
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with exit code {e.returncode}: {executable}")
            if check:
                raise
            return subprocess.CompletedProcess(
                e.cmd, e.returncode, e.stdout, e.stderr
            )
        
        except Exception as e:
            logger.error(f"Unexpected error executing command: {e}")
            raise SecureSubprocessError(f"Command execution failed: {str(e)}")
    
    @classmethod
    def _get_executable_name(cls, command: str) -> str:
        """Extract executable name from command path."""
        return Path(command).name
    
    @classmethod
    def _validate_arguments(cls, args: List[str], config: Dict) -> None:
        """Validate command arguments against security policy."""
        allowed_args = config.get('allowed_args', [])
        forbidden_args = config.get('forbidden_args', [])
        
        for arg in args:
            # Check forbidden patterns
            for forbidden in forbidden_args:
                if forbidden in arg:
                    raise SecureSubprocessError(f"Forbidden pattern '{forbidden}' in argument: {arg}")
            
            # For flags, check if they're in allowed list
            if arg.startswith('-') and allowed_args:
                arg_name = arg.split('=')[0]  # Handle --arg=value format
                if arg_name not in allowed_args:
                    # Allow short flag combinations like -czf
                    if not (arg.startswith('-') and not arg.startswith('--') and 
                           len(arg) > 2 and all(f'-{c}' in allowed_args for c in arg[1:])):
                        raise SecureSubprocessError(f"Argument '{arg_name}' is not allowed")
    
    @classmethod
    def _validate_paths(cls, cmd_list: List[str]) -> None:
        """Validate file paths in command arguments."""
        for arg in cmd_list:
            if '/' in arg and not arg.startswith('-'):
                cls._validate_path(arg)
    
    @classmethod
    def _validate_path(cls, path: str) -> None:
        """Validate a single path for security."""
        # Resolve path to catch directory traversal attempts
        try:
            resolved_path = Path(path).resolve()
        except (OSError, ValueError) as e:
            raise SecureSubprocessError(f"Invalid path: {path}")
        
        # Check for dangerous patterns
        dangerous_patterns = ['..', '~', '$', '`', '|', '&', ';']
        for pattern in dangerous_patterns:
            if pattern in str(resolved_path):
                raise SecureSubprocessError(f"Dangerous pattern '{pattern}' in path: {path}")
        
        # Ensure path is within allowed directories
        allowed_dirs = [
            '/tmp',
            '/var/tmp',
            '/opt/bdc',
            os.getcwd(),
            tempfile.gettempdir()
        ]
        
        # Add upload directories if configured
        from flask import current_app
        if current_app:
            upload_folder = current_app.config.get('UPLOAD_FOLDER')
            if upload_folder:
                allowed_dirs.append(os.path.abspath(upload_folder))
            
            quarantine_path = current_app.config.get('QUARANTINE_PATH')
            if quarantine_path:
                allowed_dirs.append(os.path.abspath(quarantine_path))
        
        # Check if path is within allowed directories
        path_allowed = False
        for allowed_dir in allowed_dirs:
            try:
                resolved_allowed = Path(allowed_dir).resolve()
                if resolved_path.is_relative_to(resolved_allowed):
                    path_allowed = True
                    break
            except (OSError, ValueError):
                continue
        
        if not path_allowed:
            raise SecureSubprocessError(f"Path outside allowed directories: {path}")
    
    @classmethod
    def _prepare_secure_environment(cls, env: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Prepare a secure environment for subprocess execution."""
        # Start with minimal environment
        secure_env = {
            'PATH': '/usr/local/bin:/usr/bin:/bin',
            'LANG': 'C.UTF-8',
            'LC_ALL': 'C.UTF-8'
        }
        
        # Add specific safe variables if provided
        if env:
            safe_vars = ['PGPASSWORD', 'MYSQL_PWD', 'TZ', 'HOME']
            for var in safe_vars:
                if var in env:
                    secure_env[var] = env[var]
        
        return secure_env
    
    @staticmethod
    def _security_preexec() -> None:
        """Security function to run before exec on Unix systems."""
        # Set process group to enable killing child processes
        os.setpgrp()
        
        # Set resource limits if available
        try:
            import resource
            # Limit memory usage (1GB)
            resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024 * 1024, 1024 * 1024 * 1024))
            # Limit CPU time (1 hour)
            resource.setrlimit(resource.RLIMIT_CPU, (3600, 3600))
            # Limit number of processes
            resource.setrlimit(resource.RLIMIT_NPROC, (100, 100))
        except ImportError:
            pass  # resource module not available on all systems


class DatabaseBackupSecure:
    """Secure database backup operations using SecureSubprocess."""
    
    @staticmethod
    def create_postgres_backup(database_url: str, backup_path: str) -> bool:
        """Create PostgreSQL backup securely."""
        try:
            # Parse database URL safely
            import urllib.parse
            parsed = urllib.parse.urlparse(database_url)
            
            # Validate inputs
            if not parsed.hostname or not parsed.username or not parsed.path:
                raise ValueError("Invalid database URL format")
            
            # Prepare secure environment
            env = {
                'PGPASSWORD': parsed.password or ''
            }
            
            # Build command securely
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
                '--no-privileges',
                '-f', backup_path
            ]
            
            # Execute securely
            result = SecureSubprocess.run_secure(
                cmd, 
                env=env, 
                timeout=3600,
                check=True
            )
            
            logger.info(f"PostgreSQL backup completed: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL backup failed: {e}")
            return False
    
    @staticmethod
    def restore_postgres_backup(database_url: str, backup_path: str) -> bool:
        """Restore PostgreSQL backup securely."""
        try:
            # Parse database URL safely
            import urllib.parse
            parsed = urllib.parse.urlparse(database_url)
            
            # Validate backup file
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Prepare secure environment
            env = {
                'PGPASSWORD': parsed.password or ''
            }
            
            # Build command securely
            cmd = [
                'psql',
                '-h', parsed.hostname,
                '-p', str(parsed.port or 5432),
                '-U', parsed.username,
                '-d', parsed.path[1:],
                '--no-password',
                '-f', backup_path
            ]
            
            # Execute securely
            result = SecureSubprocess.run_secure(
                cmd,
                env=env,
                timeout=3600,
                check=True
            )
            
            logger.info(f"PostgreSQL restore completed: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"PostgreSQL restore failed: {e}")
            return False


class VirusScannerSecure:
    """Secure virus scanning operations."""
    
    @staticmethod
    def scan_file_clamav(file_path: str) -> Dict:
        """Scan file with ClamAV securely."""
        try:
            # Try clamdscan first (daemon version)
            result = SecureSubprocess.run_secure(
                ['clamdscan', '--no-summary', file_path],
                timeout=300,
                check=False
            )
            
            if result.returncode == 0:
                return {
                    'scanner': 'ClamAV',
                    'infected': False,
                    'status': 'clean',
                    'output': result.stdout.decode('utf-8', errors='ignore')
                }
            elif result.returncode == 1:
                # Virus found
                output = result.stdout.decode('utf-8', errors='ignore')
                threats = VirusScannerSecure._parse_clamav_output(output)
                return {
                    'scanner': 'ClamAV',
                    'infected': True,
                    'status': 'infected',
                    'threats': threats,
                    'output': output
                }
            else:
                # Error occurred, try clamscan
                return VirusScannerSecure._scan_with_clamscan(file_path)
                
        except SecureSubprocessError:
            # Fallback to clamscan
            return VirusScannerSecure._scan_with_clamscan(file_path)
    
    @staticmethod
    def _scan_with_clamscan(file_path: str) -> Dict:
        """Fallback scanning with clamscan."""
        try:
            result = SecureSubprocess.run_secure(
                ['clamscan', '--no-summary', file_path],
                timeout=300,
                check=False
            )
            
            if result.returncode == 0:
                return {
                    'scanner': 'ClamAV',
                    'infected': False,
                    'status': 'clean',
                    'output': result.stdout.decode('utf-8', errors='ignore')
                }
            elif result.returncode == 1:
                output = result.stdout.decode('utf-8', errors='ignore')
                threats = VirusScannerSecure._parse_clamav_output(output)
                return {
                    'scanner': 'ClamAV',
                    'infected': True,
                    'status': 'infected',
                    'threats': threats,
                    'output': output
                }
            else:
                raise Exception(f"ClamAV scan failed: {result.stderr.decode('utf-8', errors='ignore')}")
                
        except Exception as e:
            logger.error(f"ClamAV scan error: {e}")
            raise
    
    @staticmethod
    def _parse_clamav_output(output: str) -> List[str]:
        """Parse ClamAV output for threat names."""
        threats = []
        for line in output.split('\n'):
            if 'FOUND' in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    threat = parts[1].strip().replace(' FOUND', '')
                    threats.append(threat)
        return threats


# Utility functions for secure operations
def create_secure_temp_file(suffix: str = '', prefix: str = 'bdc_') -> str:
    """Create a secure temporary file."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)  # Close file descriptor, but keep the file
    os.chmod(path, 0o600)  # Read/write for owner only
    return path


def create_secure_temp_directory(prefix: str = 'bdc_') -> str:
    """Create a secure temporary directory."""
    path = tempfile.mkdtemp(prefix=prefix)
    os.chmod(path, 0o700)  # Read/write/execute for owner only
    return path


def secure_file_operation(func):
    """Decorator for secure file operations with cleanup."""
    def wrapper(*args, **kwargs):
        temp_files = []
        temp_dirs = []
        
        try:
            # Replace temp file creation in kwargs
            if 'temp_file' in kwargs and kwargs['temp_file'] is True:
                temp_file = create_secure_temp_file()
                kwargs['temp_file'] = temp_file
                temp_files.append(temp_file)
            
            if 'temp_dir' in kwargs and kwargs['temp_dir'] is True:
                temp_dir = create_secure_temp_directory()
                kwargs['temp_dir'] = temp_dir
                temp_dirs.append(temp_dir)
            
            return func(*args, **kwargs)
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {temp_file}: {e}")
            
            # Clean up temporary directories
            for temp_dir in temp_dirs:
                try:
                    if os.path.exists(temp_dir):
                        import shutil
                        shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp dir {temp_dir}: {e}")
    
    return wrapper