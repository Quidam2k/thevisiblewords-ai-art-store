"""
Advanced Image Processing Module
Handles image optimization, validation, and enhancement for Printify uploads
"""

import os
import io
import base64
from typing import Dict, Tuple, Optional, List
from PIL import Image, ImageOps, ImageEnhance, ExifTags
from PIL.ExifTags import TAGS
import logging
from pathlib import Path
from dataclasses import dataclass

@dataclass
class ImageInfo:
    """Information about a processed image"""
    width: int
    height: int
    format: str
    size_bytes: int
    has_exif: bool
    exif_data: Dict
    optimized: bool
    original_size: int

class ImageProcessor:
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        
        # Default settings (can be overridden by config)
        self.max_width = config.get('max_width', 4000) if config else 4000
        self.max_height = config.get('max_height', 4000) if config else 4000
        self.quality = config.get('quality', 90) if config else 90
        self.output_format = config.get('format', 'JPEG') if config else 'JPEG'
        self.optimize = config.get('optimize', True) if config else True
        self.auto_orient = config.get('auto_orient', True) if config else True
        self.strip_metadata = config.get('strip_metadata', False) if config else False
        
        # Supported formats
        self.supported_formats = {'JPEG', 'PNG', 'WEBP', 'BMP', 'TIFF'}
        
        # Print area requirements for different product types
        self.print_requirements = {
            'tshirt': {'min_width': 2400, 'min_height': 2400, 'dpi': 300},
            'poster': {'min_width': 3000, 'min_height': 3000, 'dpi': 300},
            'mug': {'min_width': 2000, 'min_height': 1200, 'dpi': 300},
            'canvas': {'min_width': 3600, 'min_height': 3600, 'dpi': 300},
            'phone_case': {'min_width': 1800, 'min_height': 3200, 'dpi': 300}
        }

    def extract_comprehensive_exif(self, image_path: str) -> Dict:
        """Extract comprehensive EXIF data including AI prompts"""
        exif_data = {}
        
        try:
            with Image.open(image_path) as img:
                # Get basic EXIF
                if hasattr(img, '_getexif') and img._getexif():
                    raw_exif = img._getexif()
                    
                    for tag_id, value in raw_exif.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        exif_data[tag_name] = value
                
                # Look for AI-specific metadata
                ai_metadata = self._extract_ai_metadata(img)
                if ai_metadata:
                    exif_data.update(ai_metadata)
                    
        except Exception as e:
            self.logger.warning(f"Could not extract EXIF from {image_path}: {e}")
        
        return exif_data

    def _extract_ai_metadata(self, img: Image.Image) -> Dict:
        """Extract AI-specific metadata from various sources"""
        ai_data = {}
        
        # Common AI prompt fields
        prompt_fields = [
            'ImageDescription', 'UserComment', 'XPComment', 'Description',
            'prompt', 'parameters', 'workflow', 'software', 'model'
        ]
        
        # Check image info for PNG text chunks (common in AI generated images)
        if hasattr(img, 'text'):
            for key, value in img.text.items():
                if any(field.lower() in key.lower() for field in prompt_fields):
                    ai_data[f'ai_{key.lower()}'] = value
        
        # Check for specific AI tools metadata
        if hasattr(img, 'app'):
            for key in img.app.keys():
                if 'prompt' in key.lower() or 'param' in key.lower():
                    ai_data[f'ai_{key}'] = img.app[key]
        
        return ai_data

    def extract_prompt_from_image(self, image_path: str) -> str:
        """Extract AI prompt from image metadata with fallback strategies"""
        exif_data = self.extract_comprehensive_exif(image_path)
        
        # Priority order for prompt extraction
        prompt_sources = [
            'ImageDescription', 'ai_prompt', 'ai_parameters', 'UserComment',
            'XPComment', 'Description', 'Software', 'ai_workflow'
        ]
        
        for source in prompt_sources:
            if source in exif_data and exif_data[source]:
                prompt = str(exif_data[source])
                if len(prompt.strip()) > 10:  # Meaningful prompt
                    return prompt.strip()
        
        # Fallback: check filename for prompts
        filename = Path(image_path).stem
        if len(filename) > 20 and any(word in filename.lower() for word in 
                                    ['art', 'paint', 'draw', 'style', 'color']):
            return filename.replace('_', ' ').replace('-', ' ')
        
        return "AI generated artwork"

    def validate_image(self, image_path: str, product_type: str = 'tshirt') -> Tuple[bool, List[str]]:
        """Validate image meets requirements for specified product type"""
        issues = []
        
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                
                # Check format
                if img.format not in self.supported_formats:
                    issues.append(f"Unsupported format: {img.format}")
                
                # Check requirements for product type
                if product_type in self.print_requirements:
                    req = self.print_requirements[product_type]
                    
                    if width < req['min_width']:
                        issues.append(f"Width {width}px below minimum {req['min_width']}px")
                    
                    if height < req['min_height']:
                        issues.append(f"Height {height}px below minimum {req['min_height']}px")
                
                # Check file size (Printify limit is typically 50MB)
                file_size = os.path.getsize(image_path)
                if file_size > 50 * 1024 * 1024:  # 50MB
                    issues.append(f"File size {file_size/1024/1024:.1f}MB exceeds 50MB limit")
                
                # Check for corrupted image
                try:
                    img.verify()
                except Exception:
                    issues.append("Image appears to be corrupted")
        
        except Exception as e:
            issues.append(f"Cannot open image: {e}")
        
        return len(issues) == 0, issues

    def optimize_image(self, image_path: str, output_path: str = None) -> Tuple[str, ImageInfo]:
        """Optimize image for Printify upload"""
        if output_path is None:
            path = Path(image_path)
            output_path = path.parent / f"{path.stem}_optimized{path.suffix}"
        
        original_size = os.path.getsize(image_path)
        
        with Image.open(image_path) as img:
            # Store original info
            original_width, original_height = img.size
            original_format = img.format
            
            # Auto-orient based on EXIF
            if self.auto_orient:
                img = ImageOps.exif_transpose(img)
            
            # Convert to RGB if necessary (for JPEG output)
            if self.output_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Resize if necessary
            if img.size[0] > self.max_width or img.size[1] > self.max_height:
                img.thumbnail((self.max_width, self.max_height), Image.Resampling.LANCZOS)
                self.logger.info(f"Resized image from {original_width}x{original_height} to {img.size}")
            
            # Enhance image quality
            img = self._enhance_image_quality(img)
            
            # Prepare save parameters
            save_kwargs = {
                'format': self.output_format,
                'optimize': self.optimize,
                'quality': self.quality
            }
            
            # Preserve EXIF if not stripping metadata
            if not self.strip_metadata and hasattr(img, '_getexif') and img._getexif():
                save_kwargs['exif'] = img.info.get('exif', b'')
            
            # Save optimized image
            img.save(output_path, **save_kwargs)
        
        # Gather info about processed image
        optimized_size = os.path.getsize(output_path)
        
        with Image.open(output_path) as optimized_img:
            info = ImageInfo(
                width=optimized_img.size[0],
                height=optimized_img.size[1],
                format=optimized_img.format,
                size_bytes=optimized_size,
                has_exif=bool(self.extract_comprehensive_exif(output_path)),
                exif_data=self.extract_comprehensive_exif(output_path),
                optimized=True,
                original_size=original_size
            )
        
        compression_ratio = (1 - optimized_size / original_size) * 100
        self.logger.info(f"Optimized image: {compression_ratio:.1f}% size reduction")
        
        return str(output_path), info

    def _enhance_image_quality(self, img: Image.Image) -> Image.Image:
        """Apply subtle enhancements to improve image quality"""
        try:
            # Slight sharpening for digital art
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            # Slight contrast enhancement
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.05)
            
            # Slight color enhancement
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.02)
            
        except Exception as e:
            self.logger.warning(f"Could not enhance image: {e}")
        
        return img

    def convert_to_base64(self, image_path: str) -> str:
        """Convert image to base64 string for API upload"""
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Failed to convert image to base64: {e}")
            raise

    def create_thumbnail(self, image_path: str, size: Tuple[int, int] = (300, 300)) -> str:
        """Create a thumbnail for preview purposes"""
        path = Path(image_path)
        thumbnail_path = path.parent / f"{path.stem}_thumb{path.suffix}"
        
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, optimize=True, quality=85)
        
        return str(thumbnail_path)

    def get_optimal_print_size(self, image_width: int, image_height: int, 
                              product_type: str = 'tshirt') -> Dict[str, float]:
        """Calculate optimal print size for given image dimensions"""
        if product_type not in self.print_requirements:
            return {"width_inches": 10, "height_inches": 10, "dpi": 300}
        
        req = self.print_requirements[product_type]
        target_dpi = req['dpi']
        
        # Calculate print dimensions at target DPI
        width_inches = image_width / target_dpi
        height_inches = image_height / target_dpi
        
        # Common print size constraints
        max_sizes = {
            'tshirt': (12, 16),  # inches
            'poster': (24, 36),
            'mug': (8.5, 3.5),
            'canvas': (24, 24),
            'phone_case': (3, 6)
        }
        
        if product_type in max_sizes:
            max_w, max_h = max_sizes[product_type]
            
            # Scale down if necessary while maintaining aspect ratio
            if width_inches > max_w or height_inches > max_h:
                scale = min(max_w / width_inches, max_h / height_inches)
                width_inches *= scale
                height_inches *= scale
        
        return {
            "width_inches": round(width_inches, 2),
            "height_inches": round(height_inches, 2),
            "dpi": target_dpi,
            "scale_factor": 1.0
        }

    def batch_process_images(self, image_paths: List[str], 
                           output_dir: str = None) -> List[Tuple[str, ImageInfo]]:
        """Process multiple images in batch"""
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for image_path in image_paths:
            try:
                if output_dir:
                    filename = Path(image_path).name
                    output_path = Path(output_dir) / filename
                else:
                    output_path = None
                
                optimized_path, info = self.optimize_image(image_path, str(output_path))
                results.append((optimized_path, info))
                
            except Exception as e:
                self.logger.error(f"Failed to process {image_path}: {e}")
                results.append((None, None))
        
        return results

# Example usage
if __name__ == "__main__":
    processor = ImageProcessor()
    
    # Test with a sample image (replace with actual path)
    test_image = "test_image.jpg"
    
    if os.path.exists(test_image):
        # Validate image
        is_valid, issues = processor.validate_image(test_image)
        print(f"Image valid: {is_valid}")
        if issues:
            for issue in issues:
                print(f"  - {issue}")
        
        # Extract prompt
        prompt = processor.extract_prompt_from_image(test_image)
        print(f"Extracted prompt: {prompt}")
        
        # Optimize image
        optimized_path, info = processor.optimize_image(test_image)
        print(f"Optimized image saved to: {optimized_path}")
        print(f"Original size: {info.original_size} bytes")
        print(f"Optimized size: {info.size_bytes} bytes")
        print(f"Compression: {(1 - info.size_bytes / info.original_size) * 100:.1f}%")
    else:
        print("No test image found")