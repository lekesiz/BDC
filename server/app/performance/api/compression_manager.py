"""
Compression Manager

Advanced compression strategies for different content types,
including dynamic compression selection and compression analytics.
"""

import gzip
import brotli
import zlib
import lz4.frame
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict


class CompressionType(Enum):
    GZIP = "gzip"
    BROTLI = "br"
    DEFLATE = "deflate"
    LZ4 = "lz4"
    NONE = "none"


class ContentType(Enum):
    JSON = "application/json"
    HTML = "text/html"
    CSS = "text/css"
    JAVASCRIPT = "application/javascript"
    XML = "application/xml"
    TEXT = "text/plain"
    CSV = "text/csv"


@dataclass
class CompressionConfig:
    """Compression configuration settings"""
    enabled_types: List[CompressionType] = None
    content_type_preferences: Dict[ContentType, List[CompressionType]] = None
    size_threshold: int = 1024  # Minimum size to compress (bytes)
    max_size: int = 50 * 1024 * 1024  # Maximum size to compress (50MB)
    compression_levels: Dict[CompressionType, int] = None
    enable_adaptive: bool = True
    benchmark_interval: int = 3600  # Benchmark every hour
    
    def __post_init__(self):
        if self.enabled_types is None:
            self.enabled_types = [
                CompressionType.GZIP,
                CompressionType.BROTLI,
                CompressionType.DEFLATE
            ]
        
        if self.content_type_preferences is None:
            self.content_type_preferences = {
                ContentType.JSON: [CompressionType.BROTLI, CompressionType.GZIP],
                ContentType.HTML: [CompressionType.BROTLI, CompressionType.GZIP],
                ContentType.CSS: [CompressionType.BROTLI, CompressionType.GZIP],
                ContentType.JAVASCRIPT: [CompressionType.BROTLI, CompressionType.GZIP],
                ContentType.XML: [CompressionType.GZIP, CompressionType.DEFLATE],
                ContentType.TEXT: [CompressionType.GZIP, CompressionType.DEFLATE],
                ContentType.CSV: [CompressionType.GZIP, CompressionType.LZ4]
            }
        
        if self.compression_levels is None:
            self.compression_levels = {
                CompressionType.GZIP: 6,
                CompressionType.BROTLI: 4,
                CompressionType.DEFLATE: 6,
                CompressionType.LZ4: 0
            }


@dataclass
class CompressionResult:
    """Result of compression operation"""
    original_size: int
    compressed_size: int
    compression_type: CompressionType
    compression_ratio: float
    compression_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class CompressionStats:
    """Compression statistics per type"""
    total_operations: int = 0
    total_time: float = 0.0
    total_original_size: int = 0
    total_compressed_size: int = 0
    avg_compression_ratio: float = 0.0
    avg_compression_time: float = 0.0
    success_rate: float = 0.0


