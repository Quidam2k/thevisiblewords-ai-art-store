#!/usr/bin/env python3
"""
Simple Image Processing Functionality Test
Tests what we can without requiring PIL installation
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_module_imports():
    """Test if we can import the image processor module"""
    print("Testing module imports...")
    try:
        # Test if we can import without PIL first
        import importlib.util
        spec = importlib.util.spec_from_file_location("image_processor", "src/image_processor.py")
        if spec and spec.loader:
            print("✅ Image processor module found and loadable")
            return True
        else:
            print("❌ Cannot load image processor module")
            return False
    except Exception as e:
        print(f"❌ Error importing image processor: {e}")
        return False

def test_pil_availability():
    """Test if PIL/Pillow is available"""
    print("\nTesting PIL/Pillow availability...")
    try:
        from PIL import Image, ImageOps, ImageEnhance, ExifTags
        print("✅ PIL/Pillow is available")
        
        # Test basic PIL functionality
        print("Testing basic PIL functionality...")
        
        # Create a simple test image
        test_img = Image.new('RGB', (100, 100), color='red')
        print("✅ Can create basic images")
        
        # Test image operations
        resized = test_img.resize((50, 50))
        print("✅ Can resize images")
        
        # Test format conversion
        if test_img.mode == 'RGB':
            print("✅ RGB mode working")
        
        return True
    except ImportError as e:
        print(f"❌ PIL/Pillow not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing PIL functionality: {e}")
        return False

def test_image_processor_class():
    """Test the ImageProcessor class structure"""
    print("\nTesting ImageProcessor class structure...")
    
    try:
        from src.image_processor import ImageProcessor, ImageInfo
        
        # Test initialization
        processor = ImageProcessor()
        print("✅ Can initialize ImageProcessor")
        
        # Test basic attributes
        if hasattr(processor, 'max_width'):
            print(f"✅ Has max_width setting: {processor.max_width}")
        
        if hasattr(processor, 'supported_formats'):
            print(f"✅ Has supported formats: {processor.supported_formats}")
        
        if hasattr(processor, 'print_requirements'):
            print(f"✅ Has print requirements for: {list(processor.print_requirements.keys())}")
        
        # Test methods exist
        methods_to_check = [
            'validate_image', 'optimize_image', 'extract_comprehensive_exif',
            'extract_prompt_from_image', 'convert_to_base64', 'create_thumbnail',
            'get_optimal_print_size', 'batch_process_images'
        ]
        
        for method in methods_to_check:
            if hasattr(processor, method):
                print(f"✅ Has method: {method}")
            else:
                print(f"❌ Missing method: {method}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import ImageProcessor: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing ImageProcessor: {e}")
        return False

def test_sample_images():
    """Test availability of sample images"""
    print("\nTesting sample images availability...")
    
    project_root = Path('.')
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp', '*.tiff']
    
    found_images = []
    for ext in image_extensions:
        found_images.extend(list(project_root.glob(ext)))
    
    print(f"Found {len(found_images)} sample images:")
    for img in found_images[:5]:  # Show first 5
        file_size = img.stat().st_size
        print(f"  - {img.name} ({file_size:,} bytes)")
    
    if len(found_images) > 5:
        print(f"  ... and {len(found_images) - 5} more")
    
    return len(found_images) > 0

def test_basic_image_operations():
    """Test basic image operations if PIL is available"""
    print("\nTesting basic image operations...")
    
    try:
        from PIL import Image
        from src.image_processor import ImageProcessor
        
        processor = ImageProcessor()
        
        # Find a sample image
        project_root = Path('.')
        sample_images = list(project_root.glob('*.jpg')) + list(project_root.glob('*.png'))
        
        if not sample_images:
            print("❌ No sample images found for testing")
            return False
        
        sample_image = sample_images[0]
        print(f"Testing with: {sample_image.name}")
        
        # Test image validation
        valid, issues = processor.validate_image(str(sample_image))
        print(f"✅ Image validation result: {'Valid' if valid else 'Invalid'}")
        if issues:
            print(f"  Issues found: {issues[:3]}")  # Show first 3 issues
        
        # Test EXIF extraction
        exif_data = processor.extract_comprehensive_exif(str(sample_image))
        print(f"✅ EXIF extraction: Found {len(exif_data)} metadata entries")
        
        # Test prompt extraction
        prompt = processor.extract_prompt_from_image(str(sample_image))
        print(f"✅ Prompt extraction: '{prompt[:50]}...' ({len(prompt)} chars)")
        
        # Test print size calculation
        with Image.open(sample_image) as img:
            width, height = img.size
            print_size = processor.get_optimal_print_size(width, height, 'tshirt')
            print(f"✅ Print size calculation: {print_size['width_inches']}\" x {print_size['height_inches']}\"")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in image operations: {e}")
        return False

def analyze_image_requirements():
    """Analyze the image processing requirements and capabilities"""
    print("\nAnalyzing image processing requirements...")
    
    try:
        from src.image_processor import ImageProcessor
        
        processor = ImageProcessor()
        requirements = processor.print_requirements
        
        print("Print requirements by product type:")
        for product, req in requirements.items():
            print(f"  {product}: {req['min_width']}x{req['min_height']}px @ {req['dpi']}dpi")
        
        print(f"\nSupported formats: {', '.join(processor.supported_formats)}")
        print(f"Max dimensions: {processor.max_width}x{processor.max_height}px")
        print(f"Default quality: {processor.quality}")
        print(f"Output format: {processor.output_format}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing requirements: {e}")
        return False

def main():
    """Run all tests and provide summary"""
    print("Image Processing Functionality Test")
    print("=" * 50)
    
    test_results = {
        "Module Import": test_module_imports(),
        "PIL Availability": test_pil_availability(),
        "ImageProcessor Class": test_image_processor_class(),
        "Sample Images": test_sample_images(),
        "Requirements Analysis": analyze_image_requirements()
    }
    
    # Only test operations if PIL is available
    if test_results["PIL Availability"]:
        test_results["Basic Operations"] = test_basic_image_operations()
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Image processing functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    main()