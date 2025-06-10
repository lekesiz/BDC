"""Enhanced virus scanner service with multiple scanning engines support."""

import os
import hashlib
import magic
import logging
import tempfile
import shutil
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from pathlib import Path
from app.utils.secure_subprocess import SecureSubprocess, VirusScannerSecure
import json
from flask import current_app
from app.extensions import db
from app.models.virus_scan_log import VirusScanLog
import requests
from sqlalchemy import case

logger = logging.getLogger(__name__)


class VirusScannerService:
    """Service for scanning files for viruses and malware."""
    
    def __init__(self):
        self.config = {
            'MAX_FILE_SIZE': current_app.config.get('MAX_FILE_SIZE', 50 * 1024 * 1024),  # 50MB
            'SCAN_TIMEOUT': current_app.config.get('VIRUS_SCAN_TIMEOUT', 300),  # 5 minutes
            'QUARANTINE_PATH': current_app.config.get('QUARANTINE_PATH', '/tmp/quarantine'),
            'ENABLE_CLAMAV': current_app.config.get('ENABLE_CLAMAV', True),
            'ENABLE_VIRUSTOTAL': current_app.config.get('ENABLE_VIRUSTOTAL', False),
            'VIRUSTOTAL_API_KEY': current_app.config.get('VIRUSTOTAL_API_KEY'),
            'SCAN_ARCHIVES': current_app.config.get('SCAN_ARCHIVES', True),
            'BLOCKED_EXTENSIONS': ['.exe', '.bat', '.cmd', '.scr', '.vbs', '.js', '.jar', '.com'],
            'HIGH_RISK_EXTENSIONS': ['.doc', '.docx', '.xls', '.xlsx', '.pdf', '.zip', '.rar']
        }
        
        # Initialize scanners
        self.scanners = []
        if self.config['ENABLE_CLAMAV']:
            self.scanners.append(ClamAVScanner())
        if self.config['ENABLE_VIRUSTOTAL'] and self.config['VIRUSTOTAL_API_KEY']:
            self.scanners.append(VirusTotalScanner(self.config['VIRUSTOTAL_API_KEY']))
        
        # Ensure quarantine directory exists
        os.makedirs(self.config['QUARANTINE_PATH'], exist_ok=True)
    
    def scan_file(self, file_path: str, user_id: Optional[int] = None) -> Dict:
        """
        Scan a file for viruses and malware.
        
        Args:
            file_path: Path to the file to scan
            user_id: ID of the user who uploaded the file
            
        Returns:
            Dictionary with scan results
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate file
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_info = self._get_file_info(file_path)
            
            # Check file size
            if file_info['size'] > self.config['MAX_FILE_SIZE']:
                return {
                    'status': 'error',
                    'message': f"File too large for scanning (max {self.config['MAX_FILE_SIZE']} bytes)",
                    'file_info': file_info
                }
            
            # Check blocked extensions
            if file_info['extension'] in self.config['BLOCKED_EXTENSIONS']:
                self._quarantine_file(file_path, "Blocked file extension")
                return {
                    'status': 'blocked',
                    'message': f"File type {file_info['extension']} is blocked",
                    'file_info': file_info,
                    'action': 'quarantined'
                }
            
            # Perform virus scan
            scan_results = []
            is_infected = False
            threats_found = []
            
            for scanner in self.scanners:
                try:
                    result = scanner.scan(file_path)
                    scan_results.append(result)
                    
                    if result['infected']:
                        is_infected = True
                        threats_found.extend(result.get('threats', []))
                
                except Exception as e:
                    logger.error(f"Scanner {scanner.__class__.__name__} failed: {str(e)}")
                    scan_results.append({
                        'scanner': scanner.__class__.__name__,
                        'status': 'error',
                        'error': str(e)
                    })
            
            # Handle infected files
            if is_infected:
                quarantine_path = self._quarantine_file(file_path, f"Threats detected: {threats_found}")
                scan_result = {
                    'status': 'infected',
                    'infected': True,
                    'threats': threats_found,
                    'action': 'quarantined',
                    'quarantine_path': quarantine_path,
                    'scan_results': scan_results,
                    'file_info': file_info
                }
            else:
                scan_result = {
                    'status': 'clean',
                    'infected': False,
                    'scan_results': scan_results,
                    'file_info': file_info
                }
            
            # Log scan result
            self._log_scan_result(file_path, scan_result, user_id, start_time)
            
            return scan_result
            
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'file_info': self._get_file_info(file_path) if os.path.exists(file_path) else {}
            }
    
    def _get_file_info(self, file_path: str) -> Dict:
        """Get file information."""
        stat = os.stat(file_path)
        path = Path(file_path)
        
        # Detect MIME type
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(file_path)
        
        # Calculate hash
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        
        return {
            'name': path.name,
            'path': str(path),
            'size': stat.st_size,
            'extension': path.suffix.lower(),
            'mime_type': mime_type,
            'sha256': sha256_hash.hexdigest(),
            'created_at': datetime.fromtimestamp(stat.st_ctime),
            'modified_at': datetime.fromtimestamp(stat.st_mtime)
        }
    
    def _quarantine_file(self, file_path: str, reason: str) -> str:
        """Move file to quarantine."""
        try:
            file_name = os.path.basename(file_path)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
            
            quarantine_name = f"{timestamp}_{file_hash}_{file_name}"
            quarantine_path = os.path.join(self.config['QUARANTINE_PATH'], quarantine_name)
            
            # Move file to quarantine
            shutil.move(file_path, quarantine_path)
            
            # Create info file
            info_path = f"{quarantine_path}.info"
            with open(info_path, 'w') as f:
                json.dump({
                    'original_path': file_path,
                    'quarantine_reason': reason,
                    'quarantine_time': datetime.utcnow().isoformat(),
                    'file_hash': self._get_file_info(quarantine_path)['sha256']
                }, f, indent=2)
            
            logger.warning(f"File quarantined: {file_path} -> {quarantine_path}. Reason: {reason}")
            
            return quarantine_path
            
        except Exception as e:
            logger.error(f"Failed to quarantine file: {str(e)}")
            # If quarantine fails, try to delete
            try:
                os.remove(file_path)
                logger.warning(f"File deleted: {file_path}")
            except:
                pass
            raise
    
    def _log_scan_result(self, file_path: str, result: Dict, user_id: Optional[int], start_time: datetime):
        """Log scan result to database."""
        try:
            scan_log = VirusScanLog(
                file_path=file_path,
                file_hash=result.get('file_info', {}).get('sha256'),
                file_size=result.get('file_info', {}).get('size'),
                scan_result=result.get('status'),
                is_infected=result.get('infected', False),
                threats_found=json.dumps(result.get('threats', [])),
                scan_details=json.dumps(result.get('scan_results', [])),
                scan_duration=(datetime.utcnow() - start_time).total_seconds(),
                user_id=user_id
            )
            db.session.add(scan_log)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to log scan result: {str(e)}")
    
    def get_scan_statistics(self, days: int = 30) -> Dict:
        """Get virus scan statistics."""
        from datetime import timedelta
        from sqlalchemy import func
        
        since = datetime.utcnow() - timedelta(days=days)
        
        stats = db.session.query(
            func.count(VirusScanLog.id).label('total_scans'),
            func.sum(case([(VirusScanLog.is_infected == True, 1)], else_=0)).label('infected_files'),
            func.avg(VirusScanLog.scan_duration).label('avg_scan_time')
        ).filter(VirusScanLog.created_at >= since).first()
        
        threat_stats = db.session.query(
            VirusScanLog.threats_found,
            func.count(VirusScanLog.id).label('count')
        ).filter(
            VirusScanLog.created_at >= since,
            VirusScanLog.is_infected == True
        ).group_by(VirusScanLog.threats_found).all()
        
        return {
            'period_days': days,
            'total_scans': stats.total_scans or 0,
            'infected_files': stats.infected_files or 0,
            'infection_rate': (stats.infected_files / stats.total_scans * 100) if stats.total_scans else 0,
            'avg_scan_time': float(stats.avg_scan_time or 0),
            'top_threats': self._parse_threat_stats(threat_stats)
        }
    
    def _parse_threat_stats(self, threat_stats: List) -> List[Dict]:
        """Parse threat statistics."""
        threat_counts = {}
        
        for stat in threat_stats:
            if stat.threats_found:
                threats = json.loads(stat.threats_found)
                for threat in threats:
                    threat_counts[threat] = threat_counts.get(threat, 0) + stat.count
        
        return sorted(
            [{'threat': k, 'count': v} for k, v in threat_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:10]


class ClamAVScanner:
    """ClamAV virus scanner implementation."""
    
    def scan(self, file_path: str) -> Dict:
        """Scan file using ClamAV."""
        return VirusScannerSecure.scan_file_clamav(file_path)
    


class VirusTotalScanner:
    """VirusTotal API scanner implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://www.virustotal.com/api/v3'
    
    def scan(self, file_path: str) -> Dict:
        """Scan file using VirusTotal API."""
        try:
            # Calculate file hash
            sha256 = self._calculate_sha256(file_path)
            
            # First check if file is already scanned
            existing_result = self._check_existing_scan(sha256)
            if existing_result:
                return existing_result
            
            # Upload and scan file
            file_id = self._upload_file(file_path)
            
            # Get scan results
            return self._get_scan_results(file_id)
            
        except Exception as e:
            raise Exception(f"VirusTotal scan failed: {str(e)}")
    
    def _calculate_sha256(self, file_path: str) -> str:
        """Calculate SHA256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _check_existing_scan(self, file_hash: str) -> Optional[Dict]:
        """Check if file was already scanned."""
        headers = {'x-apikey': self.api_key}
        response = requests.get(
            f"{self.base_url}/files/{file_hash}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            return self._parse_virustotal_response(data)
        
        return None
    
    def _upload_file(self, file_path: str) -> str:
        """Upload file to VirusTotal."""
        headers = {'x-apikey': self.api_key}
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{self.base_url}/files",
                headers=headers,
                files=files
            )
        
        if response.status_code != 200:
            raise Exception(f"Failed to upload file: {response.text}")
        
        data = response.json()
        return data['data']['id']
    
    def _get_scan_results(self, file_id: str) -> Dict:
        """Get scan results from VirusTotal."""
        headers = {'x-apikey': self.api_key}
        
        # Poll for results (in production, use webhooks)
        import time
        for _ in range(30):  # Max 5 minutes
            response = requests.get(
                f"{self.base_url}/analyses/{file_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['data']['attributes']['status'] == 'completed':
                    return self._parse_virustotal_response(data)
            
            time.sleep(10)
        
        raise Exception("VirusTotal scan timeout")
    
    def _parse_virustotal_response(self, data: Dict) -> Dict:
        """Parse VirusTotal API response."""
        attributes = data['data']['attributes']
        stats = attributes.get('last_analysis_stats', attributes.get('stats', {}))
        
        malicious_count = stats.get('malicious', 0)
        threats = []
        
        if 'last_analysis_results' in attributes:
            for engine, result in attributes['last_analysis_results'].items():
                if result['category'] == 'malicious':
                    threats.append(f"{engine}: {result['result']}")
        
        return {
            'scanner': 'VirusTotal',
            'infected': malicious_count > 0,
            'status': 'infected' if malicious_count > 0 else 'clean',
            'threats': threats[:10],  # Limit to 10 threats
            'detection_ratio': f"{malicious_count}/{stats.get('total', 0)}",
            'scan_date': attributes.get('last_analysis_date')
        }