class CompressionManager:
    """
    Advanced compression manager with adaptive compression selection.
    """
    
    def __init__(self, config: Optional[CompressionConfig] = None):
        self.config = config or CompressionConfig()
        self.stats = defaultdict(CompressionStats)
        self.benchmark_results = {}
        self.last_benchmark = 0
        self.adaptive_preferences = {}
        
        # Initialize compression functions
        self.compressors = {
            CompressionType.GZIP: self._compress_gzip,
            CompressionType.BROTLI: self._compress_brotli,
            CompressionType.DEFLATE: self._compress_deflate,
            CompressionType.LZ4: self._compress_lz4
        }
        
        self.decompressors = {
            CompressionType.GZIP: self._decompress_gzip,
            CompressionType.BROTLI: self._decompress_brotli,
            CompressionType.DEFLATE: self._decompress_deflate,
            CompressionType.LZ4: self._decompress_lz4
        }
    
    def compress(self, data: Union[str, bytes], content_type: str,
                accepted_encodings: List[str] = None) -> CompressionResult:
        """
        Compress data using the best available compression method.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Check size thresholds
        if len(data) < self.config.size_threshold:
            return CompressionResult(
                original_size=len(data),
                compressed_size=len(data),
                compression_type=CompressionType.NONE,
                compression_ratio=1.0,
                compression_time=0.0,
                success=True
            )
        
        if len(data) > self.config.max_size:
            return CompressionResult(
                original_size=len(data),
                compressed_size=len(data),
                compression_type=CompressionType.NONE,
                compression_ratio=1.0,
                compression_time=0.0,
                success=False,
                error_message="Data too large for compression"
            )
        
        # Determine content type
        content_enum = self._parse_content_type(content_type)
        
        # Get preferred compression types
        preferred_types = self._get_preferred_compression_types(
            content_enum, accepted_encodings
        )
        
        # Try compression with preferred types
        best_result = None
        
        for compression_type in preferred_types:
            if compression_type not in self.config.enabled_types:
                continue
            
            try:
                result = self._perform_compression(data, compression_type)
                
                # Update statistics
                self._update_stats(compression_type, result)
                
                # Keep best result (smallest size)
                if best_result is None or result.compressed_size < best_result.compressed_size:
                    best_result = result
                
                # If we get good compression quickly, use it
                if result.compression_ratio < 0.7:  # 30% compression
                    break
                    
            except Exception as e:
                logging.error(f"Compression failed with {compression_type.value}: {e}")
                continue
        
        # Return best result or uncompressed
        if best_result and best_result.compressed_size < len(data):
            return best_result
        else:
            return CompressionResult(
                original_size=len(data),
                compressed_size=len(data),
                compression_type=CompressionType.NONE,
                compression_ratio=1.0,
                compression_time=0.0,
                success=True
            )
    
    def decompress(self, data: bytes, compression_type: CompressionType) -> bytes:
        """
        Decompress data using the specified compression type.
        """
        if compression_type == CompressionType.NONE:
            return data
        
        if compression_type not in self.decompressors:
            raise ValueError(f"Unsupported compression type: {compression_type}")
        
        return self.decompressors[compression_type](data)
    
    def benchmark_compression_types(self, test_data: bytes) -> Dict[CompressionType, Dict[str, float]]:
        """
        Benchmark different compression types with test data.
        """
        results = {}
        
        for compression_type in self.config.enabled_types:
            try:
                start_time = time.time()
                compressed = self.compressors[compression_type](test_data)
                compression_time = time.time() - start_time
                
                compression_ratio = len(compressed) / len(test_data)
                
                results[compression_type] = {
                    'compression_ratio': compression_ratio,
                    'compression_time': compression_time,
                    'compressed_size': len(compressed),
                    'speed_mbps': (len(test_data) / (1024 * 1024)) / compression_time
                }
                
            except Exception as e:
                logging.error(f"Benchmark failed for {compression_type.value}: {e}")
                results[compression_type] = {
                    'compression_ratio': 1.0,
                    'compression_time': float('inf'),
                    'compressed_size': len(test_data),
                    'speed_mbps': 0.0
                }
        
        self.benchmark_results = results
        self.last_benchmark = time.time()
        
        # Update adaptive preferences based on benchmark
        self._update_adaptive_preferences()
        
        return results
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive compression statistics.
        """
        stats_dict = {}
        
        for compression_type, stats in self.stats.items():
            if stats.total_operations > 0:
                stats_dict[compression_type.value] = {
                    'total_operations': stats.total_operations,
                    'avg_compression_ratio': round(stats.avg_compression_ratio, 3),
                    'avg_compression_time_ms': round(stats.avg_compression_time * 1000, 2),
                    'success_rate': round(stats.success_rate, 3),
                    'total_size_saved_mb': round(
                        (stats.total_original_size - stats.total_compressed_size) / (1024 * 1024), 2
                    ),
                    'bandwidth_savings_percent': round(
                        (1 - stats.avg_compression_ratio) * 100, 1
                    )
                }
        
        # Add overall statistics
        total_ops = sum(stats.total_operations for stats in self.stats.values())
        total_original = sum(stats.total_original_size for stats in self.stats.values())
        total_compressed = sum(stats.total_compressed_size for stats in self.stats.values())
        
        overall_ratio = total_compressed / total_original if total_original > 0 else 1.0
        
        stats_dict['overall'] = {
            'total_operations': total_ops,
            'overall_compression_ratio': round(overall_ratio, 3),
            'total_bandwidth_saved_mb': round((total_original - total_compressed) / (1024 * 1024), 2),
            'bandwidth_savings_percent': round((1 - overall_ratio) * 100, 1)
        }
        
        return stats_dict
    
    def optimize_for_content_type(self, content_type: ContentType, 
                                 sample_data: bytes) -> List[CompressionType]:
        """
        Optimize compression preferences for a specific content type.
        """
        # Run benchmark with sample data
        benchmark_results = {}
        
        for compression_type in self.config.enabled_types:
            try:
                result = self._perform_compression(sample_data, compression_type)
                
                # Calculate efficiency score (compression ratio / time)
                efficiency = (1 - result.compression_ratio) / result.compression_time
                
                benchmark_results[compression_type] = {
                    'efficiency': efficiency,
                    'compression_ratio': result.compression_ratio,
                    'compression_time': result.compression_time
                }
                
            except Exception as e:
                logging.error(f"Optimization benchmark failed for {compression_type.value}: {e}")
        
        # Sort by efficiency (best first)
        sorted_types = sorted(
            benchmark_results.keys(),
            key=lambda ct: benchmark_results[ct]['efficiency'],
            reverse=True
        )
        
        # Update preferences
        self.config.content_type_preferences[content_type] = sorted_types
        
        return sorted_types
    
    # Private methods
    def _perform_compression(self, data: bytes, compression_type: CompressionType) -> CompressionResult:
        """Perform compression with timing and error handling"""
        start_time = time.time()
        
        try:
            compressed_data = self.compressors[compression_type](data)
            compression_time = time.time() - start_time
            
            return CompressionResult(
                original_size=len(data),
                compressed_size=len(compressed_data),
                compression_type=compression_type,
                compression_ratio=len(compressed_data) / len(data),
                compression_time=compression_time,
                success=True
            )
            
        except Exception as e:
            compression_time = time.time() - start_time
            
            return CompressionResult(
                original_size=len(data),
                compressed_size=len(data),
                compression_type=compression_type,
                compression_ratio=1.0,
                compression_time=compression_time,
                success=False,
                error_message=str(e)
            )
    
    def _parse_content_type(self, content_type: str) -> ContentType:
        """Parse content type string to enum"""
        content_type = content_type.lower().split(';')[0].strip()
        
        content_type_map = {
            'application/json': ContentType.JSON,
            'text/html': ContentType.HTML,
            'text/css': ContentType.CSS,
            'application/javascript': ContentType.JAVASCRIPT,
            'text/javascript': ContentType.JAVASCRIPT,
            'application/xml': ContentType.XML,
            'text/xml': ContentType.XML,
            'text/plain': ContentType.TEXT,
            'text/csv': ContentType.CSV
        }
        
        return content_type_map.get(content_type, ContentType.TEXT)
    
    def _get_preferred_compression_types(self, content_type: ContentType, 
                                       accepted_encodings: List[str] = None) -> List[CompressionType]:
        """Get preferred compression types for content type and client support"""
        if accepted_encodings is None:
            accepted_encodings = ['gzip', 'br', 'deflate']
        
        # Get base preferences
        preferences = self.config.content_type_preferences.get(
            content_type, [CompressionType.GZIP]
        )
        
        # Filter by client support
        supported_types = []
        for comp_type in preferences:
            if comp_type.value in accepted_encodings:
                supported_types.append(comp_type)
        
        # Apply adaptive preferences if enabled
        if self.config.enable_adaptive and content_type in self.adaptive_preferences:
            adaptive_prefs = self.adaptive_preferences[content_type]
            # Merge with base preferences, giving priority to adaptive
            supported_types = adaptive_prefs + [ct for ct in supported_types if ct not in adaptive_prefs]
        
        return supported_types or [CompressionType.GZIP]
    
    def _update_stats(self, compression_type: CompressionType, result: CompressionResult):
        """Update compression statistics"""
        stats = self.stats[compression_type]
        
        # Update counters
        stats.total_operations += 1
        stats.total_time += result.compression_time
        stats.total_original_size += result.original_size
        stats.total_compressed_size += result.compressed_size
        
        # Update averages
        stats.avg_compression_ratio = (
            stats.total_compressed_size / stats.total_original_size
        )
        stats.avg_compression_time = (
            stats.total_time / stats.total_operations
        )
        
        # Update success rate
        if result.success:
            stats.success_rate = (
                (stats.success_rate * (stats.total_operations - 1) + 1) / stats.total_operations
            )
        else:
            stats.success_rate = (
                stats.success_rate * (stats.total_operations - 1) / stats.total_operations
            )
    
    def _update_adaptive_preferences(self):
        """Update adaptive compression preferences based on benchmarks"""
        if not self.benchmark_results:
            return
        
        # For each content type, reorder preferences based on benchmark results
        for content_type in ContentType:
            # Calculate efficiency scores
            efficiency_scores = {}
            
            for comp_type, benchmark in self.benchmark_results.items():
                # Efficiency = compression savings / time
                compression_savings = 1 - benchmark['compression_ratio']
                time_penalty = benchmark['compression_time']
                
                efficiency_scores[comp_type] = compression_savings / max(time_penalty, 0.001)
            
            # Sort by efficiency
            sorted_types = sorted(
                efficiency_scores.keys(),
                key=lambda ct: efficiency_scores[ct],
                reverse=True
            )
            
            self.adaptive_preferences[content_type] = sorted_types
    
    # Compression implementations
    def _compress_gzip(self, data: bytes) -> bytes:
        """Compress using gzip"""
        level = self.config.compression_levels.get(CompressionType.GZIP, 6)
        return gzip.compress(data, compresslevel=level)
    
    def _compress_brotli(self, data: bytes) -> bytes:
        """Compress using Brotli"""
        level = self.config.compression_levels.get(CompressionType.BROTLI, 4)
        return brotli.compress(data, quality=level)
    
    def _compress_deflate(self, data: bytes) -> bytes:
        """Compress using deflate"""
        level = self.config.compression_levels.get(CompressionType.DEFLATE, 6)
        return zlib.compress(data, level=level)
    
    def _compress_lz4(self, data: bytes) -> bytes:
        """Compress using LZ4"""
        return lz4.frame.compress(data)
    
    # Decompression implementations
    def _decompress_gzip(self, data: bytes) -> bytes:
        """Decompress gzip data"""
        return gzip.decompress(data)
    
    def _decompress_brotli(self, data: bytes) -> bytes:
        """Decompress Brotli data"""
        return brotli.decompress(data)
    
    def _decompress_deflate(self, data: bytes) -> bytes:
        """Decompress deflate data"""
        return zlib.decompress(data)
    
    def _decompress_lz4(self, data: bytes) -> bytes:
        """Decompress LZ4 data"""
        return lz4.frame.decompress(data)