"""
CDN Manager

Advanced CDN integration and management for optimal asset delivery,
including multi-CDN support, geographic optimization, and intelligent routing.
"""

import time
import hashlib
import logging
import requests
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import asyncio
import aiohttp


class CDNProvider(Enum):
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    FASTLY = "fastly"
    KEYCDN = "keycdn"
    CUSTOM = "custom"


class AssetType(Enum):
    IMAGE = "image"
    CSS = "css"
    JAVASCRIPT = "javascript"
    FONT = "font"
    VIDEO = "video"
    DOCUMENT = "document"
    API = "api"


@dataclass
class CDNEndpoint:
    """CDN endpoint configuration"""
    provider: CDNProvider
    base_url: str
    regions: List[str]
    priority: int
    supports_webp: bool = True
    supports_avif: bool = False
    supports_brotli: bool = True
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    api_key: Optional[str] = None
    api_secret: Optional[str] = None


@dataclass
class AssetDeliveryRule:
    """Asset delivery rule configuration"""
    asset_types: List[AssetType]
    preferred_providers: List[CDNProvider]
    cache_ttl: int
    compression_enabled: bool = True
    geo_routing: bool = True
    failover_enabled: bool = True


@dataclass
class CDNPerformanceMetrics:
    """CDN performance metrics"""
    provider: CDNProvider
    region: str
    response_time: float
    success_rate: float
    bandwidth_usage: int
    cache_hit_rate: float
    error_count: int
    last_updated: float


