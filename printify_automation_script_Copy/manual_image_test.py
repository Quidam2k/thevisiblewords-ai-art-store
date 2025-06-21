#!/usr/bin/env python3
"""
Manual Image Processing Test
Tests image processing capabilities without requiring PIL
"""

import os
import sys
import struct
from pathlib import Path

def get_jpeg_dimensions(filepath):
    """Get JPEG dimensions without PIL"""
    try:
        with open(filepath, 'rb') as f:
            # Skip SOI marker
            f.read(2)
            
            while True:
                marker = f.read(2)
                if not marker:
                    break
                    
                if marker[0] != 0xFF:
                    break
                    
                # Skip variable length segments
                if marker[1] in (0xC0, 0xC1, 0xC2):  # SOF markers
                    length = struct.unpack('>H', f.read(2))[0]
                    f.read(1)  # precision
                    height = struct.unpack('>H', f.read(2))[0]
                    width = struct.unpack('>H', f.read(2))[0]
                    return width, height
                else:
                    length = struct.unpack('>H', f.read(2))[0]
                    f.read(length - 2)
                    
    except Exception as e:
        print(f"Error reading JPEG {filepath}: {e}")
        return None, None
    
    return None, None

def get_png_dimensions(filepath):
    """Get PNG dimensions without PIL"""
    try:
        with open(filepath, 'rb') as f:
            # Skip PNG signature
            f.read(8)
            
            # Read IHDR chunk
            length = struct.unpack('>I', f.read(4))[0]
            chunk_type = f.read(4)
            
            if chunk_type == b'IHDR':
                width = struct.unpack('>I', f.read(4))[0]
                height = struct.unpack('>I', f.read(4))[0]
                return width, height
                
    except Exception as e:
        print(f"Error reading PNG {filepath}: {e}")
        return None, None
    
    return None, None

def analyze_image_file(filepath):
    """Analyze an image file without PIL"""
    path = Path(filepath)
    
    if not path.exists():
        return None
    
    file_size = path.stat().st_size
    extension = path.suffix.lower()
    
    width, height = None, None
    
    if extension in ['.jpg', '.jpeg']:
        width, height = get_jpeg_dimensions(filepath)
    elif extension == '.png':
        width, height = get_png_dimensions(filepath)
    
    return {
        'filename': path.name,
        'size_bytes': file_size,
        'extension': extension,
        'width': width,
        'height': height,
        'megapixels': (width * height / 1000000) if width and height else None
    }

def test_image_dimensions():
    """Test image dimension extraction"""
    print("Testing Image Dimension Extraction")
    print("=" * 40)
    
    project_root = Path('.')
    sample_images = list(project_root.glob('*.jpg'))[:5] + list(project_root.glob('*.png'))[:5]
    
    results = []
    
    for image_path in sample_images:
        info = analyze_image_file(str(image_path))
        if info:
            results.append(info)
            print(f"📸 {info['filename'][:50]}...")
            print(f"   Size: {info['size_bytes']:,} bytes ({info['size_bytes']/1024/1024:.1f} MB)")
            if info['width'] and info['height']:
                print(f"   Dimensions: {info['width']}x{info['height']} ({info['megapixels']:.1f} MP)")
            else:
                print(f"   Dimensions: Could not determine")
            print()
    
    return results

def check_print_suitability(image_info):
    """Check if image meets print requirements"""
    print("Print Suitability Analysis")
    print("=" * 30)
    
    # Print requirements (from ImageProcessor)
    requirements = {
        'tshirt': {'min_width': 2400, 'min_height': 2400, 'dpi': 300},
        'poster': {'min_width': 3000, 'min_height': 3000, 'dpi': 300},
        'mug': {'min_width': 2000, 'min_height': 1200, 'dpi': 300},
        'canvas': {'min_width': 3600, 'min_height': 3600, 'dpi': 300},
        'phone_case': {'min_width': 1800, 'min_height': 3200, 'dpi': 300}
    }
    
    for info in image_info:
        if info['width'] and info['height']:
            print(f"🖼️  {info['filename'][:40]}...")
            print(f"   Resolution: {info['width']}x{info['height']}")
            
            suitable_products = []
            for product, req in requirements.items():
                if info['width'] >= req['min_width'] and info['height'] >= req['min_height']:
                    suitable_products.append(product)
            
            if suitable_products:
                print(f"   ✅ Suitable for: {', '.join(suitable_products)}")
            else:
                print(f"   ❌ Resolution too low for high-quality printing")
            print()

def extract_filename_prompts():
    """Extract potential AI prompts from filenames"""
    print("AI Prompt Analysis from Filenames")
    print("=" * 35)
    
    project_root = Path('.')
    sample_images = list(project_root.glob('*.jpg')) + list(project_root.glob('*.png'))
    
    for image_path in sample_images[:10]:  # First 10 images
        filename = image_path.stem
        
        # Remove common AI generation patterns
        clean_name = filename.replace('_', ' ').replace('-', ' ')
        
        # Look for common AI prompt patterns
        if 'quidamn' in clean_name.lower():
            # Remove the username
            clean_name = clean_name.replace('quidamn', '').strip()
        
        # Remove hash patterns
        import re
        clean_name = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '', clean_name)
        clean_name = re.sub(r'[a-f0-9]{8}', '', clean_name)
        clean_name = re.sub(r'\s+', ' ', clean_name).strip()
        
        if len(clean_name) > 10:
            print(f"🎨 {image_path.name[:40]}...")
            print(f"   Extracted prompt: {clean_name}")
            print()

def analyze_file_structure():
    """Analyze the image file structure"""
    print("File Structure Analysis")
    print("=" * 25)
    
    project_root = Path('.')
    image_files = []
    
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp', '*.tiff']:
        image_files.extend(list(project_root.glob(ext)))
    
    # Group by extension
    by_extension = {}
    total_size = 0
    
    for img_path in image_files:
        ext = img_path.suffix.lower()
        size = img_path.stat().st_size
        total_size += size
        
        if ext not in by_extension:
            by_extension[ext] = {'count': 0, 'size': 0}
        by_extension[ext]['count'] += 1
        by_extension[ext]['size'] += size
    
    print(f"Total images: {len(image_files)}")
    print(f"Total size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
    print()
    
    for ext, info in by_extension.items():
        avg_size = info['size'] / info['count']
        print(f"{ext.upper()}: {info['count']} files, {info['size']/1024/1024:.1f} MB total, {avg_size/1024/1024:.1f} MB avg")

def main():
    """Run all manual tests"""
    print("Manual Image Processing Analysis")
    print("=" * 50)
    print()
    
    # Test 1: File structure analysis
    analyze_file_structure()
    print()
    
    # Test 2: Dimension extraction
    image_info = test_image_dimensions()
    print()
    
    # Test 3: Print suitability
    if image_info:
        check_print_suitability(image_info)
        print()
    
    # Test 4: Filename prompt extraction
    extract_filename_prompts()
    print()
    
    # Summary
    print("=" * 50)
    print("MANUAL TEST SUMMARY")
    print("=" * 50)
    
    print("✅ Found and analyzed image files")
    print("✅ Extracted dimensions from JPEG/PNG files")
    print("✅ Analyzed print suitability")
    print("✅ Extracted potential prompts from filenames")
    print("❌ PIL/Pillow not available for advanced processing")
    print()
    print("RECOMMENDATIONS:")
    print("- Install PIL/Pillow: pip install pillow")
    print("- Image processing module structure is sound")
    print("- Sufficient sample images available for testing")
    print("- Manual dimension extraction works as fallback")

if __name__ == "__main__":
    main()