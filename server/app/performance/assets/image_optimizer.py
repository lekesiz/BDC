"""
Image Optimizer

Advanced image optimization including compression, format conversion,
responsive images, and automatic optimization based on client capabilities.
"""

import os
import io
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from PIL import Image, ImageOptim
import requests
from pathlib import Path


class ImageFormat(Enum):
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    SVG = "svg"


class OptimizationLevel(Enum):
    BASIC = "basic"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class ImageOptimizationConfig:
    """Image optimization configuration"""
    quality_jpeg: int = 85
    quality_webp: int = 80
    quality_avif: int = 75
    enable_progressive: bool = True
    strip_metadata: bool = True
    auto_orient: bool = True
    max_width: int = 2560
    max_height: int = 1440
    generate_responsive: bool = True
    responsive_breakpoints: List[int] = None
    enable_lazy_loading: bool = True
    cdn_base_url: Optional[str] = None
    cache_ttl: int = 86400  # 24 hours
    
    def __post_init__(self):
        if self.responsive_breakpoints is None:
            self.responsive_breakpoints = [320, 480, 768, 1024, 1366, 1920]


@dataclass
class OptimizationResult:
    """Image optimization result"""
    original_size: int
    optimized_size: int
    compression_ratio: float
    format_original: str
    format_optimized: str
    width: int
    height: int
    processing_time: float
    generated_variants: List[str]