class CDNManager:
    """
    Advanced CDN manager with multi-provider support and intelligent routing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.endpoints = {}
        self.delivery_rules = []
        self.performance_metrics = {}
        self.asset_cache = {}
        self.geographic_mapping = {}
        
        # Performance tracking
        self.request_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'failovers': 0,
            'total_bandwidth': 0
        }
        
        # Initialize CDN endpoints
        self._init_cdn_endpoints()
        
        # Initialize delivery rules
        self._init_delivery_rules()
        
        # Start performance monitoring
        self._start_performance_monitoring()
    
    def register_cdn_endpoint(self, endpoint: CDNEndpoint):
        """Register a new CDN endpoint"""
        self.endpoints[endpoint.provider] = endpoint
        logging.info(f"Registered CDN endpoint: {endpoint.provider.value}")
    
    def get_asset_url(self, asset_path: str, asset_type: AssetType,
                     client_region: Optional[str] = None,
                     client_capabilities: Optional[Dict[str, bool]] = None) -> str:
        """
        Get optimized asset URL based on client location and capabilities.
        """
        # Normalize asset path
        asset_path = asset_path.lstrip('/')
        
        # Find best CDN endpoint for this asset
        best_endpoint = self._select_best_endpoint(
            asset_type, client_region, client_capabilities
        )
        
        if not best_endpoint:
            # Fallback to local serving
            return f"/{asset_path}"
        
        # Generate optimized URL
        optimized_url = self._generate_optimized_url(
            best_endpoint, asset_path, asset_type, client_capabilities
        )
        
        # Track request
        self._track_request(best_endpoint.provider, asset_type)
        
        return optimized_url
    
    def upload_asset(self, local_path: Union[str, Path], 
                    remote_path: str,
                    asset_type: AssetType,
                    providers: Optional[List[CDNProvider]] = None) -> Dict[CDNProvider, str]:
        """
        Upload asset to specified CDN providers.
        """
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Asset not found: {local_path}")
        
        providers = providers or list(self.endpoints.keys())
        upload_results = {}
        
        for provider in providers:
            if provider not in self.endpoints:
                logging.warning(f"CDN provider not configured: {provider}")
                continue
            
            try:
                endpoint = self.endpoints[provider]
                url = self._upload_to_provider(endpoint, local_path, remote_path)
                upload_results[provider] = url
                logging.info(f"Uploaded {local_path.name} to {provider.value}")
                
            except Exception as e:
                logging.error(f"Failed to upload to {provider.value}: {e}")
        
        return upload_results
    
    def purge_cache(self, asset_paths: Union[str, List[str]],
                   providers: Optional[List[CDNProvider]] = None) -> Dict[CDNProvider, bool]:
        """
        Purge cached assets from CDN providers.
        """
        if isinstance(asset_paths, str):
            asset_paths = [asset_paths]
        
        providers = providers or list(self.endpoints.keys())
        purge_results = {}
        
        for provider in providers:
            if provider not in self.endpoints:
                continue
            
            try:
                endpoint = self.endpoints[provider]
                success = self._purge_from_provider(endpoint, asset_paths)
                purge_results[provider] = success
                
                if success:
                    logging.info(f"Purged {len(asset_paths)} assets from {provider.value}")
                else:
                    logging.warning(f"Purge failed for {provider.value}")
                    
            except Exception as e:
                logging.error(f"Purge error for {provider.value}: {e}")
                purge_results[provider] = False
        
        return purge_results
    
    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive CDN performance report.
        """
        report = {
            'timestamp': time.time(),
            'request_stats': self.request_stats.copy(),
            'provider_performance': {},
            'geographic_performance': {},
            'recommendations': []
        }
        
        # Provider performance
        for provider, metrics in self.performance_metrics.items():
            if isinstance(metrics, list) and metrics:
                latest_metrics = metrics[-1]
                report['provider_performance'][provider.value] = {
                    'response_time_ms': latest_metrics.response_time,
                    'success_rate': latest_metrics.success_rate,
                    'cache_hit_rate': latest_metrics.cache_hit_rate,
                    'bandwidth_mb': latest_metrics.bandwidth_usage / (1024 * 1024)
                }
        
        # Geographic performance
        for region, region_metrics in self.geographic_mapping.items():
            report['geographic_performance'][region] = {
                'best_provider': region_metrics.get('best_provider'),
                'avg_response_time': region_metrics.get('avg_response_time', 0)
            }
        
        # Generate recommendations
        report['recommendations'] = self._generate_performance_recommendations()
        
        return report
    
    def optimize_asset_delivery(self, asset_path: str, 
                              optimization_options: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Generate optimized asset URLs for different scenarios.
        """
        optimization_options = optimization_options or {}
        optimized_urls = {}
        
        # Original asset
        optimized_urls['original'] = self.get_asset_url(asset_path, AssetType.IMAGE)
        
        # WebP version for supported browsers
        if optimization_options.get('webp', True):
            webp_path = self._convert_to_webp_path(asset_path)
            optimized_urls['webp'] = self.get_asset_url(
                webp_path, AssetType.IMAGE,
                client_capabilities={'webp': True}
            )
        
        # AVIF version for supported browsers
        if optimization_options.get('avif', True):
            avif_path = self._convert_to_avif_path(asset_path)
            optimized_urls['avif'] = self.get_asset_url(
                avif_path, AssetType.IMAGE,
                client_capabilities={'avif': True}
            )
        
        # Responsive versions
        if optimization_options.get('responsive', True):
            responsive_sizes = optimization_options.get('sizes', [480, 768, 1024, 1920])
            optimized_urls['responsive'] = {}
            
            for size in responsive_sizes:
                responsive_path = self._convert_to_responsive_path(asset_path, size)
                optimized_urls['responsive'][f'{size}w'] = self.get_asset_url(
                    responsive_path, AssetType.IMAGE
                )
        
        return optimized_urls
    
    def preload_assets(self, asset_paths: List[str], 
                      priority_regions: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Preload assets to CDN edge locations.
        """
        preload_results = {}
        
        for asset_path in asset_paths:
            try:
                # Determine asset type
                asset_type = self._detect_asset_type(asset_path)
                
                # Get best endpoint
                best_endpoint = self._select_best_endpoint(asset_type)
                
                if best_endpoint:
                    success = self._preload_to_provider(best_endpoint, asset_path)
                    preload_results[asset_path] = success
                else:
                    preload_results[asset_path] = False
                    
            except Exception as e:
                logging.error(f"Preload failed for {asset_path}: {e}")
                preload_results[asset_path] = False
        
        return preload_results
    
    # Private methods
    def _init_cdn_endpoints(self):
        """Initialize default CDN endpoints"""
        # Example Cloudflare endpoint
        if 'cloudflare' in self.config:
            cf_config = self.config['cloudflare']
            self.register_cdn_endpoint(CDNEndpoint(
                provider=CDNProvider.CLOUDFLARE,
                base_url=cf_config.get('base_url', 'https://cdn.example.com'),
                regions=['global'],
                priority=1,
                supports_webp=True,
                supports_avif=True,
                supports_brotli=True,
                api_key=cf_config.get('api_key'),
                api_secret=cf_config.get('api_secret')
            ))
        
        # Example AWS CloudFront endpoint
        if 'aws_cloudfront' in self.config:
            aws_config = self.config['aws_cloudfront']
            self.register_cdn_endpoint(CDNEndpoint(
                provider=CDNProvider.AWS_CLOUDFRONT,
                base_url=aws_config.get('base_url', 'https://d123.cloudfront.net'),
                regions=['us-east-1', 'eu-west-1', 'ap-southeast-1'],
                priority=2,
                supports_webp=True,
                supports_avif=False,
                api_key=aws_config.get('access_key'),
                api_secret=aws_config.get('secret_key')
            ))
    
    def _init_delivery_rules(self):
        """Initialize asset delivery rules"""
        # Images - prefer providers with modern format support
        self.delivery_rules.append(AssetDeliveryRule(
            asset_types=[AssetType.IMAGE],
            preferred_providers=[CDNProvider.CLOUDFLARE, CDNProvider.AWS_CLOUDFRONT],
            cache_ttl=86400,  # 24 hours
            compression_enabled=True,
            geo_routing=True
        ))
        
        # CSS/JS - prefer providers with good compression
        self.delivery_rules.append(AssetDeliveryRule(
            asset_types=[AssetType.CSS, AssetType.JAVASCRIPT],
            preferred_providers=[CDNProvider.CLOUDFLARE, CDNProvider.FASTLY],
            cache_ttl=3600,   # 1 hour
            compression_enabled=True,
            geo_routing=True
        ))
        
        # Fonts - long cache, geographic distribution
        self.delivery_rules.append(AssetDeliveryRule(
            asset_types=[AssetType.FONT],
            preferred_providers=[CDNProvider.GOOGLE_CDN, CDNProvider.CLOUDFLARE],
            cache_ttl=604800,  # 1 week
            compression_enabled=True,
            geo_routing=True
        ))
    
    def _select_best_endpoint(self, asset_type: AssetType,
                            client_region: Optional[str] = None,
                            client_capabilities: Optional[Dict[str, bool]] = None) -> Optional[CDNEndpoint]:
        """Select the best CDN endpoint for asset delivery"""
        client_capabilities = client_capabilities or {}
        
        # Find applicable delivery rules
        applicable_rules = [
            rule for rule in self.delivery_rules
            if asset_type in rule.asset_types
        ]
        
        if not applicable_rules:
            # Default to first available endpoint
            return next(iter(self.endpoints.values()), None)
        
        # Use the first applicable rule
        rule = applicable_rules[0]
        
        # Filter endpoints by capabilities
        suitable_endpoints = []
        for provider in rule.preferred_providers:
            if provider not in self.endpoints:
                continue
            
            endpoint = self.endpoints[provider]
            
            # Check format support
            if client_capabilities.get('webp', False) and not endpoint.supports_webp:
                continue
            if client_capabilities.get('avif', False) and not endpoint.supports_avif:
                continue
            
            # Check regional performance
            if client_region and self._has_poor_regional_performance(provider, client_region):
                continue
            
            suitable_endpoints.append(endpoint)
        
        if not suitable_endpoints:
            return None
        
        # Select best endpoint based on performance metrics
        return self._select_best_performing_endpoint(suitable_endpoints, client_region)
    
    def _generate_optimized_url(self, endpoint: CDNEndpoint, asset_path: str,
                              asset_type: AssetType,
                              client_capabilities: Optional[Dict[str, bool]] = None) -> str:
        """Generate optimized URL for asset"""
        client_capabilities = client_capabilities or {}
        
        base_url = endpoint.base_url.rstrip('/')
        asset_path = asset_path.lstrip('/')
        
        # Add format optimization parameters
        url_params = []
        
        if asset_type == AssetType.IMAGE:
            # Auto format selection
            if client_capabilities.get('avif', False) and endpoint.supports_avif:
                url_params.append('f=avif')
            elif client_capabilities.get('webp', False) and endpoint.supports_webp:
                url_params.append('f=webp')
            
            # Quality optimization
            url_params.append('q=auto')
        
        # Add compression parameters
        if endpoint.supports_brotli and client_capabilities.get('brotli', True):
            url_params.append('compress=br')
        elif client_capabilities.get('gzip', True):
            url_params.append('compress=gzip')
        
        # Build final URL
        url = f"{base_url}/{asset_path}"
        if url_params:
            url += '?' + '&'.join(url_params)
        
        return url
    
    def _upload_to_provider(self, endpoint: CDNEndpoint, 
                          local_path: Path, remote_path: str) -> str:
        """Upload asset to CDN provider"""
        if endpoint.provider == CDNProvider.CLOUDFLARE:
            return self._upload_to_cloudflare(endpoint, local_path, remote_path)
        elif endpoint.provider == CDNProvider.AWS_CLOUDFRONT:
            return self._upload_to_aws(endpoint, local_path, remote_path)
        else:
            # Generic upload implementation
            return self._upload_generic(endpoint, local_path, remote_path)
    
    def _upload_to_cloudflare(self, endpoint: CDNEndpoint,
                            local_path: Path, remote_path: str) -> str:
        """Upload to Cloudflare"""
        # Implement Cloudflare-specific upload logic
        # This would use Cloudflare's API
        logging.info(f"Uploading {local_path.name} to Cloudflare")
        return f"{endpoint.base_url}/{remote_path}"
    
    def _upload_to_aws(self, endpoint: CDNEndpoint,
                      local_path: Path, remote_path: str) -> str:
        """Upload to AWS CloudFront (via S3)"""
        # Implement AWS S3 upload logic
        # This would use boto3
        logging.info(f"Uploading {local_path.name} to AWS CloudFront")
        return f"{endpoint.base_url}/{remote_path}"
    
    def _upload_generic(self, endpoint: CDNEndpoint,
                       local_path: Path, remote_path: str) -> str:
        """Generic upload implementation"""
        # Implement generic HTTP upload
        logging.info(f"Uploading {local_path.name} to {endpoint.provider.value}")
        return f"{endpoint.base_url}/{remote_path}"
    
    def _purge_from_provider(self, endpoint: CDNEndpoint, asset_paths: List[str]) -> bool:
        """Purge assets from CDN provider"""
        if endpoint.provider == CDNProvider.CLOUDFLARE:
            return self._purge_cloudflare(endpoint, asset_paths)
        elif endpoint.provider == CDNProvider.AWS_CLOUDFRONT:
            return self._purge_aws(endpoint, asset_paths)
        else:
            return self._purge_generic(endpoint, asset_paths)
    
    def _purge_cloudflare(self, endpoint: CDNEndpoint, asset_paths: List[str]) -> bool:
        """Purge from Cloudflare"""
        # Implement Cloudflare purge API call
        logging.info(f"Purging {len(asset_paths)} assets from Cloudflare")
        return True
    
    def _purge_aws(self, endpoint: CDNEndpoint, asset_paths: List[str]) -> bool:
        """Purge from AWS CloudFront"""
        # Implement AWS CloudFront invalidation
        logging.info(f"Purging {len(asset_paths)} assets from AWS CloudFront")
        return True
    
    def _purge_generic(self, endpoint: CDNEndpoint, asset_paths: List[str]) -> bool:
        """Generic purge implementation"""
        logging.info(f"Purging {len(asset_paths)} assets from {endpoint.provider.value}")
        return True
    
    def _preload_to_provider(self, endpoint: CDNEndpoint, asset_path: str) -> bool:
        """Preload asset to CDN edge locations"""
        # Implement preloading logic specific to provider
        logging.info(f"Preloading {asset_path} to {endpoint.provider.value}")
        return True
    
    def _detect_asset_type(self, asset_path: str) -> AssetType:
        """Detect asset type from file extension"""
        extension = Path(asset_path).suffix.lower()
        
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.avif', '.svg']:
            return AssetType.IMAGE
        elif extension in ['.css']:
            return AssetType.CSS
        elif extension in ['.js', '.mjs']:
            return AssetType.JAVASCRIPT
        elif extension in ['.woff', '.woff2', '.ttf', '.otf']:
            return AssetType.FONT
        elif extension in ['.mp4', '.webm', '.ogg']:
            return AssetType.VIDEO
        elif extension in ['.pdf', '.doc', '.docx']:
            return AssetType.DOCUMENT
        else:
            return AssetType.DOCUMENT  # Default
    
    def _convert_to_webp_path(self, asset_path: str) -> str:
        """Convert asset path to WebP version"""
        path = Path(asset_path)
        return str(path.with_suffix('.webp'))
    
    def _convert_to_avif_path(self, asset_path: str) -> str:
        """Convert asset path to AVIF version"""
        path = Path(asset_path)
        return str(path.with_suffix('.avif'))
    
    def _convert_to_responsive_path(self, asset_path: str, width: int) -> str:
        """Convert asset path to responsive version"""
        path = Path(asset_path)
        stem = path.stem
        suffix = path.suffix
        return str(path.with_name(f"{stem}_w{width}{suffix}"))
    
    def _track_request(self, provider: CDNProvider, asset_type: AssetType):
        """Track CDN request statistics"""
        self.request_stats['total_requests'] += 1
        
        # Track per-provider stats (simplified)
        provider_stats = self.performance_metrics.setdefault(provider, [])
        # Would normally update detailed metrics here
    
    def _has_poor_regional_performance(self, provider: CDNProvider, region: str) -> bool:
        """Check if provider has poor performance in region"""
        # Implement regional performance checking
        return False
    
    def _select_best_performing_endpoint(self, endpoints: List[CDNEndpoint],
                                       client_region: Optional[str] = None) -> CDNEndpoint:
        """Select best performing endpoint from candidates"""
        # Simple implementation - could be more sophisticated
        return min(endpoints, key=lambda e: e.priority)
    
    def _start_performance_monitoring(self):
        """Start background performance monitoring"""
        # This would run periodic performance tests
        logging.info("Starting CDN performance monitoring...")
    
    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Check cache hit rates
        total_requests = self.request_stats['total_requests']
        cache_hits = self.request_stats['cache_hits']
        
        if total_requests > 0:
            hit_rate = cache_hits / total_requests
            if hit_rate < 0.8:  # Less than 80% hit rate
                recommendations.append("Low cache hit rate detected - consider longer TTL or cache warming")
        
        # Check failover frequency
        failovers = self.request_stats['failovers']
        if failovers > total_requests * 0.05:  # More than 5% failover rate
            recommendations.append("High failover rate - investigate CDN provider reliability")
        
        # Provider-specific recommendations
        for provider, metrics_list in self.performance_metrics.items():
            if metrics_list and isinstance(metrics_list, list):
                latest = metrics_list[-1]
                if latest.response_time > 500:  # > 500ms
                    recommendations.append(f"High response time for {provider.value} - consider provider optimization")
        
        return recommendations