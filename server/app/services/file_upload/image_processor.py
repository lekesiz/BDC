"""Image processing and sanitization module."""

import os
import io
from typing import Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter
from PIL.ExifTags import TAGS
import pillow_heif
import logging

from .config import FileUploadConfig
from .exceptions import ImageProcessingException

logger = logging.getLogger(__name__)

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()


class ImageProcessor:
    """Processes and sanitizes images for secure storage."""
    
    def __init__(self, config: FileUploadConfig):
        self.config = config
        
    def process_image(self, file_path: str, output_path: str) -> Dict[str, any]:
        """
        Process and sanitize an image file.
        
        Args:
            file_path: Path to input image
            output_path: Path for processed image
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Open and validate image
            img = self._open_and_validate_image(file_path)
            
            # Extract metadata before processing
            metadata = self._extract_metadata(img)
            
            # Strip EXIF data if configured
            if self.config.STRIP_EXIF_DATA:
                img = self._strip_exif_data(img)
            
            # Resize if needed
            img = self._resize_if_needed(img)
            
            # Convert to safe format
            img = self._convert_to_safe_format(img)
            
            # Save processed image
            self._save_image(img, output_path)
            
            # Generate thumbnails
            thumbnails = self._generate_thumbnails(img, output_path)
            
            return {
                'original_path': file_path,
                'processed_path': output_path,
                'original_metadata': metadata,
                'size': img.size,
                'format': img.format,
                'mode': img.mode,
                'thumbnails': thumbnails
            }
            
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {str(e)}")
            raise ImageProcessingException(f"Image processing failed: {str(e)}")
    
    def _open_and_validate_image(self, file_path: str) -> Image.Image:
        """Open and validate image file."""
        try:
            img = Image.open(file_path)
            
            # Verify it's actually an image
            img.verify()
            
            # Reopen after verify (verify closes the file)
            img = Image.open(file_path)
            
            # Check for decompression bombs
            Image.MAX_IMAGE_PIXELS = 178956970  # ~178 megapixels
            
            return img
            
        except Image.DecompressionBombError:
            raise ImageProcessingException("Image size is suspiciously large")
        except Exception as e:
            raise ImageProcessingException(f"Failed to open image: {str(e)}")
    
    def _extract_metadata(self, img: Image.Image) -> Dict[str, any]:
        """Extract metadata from image."""
        metadata = {
            'format': img.format,
            'mode': img.mode,
            'size': img.size,
            'info': {}
        }
        
        # Extract EXIF data
        if hasattr(img, '_getexif') and img._getexif():
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    # Convert bytes to string for JSON serialization
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)
                    metadata['info'][tag_name] = value
        
        return metadata
    
    def _strip_exif_data(self, img: Image.Image) -> Image.Image:
        """Remove EXIF data from image."""
        # Create a new image without EXIF data
        data = list(img.getdata())
        img_without_exif = Image.new(img.mode, img.size)
        img_without_exif.putdata(data)
        
        # Preserve rotation information
        if hasattr(img, '_getexif') and img._getexif():
            exif = img._getexif()
            if exif and 274 in exif:  # Orientation tag
                orientation = exif[274]
                if orientation == 3:
                    img_without_exif = img_without_exif.rotate(180, expand=True)
                elif orientation == 6:
                    img_without_exif = img_without_exif.rotate(270, expand=True)
                elif orientation == 8:
                    img_without_exif = img_without_exif.rotate(90, expand=True)
        
        return img_without_exif
    
    def _resize_if_needed(self, img: Image.Image) -> Image.Image:
        """Resize image if it exceeds maximum dimensions."""
        max_dim = self.config.MAX_IMAGE_DIMENSION
        
        if img.width > max_dim or img.height > max_dim:
            # Calculate new dimensions maintaining aspect ratio
            ratio = min(max_dim / img.width, max_dim / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            
            # Use high-quality resampling
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
        return img
    
    def _convert_to_safe_format(self, img: Image.Image) -> Image.Image:
        """Convert image to a safe format."""
        # Convert RGBA to RGB if saving as JPEG
        if img.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        return img
    
    def _save_image(self, img: Image.Image, output_path: str):
        """Save processed image."""
        # Determine format based on output path
        _, ext = os.path.splitext(output_path)
        format_map = {
            '.jpg': 'JPEG',
            '.jpeg': 'JPEG',
            '.png': 'PNG',
            '.webp': 'WebP'
        }
        
        save_format = format_map.get(ext.lower(), 'JPEG')
        
        # Save with optimization
        save_kwargs = {
            'format': save_format,
            'optimize': True,
            'quality': 85
        }
        
        if save_format == 'PNG':
            save_kwargs['compress_level'] = 9
        elif save_format == 'WebP':
            save_kwargs['quality'] = 80
            save_kwargs['method'] = 6
        
        img.save(output_path, **save_kwargs)
    
    def _generate_thumbnails(self, img: Image.Image, base_path: str) -> Dict[str, str]:
        """Generate thumbnails of various sizes."""
        thumbnails = {}
        base_dir = os.path.dirname(base_path)
        base_name = os.path.splitext(os.path.basename(base_path))[0]
        
        for size_name, dimensions in self.config.THUMBNAIL_SIZES.items():
            # Create thumbnail
            thumb = img.copy()
            thumb.thumbnail(dimensions, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            thumb_filename = f"{base_name}_thumb_{size_name}.jpg"
            thumb_path = os.path.join(base_dir, thumb_filename)
            
            thumb.save(thumb_path, 'JPEG', optimize=True, quality=85)
            thumbnails[size_name] = thumb_path
        
        return thumbnails
    
    def add_watermark(self, img_path: str, watermark_text: str, 
                     output_path: Optional[str] = None) -> str:
        """Add a watermark to an image."""
        try:
            img = Image.open(img_path)
            
            # Create a drawing context
            draw = ImageDraw.Draw(img)
            
            # Calculate watermark position (bottom right)
            text_width = len(watermark_text) * 10  # Approximate
            text_height = 20
            x = img.width - text_width - 10
            y = img.height - text_height - 10
            
            # Add semi-transparent watermark
            draw.text((x, y), watermark_text, fill=(255, 255, 255, 128))
            
            # Save watermarked image
            if output_path is None:
                output_path = img_path
            
            img.save(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Error adding watermark: {str(e)}")
            raise ImageProcessingException(f"Failed to add watermark: {str(e)}")
    
    def blur_sensitive_areas(self, img_path: str, areas: list, 
                           output_path: Optional[str] = None) -> str:
        """
        Blur specific areas of an image.
        
        Args:
            img_path: Path to image
            areas: List of (x, y, width, height) tuples defining areas to blur
            output_path: Output path for blurred image
        """
        try:
            img = Image.open(img_path)
            
            for x, y, width, height in areas:
                # Extract the area
                area = img.crop((x, y, x + width, y + height))
                
                # Apply blur
                blurred = area.filter(ImageFilter.GaussianBlur(radius=10))
                
                # Paste back
                img.paste(blurred, (x, y))
            
            # Save blurred image
            if output_path is None:
                output_path = img_path
            
            img.save(output_path)
            return output_path
            
        except Exception as e:
            logger.error(f"Error blurring image: {str(e)}")
            raise ImageProcessingException(f"Failed to blur image: {str(e)}")