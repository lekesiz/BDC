"""
CDN Configuration for Static Assets
Configures Content Delivery Network settings for optimal static asset delivery.
"""

import os
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

from flask import Flask, url_for, current_app
from werkzeug.urls import url_parse

from app.utils.logging import logger


class CDNManager:
    """Manages CDN configuration and asset delivery optimization"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.cdn_domain = None
        self.cdn_https = True
        self.asset_versioning = True
        self.cache_busting = True
        self.compression_enabled = True
        
        # Asset type configurations
        self.asset_configs = {
            'images': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'],
                'cache_control': 'public, max-age=31536000',  # 1 year
                'compression': True,
                'optimization': True
            },
            'styles': {
                'extensions': ['.css'],
                'cache_control': 'public, max-age=31536000',  # 1 year
                'compression': True,
                'minification': True
            },
            'scripts': {
                'extensions': ['.js'],
                'cache_control': 'public, max-age=31536000',  # 1 year
                'compression': True,
                'minification': True
            },
            'fonts': {
                'extensions': ['.woff', '.woff2', '.ttf', '.eot', '.otf'],
                'cache_control': 'public, max-age=31536000',  # 1 year
                'compression': False,  # Fonts are already compressed
                'cors_enabled': True
            },
            'documents': {
                'extensions': ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
                'cache_control': 'public, max-age=86400',  # 1 day
                'compression': True,
                'security_headers': True
            },
            'media': {
                'extensions': ['.mp4', '.mp3', '.avi', '.mov', '.wav'],
                'cache_control': 'public, max-age=604800',  # 1 week
                'compression': False,  # Media files are already compressed
                'streaming_enabled': True
            }
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize CDN configuration with Flask app"""
        self.app = app
        
        # Load CDN configuration from app config
        self.cdn_domain = app.config.get('CDN_DOMAIN')
        self.cdn_https = app.config.get('CDN_HTTPS', True)
        self.asset_versioning = app.config.get('CDN_ASSET_VERSIONING', True)
        self.cache_busting = app.config.get('CDN_CACHE_BUSTING', True)
        
        # Register template context processor
        app.context_processor(self._inject_cdn_helpers)
        
        # Configure static file serving with CDN
        if self.cdn_domain:
            self._setup_cdn_routing()
        
        logger.info(f"CDN configuration initialized: {self.cdn_domain or 'Local serving'}")
    
    def _inject_cdn_helpers(self):
        """Inject CDN helper functions into template context"""
        return {
            'cdn_url': self.get_cdn_url,
            'static_url': self.get_static_url,
            'asset_url': self.get_asset_url
        }
    
    def _setup_cdn_routing(self):
        """Setup CDN routing for static files"""
        if not self.app:
            return
        
        # Override static URL generation
        original_url_for = self.app.jinja_env.globals['url_for']
        
        def cdn_url_for(endpoint, **values):
            if endpoint == 'static':
                filename = values.get('filename', '')
                return self.get_static_url(filename)
            return original_url_for(endpoint, **values)
        
        self.app.jinja_env.globals['url_for'] = cdn_url_for
    
    def get_cdn_url(self, path: str) -> str:
        """Get CDN URL for a given path"""
        if not self.cdn_domain:
            return path
        
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        # Build CDN URL
        scheme = 'https' if self.cdn_https else 'http'
        return f"{scheme}://{self.cdn_domain}{path}"
    
    def get_static_url(self, filename: str) -> str:
        """Get optimized URL for static assets"""
        if not filename:
            return ''
        
        # Add version/cache busting if enabled
        if self.cache_busting:
            filename = self._add_cache_buster(filename)
        
        # Generate base URL
        if self.cdn_domain:
            static_path = f"/static/{filename}"
            return self.get_cdn_url(static_path)
        else:
            # Use Flask's url_for for local serving
            return url_for('static', filename=filename)
    
    def get_asset_url(self, asset_type: str, filename: str) -> str:
        """Get optimized URL for specific asset types"""
        asset_config = self.asset_configs.get(asset_type, {})
        
        # Add asset type prefix if configured
        if asset_type in ['images', 'styles', 'scripts', 'fonts']:
            filename = f"{asset_type}/{filename}"
        
        return self.get_static_url(filename)
    
    def _add_cache_buster(self, filename: str) -> str:
        """Add cache busting parameter to filename"""
        if not self.cache_busting:
            return filename
        
        # Try to get file modification time for versioning
        if self.app:
            static_folder = self.app.static_folder
            if static_folder:
                file_path = os.path.join(static_folder, filename)
                if os.path.exists(file_path):
                    try:
                        mtime = int(os.path.getmtime(file_path))
                        return f"{filename}?v={mtime}"
                    except OSError:
                        pass
        
        # Fallback to app version if available
        version = current_app.config.get('APP_VERSION', '1.0.0')
        return f"{filename}?v={version.replace('.', '')}"
    
    def get_asset_headers(self, filename: str) -> Dict[str, str]:
        """Get HTTP headers for asset delivery"""
        headers = {}
        
        # Determine asset type
        asset_type = self._get_asset_type(filename)
        asset_config = self.asset_configs.get(asset_type, {})
        
        # Cache control headers
        cache_control = asset_config.get('cache_control', 'public, max-age=3600')
        headers['Cache-Control'] = cache_control
        
        # Compression headers
        if asset_config.get('compression', False):
            headers['Vary'] = 'Accept-Encoding'
        
        # CORS headers for fonts
        if asset_config.get('cors_enabled', False):
            headers['Access-Control-Allow-Origin'] = '*'
            headers['Access-Control-Allow-Methods'] = 'GET'
            headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        # Security headers for documents
        if asset_config.get('security_headers', False):
            headers['X-Content-Type-Options'] = 'nosniff'
            headers['X-Frame-Options'] = 'DENY'
        
        # Content type headers
        content_type = self._get_content_type(filename)
        if content_type:
            headers['Content-Type'] = content_type
        
        return headers
    
    def _get_asset_type(self, filename: str) -> str:
        """Determine asset type from filename"""
        _, ext = os.path.splitext(filename.lower())
        
        for asset_type, config in self.asset_configs.items():
            if ext in config.get('extensions', []):
                return asset_type
        
        return 'unknown'
    
    def _get_content_type(self, filename: str) -> Optional[str]:
        """Get content type for filename"""
        _, ext = os.path.splitext(filename.lower())
        
        content_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.eot': 'application/vnd.ms-fontobject',
            '.otf': 'font/otf',
            '.pdf': 'application/pdf',
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg'
        }
        
        return content_types.get(ext)
    
    def generate_asset_manifest(self) -> Dict[str, Any]:
        """Generate asset manifest for cache management"""
        manifest = {
            'version': current_app.config.get('APP_VERSION', '1.0.0'),
            'cdn_domain': self.cdn_domain,
            'assets': {},
            'generated_at': '2024-01-01T00:00:00Z'  # Placeholder
        }
        
        if not self.app or not self.app.static_folder:
            return manifest
        
        static_folder = self.app.static_folder
        
        try:
            # Walk through static files
            for root, dirs, files in os.walk(static_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, static_folder)
                    
                    # Normalize path separators
                    relative_path = relative_path.replace(os.sep, '/')
                    
                    # Get file info
                    try:
                        stat = os.stat(file_path)
                        asset_type = self._get_asset_type(file)
                        
                        manifest['assets'][relative_path] = {
                            'size': stat.st_size,
                            'mtime': int(stat.st_mtime),
                            'type': asset_type,
                            'url': self.get_static_url(relative_path),
                            'headers': self.get_asset_headers(relative_path)
                        }
                    except OSError:
                        continue
        
        except Exception as e:
            logger.error(f"Error generating asset manifest: {e}")
        
        return manifest
    
    def optimize_asset_delivery(self) -> Dict[str, Any]:
        """Analyze and optimize asset delivery"""
        optimization_report = {
            'recommendations': [],
            'asset_analysis': {},
            'performance_metrics': {}
        }
        
        try:
            manifest = self.generate_asset_manifest()
            assets = manifest.get('assets', {})
            
            # Analyze asset sizes
            total_size = 0
            large_assets = []
            uncompressed_assets = []
            
            for path, info in assets.items():
                size = info.get('size', 0)
                total_size += size
                asset_type = info.get('type', 'unknown')
                
                # Check for large assets
                if size > 1024 * 1024:  # 1MB
                    large_assets.append({
                        'path': path,
                        'size_mb': size / (1024 * 1024),
                        'type': asset_type
                    })
                
                # Check for uncompressed assets
                asset_config = self.asset_configs.get(asset_type, {})
                if asset_config.get('compression', False) and size > 10240:  # 10KB
                    uncompressed_assets.append({
                        'path': path,
                        'size_kb': size / 1024,
                        'type': asset_type
                    })
            
            # Generate recommendations
            if large_assets:
                optimization_report['recommendations'].append({
                    'type': 'size_optimization',
                    'priority': 'high',
                    'description': f'Found {len(large_assets)} large assets that could be optimized',
                    'assets': large_assets[:5]  # Top 5
                })
            
            if uncompressed_assets:
                optimization_report['recommendations'].append({
                    'type': 'compression',
                    'priority': 'medium',
                    'description': f'Found {len(uncompressed_assets)} assets that could benefit from compression',
                    'assets': uncompressed_assets[:5]  # Top 5
                })
            
            if not self.cdn_domain:
                optimization_report['recommendations'].append({
                    'type': 'cdn_setup',
                    'priority': 'medium',
                    'description': 'Consider setting up a CDN for better asset delivery performance'
                })
            
            # Performance metrics
            optimization_report['performance_metrics'] = {
                'total_assets': len(assets),
                'total_size_mb': total_size / (1024 * 1024),
                'large_assets_count': len(large_assets),
                'cdn_enabled': bool(self.cdn_domain),
                'cache_busting_enabled': self.cache_busting,
                'compression_enabled': self.compression_enabled
            }
            
            # Asset analysis by type
            type_analysis = {}
            for path, info in assets.items():
                asset_type = info.get('type', 'unknown')
                if asset_type not in type_analysis:
                    type_analysis[asset_type] = {
                        'count': 0,
                        'total_size': 0,
                        'average_size': 0
                    }
                
                type_analysis[asset_type]['count'] += 1
                type_analysis[asset_type]['total_size'] += info.get('size', 0)
            
            # Calculate averages
            for asset_type, analysis in type_analysis.items():
                if analysis['count'] > 0:
                    analysis['average_size'] = analysis['total_size'] / analysis['count']
                    analysis['total_size_mb'] = analysis['total_size'] / (1024 * 1024)
                    analysis['average_size_kb'] = analysis['average_size'] / 1024
            
            optimization_report['asset_analysis'] = type_analysis
        
        except Exception as e:
            logger.error(f"Asset optimization analysis failed: {e}")
            optimization_report['error'] = str(e)
        
        return optimization_report