class ImageOptimizer:
    """
    Advanced image optimizer with format conversion and responsive image generation.
    """
    
    def __init__(self, config: Optional[ImageOptimizationConfig] = None):
        self.config = config or ImageOptimizationConfig()
        self.cache_dir = Path("cache/images")
        self.output_dir = Path("optimized")
        self.optimization_stats = {
            'images_processed': 0,
            'total_size_saved': 0,
            'processing_time': 0.0
        }
        
        # Ensure directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize image processing libraries
        self._init_processors()
    
    def optimize_image(self, image_path: Union[str, Path], 
                      target_format: Optional[ImageFormat] = None,
                      optimization_level: OptimizationLevel = OptimizationLevel.MODERATE) -> OptimizationResult:
        """
        Optimize a single image with comprehensive optimizations.
        """
        import time
        start_time = time.time()
        
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Get original image info
        original_size = image_path.stat().st_size
        
        with Image.open(image_path) as img:
            original_format = img.format.lower()
            original_width, original_height = img.size
            
            # Determine optimal format if not specified
            if target_format is None:
                target_format = self._determine_optimal_format(img)
            
            # Apply optimizations
            optimized_img = self._apply_optimizations(img, optimization_level)
            
            # Generate output filename
            output_filename = self._generate_output_filename(
                image_path, target_format, optimization_level
            )
            output_path = self.output_dir / output_filename
            
            # Save optimized image
            self._save_optimized_image(optimized_img, output_path, target_format)
            
            # Generate responsive variants if enabled
            generated_variants = []
            if self.config.generate_responsive:
                generated_variants = self._generate_responsive_variants(
                    optimized_img, output_path, target_format
                )
            
            # Calculate results
            optimized_size = output_path.stat().st_size
            compression_ratio = (original_size - optimized_size) / original_size
            processing_time = time.time() - start_time
            
            # Update statistics
            self._update_stats(original_size, optimized_size, processing_time)
            
            result = OptimizationResult(
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=compression_ratio,
                format_original=original_format,
                format_optimized=target_format.value,
                width=optimized_img.width,
                height=optimized_img.height,
                processing_time=processing_time,
                generated_variants=generated_variants
            )
            
            logging.info(
                f"Optimized {image_path.name}: "
                f"{original_size} -> {optimized_size} bytes "
                f"({compression_ratio:.1%} reduction)"
            )
            
            return result
    
    def optimize_directory(self, directory_path: Union[str, Path],
                          recursive: bool = True,
                          target_format: Optional[ImageFormat] = None) -> List[OptimizationResult]:
        """
        Optimize all images in a directory.
        """
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Invalid directory: {directory_path}")
        
        results = []
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
        
        # Find all image files
        pattern = "**/*" if recursive else "*"
        for file_path in directory_path.glob(pattern):
            if file_path.suffix.lower() in image_extensions:
                try:
                    result = self.optimize_image(file_path, target_format)
                    results.append(result)
                except Exception as e:
                    logging.error(f"Failed to optimize {file_path}: {e}")
        
        logging.info(f"Optimized {len(results)} images in {directory_path}")
        return results
    
    def generate_responsive_image(self, image_path: Union[str, Path],
                                breakpoints: Optional[List[int]] = None) -> Dict[int, str]:
        """
        Generate responsive image variants for different screen sizes.
        """
        breakpoints = breakpoints or self.config.responsive_breakpoints
        image_path = Path(image_path)
        
        variants = {}
        
        with Image.open(image_path) as img:
            original_width = img.width
            
            for breakpoint in breakpoints:
                if breakpoint >= original_width:
                    continue
                
                # Calculate new dimensions maintaining aspect ratio
                aspect_ratio = img.height / img.width
                new_width = breakpoint
                new_height = int(new_width * aspect_ratio)
                
                # Resize image
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Generate filename
                filename = f"{image_path.stem}_w{new_width}{image_path.suffix}"
                output_path = self.output_dir / filename
                
                # Save variant
                self._save_optimized_image(resized_img, output_path, ImageFormat.WEBP)
                variants[breakpoint] = str(output_path)
        
        return variants
    
    def convert_to_modern_format(self, image_path: Union[str, Path],
                               target_formats: List[ImageFormat] = None) -> Dict[str, str]:
        """
        Convert image to modern formats (WebP, AVIF).
        """
        if target_formats is None:
            target_formats = [ImageFormat.WEBP, ImageFormat.AVIF]
        
        image_path = Path(image_path)
        converted_files = {}
        
        with Image.open(image_path) as img:
            for format_type in target_formats:
                try:
                    output_filename = f"{image_path.stem}.{format_type.value}"
                    output_path = self.output_dir / output_filename
                    
                    self._save_optimized_image(img, output_path, format_type)
                    converted_files[format_type.value] = str(output_path)
                    
                except Exception as e:
                    logging.warning(f"Failed to convert to {format_type.value}: {e}")
        
        return converted_files
    
    def generate_image_metadata(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Generate comprehensive image metadata.
        """
        image_path = Path(image_path)
        
        with Image.open(image_path) as img:
            # Basic image info
            metadata = {
                'filename': image_path.name,
                'format': img.format,
                'mode': img.mode,
                'width': img.width,
                'height': img.height,
                'size_bytes': image_path.stat().st_size,
                'aspect_ratio': img.width / img.height,
                'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
            }
            
            # EXIF data if available
            if hasattr(img, '_getexif') and img._getexif():
                metadata['exif'] = dict(img._getexif().items())
            
            # Color analysis
            colors = img.getcolors(maxcolors=256*256*256)
            if colors:
                metadata['dominant_colors'] = self._analyze_colors(colors)
            
            # Optimization recommendations
            metadata['recommendations'] = self._generate_optimization_recommendations(img)
            
            return metadata
    
    def create_picture_element(self, image_path: Union[str, Path],
                             alt_text: str = "",
                             css_classes: str = "",
                             lazy_loading: bool = None) -> str:
        """
        Generate HTML picture element with responsive sources.
        """
        if lazy_loading is None:
            lazy_loading = self.config.enable_lazy_loading
        
        image_path = Path(image_path)
        
        # Generate responsive variants
        variants = self.generate_responsive_image(image_path)
        
        # Convert to modern formats
        modern_formats = self.convert_to_modern_format(image_path)
        
        # Build picture element
        picture_html = "<picture>\n"
        
        # Add modern format sources
        for format_name, file_path in modern_formats.items():
            picture_html += f'  <source srcset="{file_path}" type="image/{format_name}">\n'
        
        # Add responsive sources
        if variants:
            srcset_webp = ", ".join([
                f"{file_path} {width}w" 
                for width, file_path in variants.items()
            ])
            picture_html += f'  <source srcset="{srcset_webp}" type="image/webp">\n'
        
        # Fallback img element
        loading_attr = 'loading="lazy"' if lazy_loading else ''
        class_attr = f'class="{css_classes}"' if css_classes else ''
        
        picture_html += f'  <img src="{image_path}" alt="{alt_text}" {class_attr} {loading_attr}>\n'
        picture_html += "</picture>"
        
        return picture_html
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive optimization statistics.
        """
        return {
            'images_processed': self.optimization_stats['images_processed'],
            'total_size_saved_mb': self.optimization_stats['total_size_saved'] / (1024 * 1024),
            'average_compression_ratio': self._calculate_average_compression(),
            'total_processing_time': self.optimization_stats['processing_time'],
            'cache_size_mb': self._calculate_cache_size() / (1024 * 1024),
            'supported_formats': [fmt.value for fmt in ImageFormat]
        }
    
    # Private methods
    def _init_processors(self):
        """Initialize image processing libraries"""
        try:
            # Check if optional libraries are available
            import pillow_heif
            pillow_heif.register_heif_opener()
            logging.info("HEIF support enabled")
        except ImportError:
            logging.info("HEIF support not available")
        
        try:
            import pillow_avif
            logging.info("AVIF support enabled")
        except ImportError:
            logging.info("AVIF support not available")
    
    def _determine_optimal_format(self, img: Image.Image) -> ImageFormat:
        """Determine optimal format based on image characteristics"""
        # Check if image has transparency
        has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
        
        # Analyze color complexity
        colors = img.getcolors(maxcolors=256)
        is_simple = colors is not None and len(colors) < 64
        
        # Determine optimal format
        if has_transparency:
            return ImageFormat.WEBP  # WebP handles transparency well
        elif is_simple:
            return ImageFormat.PNG   # PNG for simple graphics
        else:
            return ImageFormat.WEBP  # WebP for complex photos
    
    def _apply_optimizations(self, img: Image.Image, 
                           optimization_level: OptimizationLevel) -> Image.Image:
        """Apply various image optimizations"""
        optimized_img = img.copy()
        
        # Auto-orient based on EXIF
        if self.config.auto_orient:
            try:
                optimized_img = self._auto_orient(optimized_img)
            except Exception as e:
                logging.warning(f"Auto-orient failed: {e}")
        
        # Resize if too large
        if (optimized_img.width > self.config.max_width or 
            optimized_img.height > self.config.max_height):
            optimized_img = self._resize_maintaining_aspect_ratio(
                optimized_img, self.config.max_width, self.config.max_height
            )
        
        # Apply optimization level specific adjustments
        if optimization_level == OptimizationLevel.AGGRESSIVE:
            # More aggressive compression
            optimized_img = self._apply_aggressive_optimizations(optimized_img)
        
        return optimized_img
    
    def _save_optimized_image(self, img: Image.Image, output_path: Path, 
                            format_type: ImageFormat):
        """Save image with format-specific optimizations"""
        save_kwargs = {}
        
        if format_type == ImageFormat.JPEG:
            save_kwargs = {
                'format': 'JPEG',
                'quality': self.config.quality_jpeg,
                'optimize': True,
                'progressive': self.config.enable_progressive
            }
        elif format_type == ImageFormat.PNG:
            save_kwargs = {
                'format': 'PNG',
                'optimize': True
            }
        elif format_type == ImageFormat.WEBP:
            save_kwargs = {
                'format': 'WEBP',
                'quality': self.config.quality_webp,
                'optimize': True,
                'method': 6  # Best compression
            }
        elif format_type == ImageFormat.AVIF:
            save_kwargs = {
                'format': 'AVIF',
                'quality': self.config.quality_avif,
                'speed': 6  # Balance between speed and compression
            }
        
        # Strip metadata if configured
        if self.config.strip_metadata:
            img = self._strip_metadata(img)
        
        img.save(output_path, **save_kwargs)
    
    def _generate_responsive_variants(self, img: Image.Image, base_path: Path,
                                    format_type: ImageFormat) -> List[str]:
        """Generate responsive image variants"""
        variants = []
        original_width = img.width
        
        for breakpoint in self.config.responsive_breakpoints:
            if breakpoint >= original_width:
                continue
            
            # Calculate new dimensions
            aspect_ratio = img.height / img.width
            new_width = breakpoint
            new_height = int(new_width * aspect_ratio)
            
            # Resize image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Generate filename
            variant_filename = f"{base_path.stem}_w{new_width}.{format_type.value}"
            variant_path = base_path.parent / variant_filename
            
            # Save variant
            self._save_optimized_image(resized_img, variant_path, format_type)
            variants.append(str(variant_path))
        
        return variants
    
    def _generate_output_filename(self, original_path: Path, 
                                format_type: ImageFormat,
                                optimization_level: OptimizationLevel) -> str:
        """Generate output filename with optimization indicators"""
        base_name = original_path.stem
        level_suffix = optimization_level.value[0]  # b, m, a
        return f"{base_name}_opt{level_suffix}.{format_type.value}"
    
    def _auto_orient(self, img: Image.Image) -> Image.Image:
        """Auto-orient image based on EXIF data"""
        try:
            from PIL.ExifTags import ORIENTATION
            
            if hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif is not None:
                    orientation = exif.get(ORIENTATION)
                    if orientation:
                        if orientation == 3:
                            img = img.rotate(180, expand=True)
                        elif orientation == 6:
                            img = img.rotate(270, expand=True)
                        elif orientation == 8:
                            img = img.rotate(90, expand=True)
        except Exception as e:
            logging.warning(f"Auto-orientation failed: {e}")
        
        return img
    
    def _resize_maintaining_aspect_ratio(self, img: Image.Image, 
                                       max_width: int, max_height: int) -> Image.Image:
        """Resize image maintaining aspect ratio"""
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return img
    
    def _apply_aggressive_optimizations(self, img: Image.Image) -> Image.Image:
        """Apply aggressive optimizations that may reduce quality"""
        # Reduce color palette for PNG images
        if img.mode == 'RGBA':
            # Convert to palette mode if possible
            try:
                img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
            except Exception:
                pass
        
        return img
    
    def _strip_metadata(self, img: Image.Image) -> Image.Image:
        """Strip EXIF and other metadata from image"""
        # Create new image without metadata
        data = list(img.getdata())
        image_without_exif = Image.new(img.mode, img.size)
        image_without_exif.putdata(data)
        return image_without_exif
    
    def _analyze_colors(self, colors: List[Tuple]) -> List[Dict[str, Any]]:
        """Analyze dominant colors in image"""
        # Sort colors by frequency
        sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
        
        dominant_colors = []
        for count, color in sorted_colors[:5]:  # Top 5 colors
            if isinstance(color, int):
                # Grayscale
                rgb = (color, color, color)
            else:
                rgb = color[:3]  # RGB values
            
            dominant_colors.append({
                'rgb': rgb,
                'hex': f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}",
                'frequency': count
            })
        
        return dominant_colors
    
    def _generate_optimization_recommendations(self, img: Image.Image) -> List[str]:
        """Generate optimization recommendations for image"""
        recommendations = []
        
        # Size recommendations
        if img.width > 2560 or img.height > 1440:
            recommendations.append("Consider reducing image dimensions for web use")
        
        # Format recommendations
        has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
        
        if img.format == 'PNG' and not has_transparency:
            recommendations.append("Consider converting to JPEG for better compression")
        
        if img.format in ('JPEG', 'PNG'):
            recommendations.append("Consider converting to WebP for better compression")
        
        # Quality recommendations
        colors = img.getcolors(maxcolors=256)
        if colors and len(colors) < 16:
            recommendations.append("Image has few colors - consider PNG or reduce quality")
        
        return recommendations
    
    def _update_stats(self, original_size: int, optimized_size: int, processing_time: float):
        """Update optimization statistics"""
        self.optimization_stats['images_processed'] += 1
        self.optimization_stats['total_size_saved'] += (original_size - optimized_size)
        self.optimization_stats['processing_time'] += processing_time
    
    def _calculate_average_compression(self) -> float:
        """Calculate average compression ratio"""
        if self.optimization_stats['images_processed'] == 0:
            return 0.0
        
        # This is simplified - in practice, you'd track individual ratios
        return 0.3  # Placeholder for 30% average compression
    
    def _calculate_cache_size(self) -> int:
        """Calculate total cache size in bytes"""
        total_size = 0
        for file_path in self.cache_dir.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size