# Global CDN manager instance
cdn_manager = CDNManager()


def init_cdn_configuration(app: Flask):
    """Initialize CDN configuration for Flask app"""
    cdn_manager.init_app(app)
    
    # Setup static file serving with optimized headers
    @app.after_request
    def add_asset_headers(response):
        # Only apply to static files
        if hasattr(response, 'headers') and response.status_code == 200:
            # Check if this is a static file request
            if hasattr(response, 'direct_passthrough') and response.direct_passthrough:
                # This is likely a static file
                content_type = response.headers.get('Content-Type', '')
                
                # Apply appropriate cache headers based on content type
                if any(ct in content_type for ct in ['image/', 'font/', 'text/css', 'application/javascript']):
                    # Long cache for static assets
                    response.headers['Cache-Control'] = 'public, max-age=31536000'
                    response.headers['Vary'] = 'Accept-Encoding'
                
                # Add security headers
                response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response
    
    logger.info("CDN configuration initialized")


def get_optimized_asset_url(asset_type: str, filename: str) -> str:
    """Get optimized URL for an asset"""
    return cdn_manager.get_asset_url(asset_type, filename)


def generate_asset_preload_tags(critical_assets: List[str]) -> str:
    """Generate HTML preload tags for critical assets"""
    preload_tags = []
    
    for asset in critical_assets:
        asset_type = cdn_manager._get_asset_type(asset)
        url = cdn_manager.get_static_url(asset)
        
        # Determine preload type
        if asset_type == 'styles':
            preload_tags.append(f'<link rel="preload" href="{url}" as="style">')
        elif asset_type == 'scripts':
            preload_tags.append(f'<link rel="preload" href="{url}" as="script">')
        elif asset_type == 'fonts':
            preload_tags.append(f'<link rel="preload" href="{url}" as="font" type="font/woff2" crossorigin>')
        elif asset_type == 'images':
            preload_tags.append(f'<link rel="preload" href="{url}" as="image">')
    
    return '\n'.join(preload_tags)