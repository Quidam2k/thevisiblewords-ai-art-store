"""
Comprehensive tests for the ImageProcessor module
Tests image processing functionality including optimization, validation, and EXIF handling
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from PIL import Image, ImageDraw
    from image_processor import ImageProcessor, ImageInfo
    PILLOW_AVAILABLE = True
except ImportError as e:
    print(f"PIL/Pillow not available: {e}")
    PILLOW_AVAILABLE = False

class TestImageProcessor(unittest.TestCase):
    """Test suite for ImageProcessor functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        if not PILLOW_AVAILABLE:
            cls.skipTest(cls, "PIL/Pillow not available")
        
        cls.test_dir = tempfile.mkdtemp()
        cls.processor = ImageProcessor()
        
        # Create test images
        cls.test_images = {}
        cls._create_test_images()
        
        # Find real sample images from the project
        cls.sample_images = []
        project_root = Path(__file__).parent.parent
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            cls.sample_images.extend(list(project_root.glob(ext)))
    
    @classmethod
    def _create_test_images(cls):
        """Create various test images for testing"""
        # Create a simple RGB image
        rgb_img = Image.new('RGB', (1000, 1000), color='red')
        rgb_path = os.path.join(cls.test_dir, 'test_rgb.jpg')
        rgb_img.save(rgb_path, 'JPEG')
        cls.test_images['rgb'] = rgb_path
        
        # Create a RGBA image (with transparency)
        rgba_img = Image.new('RGBA', (800, 600), color=(0, 255, 0, 128))
        rgba_path = os.path.join(cls.test_dir, 'test_rgba.png')
        rgba_img.save(rgba_path, 'PNG')
        cls.test_images['rgba'] = rgba_path
        
        # Create a large image
        large_img = Image.new('RGB', (5000, 5000), color='blue')
        large_path = os.path.join(cls.test_dir, 'test_large.jpg')
        large_img.save(large_path, 'JPEG')
        cls.test_images['large'] = large_path
        
        # Create a small image
        small_img = Image.new('RGB', (100, 100), color='yellow')
        small_path = os.path.join(cls.test_dir, 'test_small.jpg')
        small_img.save(small_path, 'JPEG')
        cls.test_images['small'] = small_path
    
    def test_image_processor_initialization(self):
        """Test ImageProcessor initialization with different configs"""
        # Test default initialization
        processor = ImageProcessor()
        self.assertEqual(processor.max_width, 4000)
        self.assertEqual(processor.max_height, 4000)
        self.assertEqual(processor.quality, 90)
        
        # Test with custom config
        config = {
            'max_width': 2000,
            'max_height': 2000,
            'quality': 85,
            'format': 'PNG'
        }
        processor = ImageProcessor(config)
        self.assertEqual(processor.max_width, 2000)
        self.assertEqual(processor.max_height, 2000)
        self.assertEqual(processor.quality, 85)
        self.assertEqual(processor.output_format, 'PNG')
    
    def test_image_validation(self):
        """Test image validation functionality"""
        # Test valid image
        valid, issues = self.processor.validate_image(self.test_images['rgb'])
        self.assertTrue(valid)
        self.assertEqual(len(issues), 0)
        
        # Test small image against print requirements
        valid, issues = self.processor.validate_image(self.test_images['small'], 'tshirt')
        self.assertFalse(valid)
        self.assertTrue(any('Width' in issue for issue in issues))
        self.assertTrue(any('Height' in issue for issue in issues))
        
        # Test non-existent image
        valid, issues = self.processor.validate_image('nonexistent.jpg')
        self.assertFalse(valid)
        self.assertTrue(len(issues) > 0)
    
    def test_image_optimization(self):
        """Test image optimization functionality"""
        # Test RGB image optimization
        output_path, info = self.processor.optimize_image(self.test_images['rgb'])
        
        self.assertTrue(os.path.exists(output_path))
        self.assertIsInstance(info, ImageInfo)
        self.assertEqual(info.width, 1000)
        self.assertEqual(info.height, 1000)
        self.assertTrue(info.optimized)
        
        # Test large image resizing
        output_path, info = self.processor.optimize_image(self.test_images['large'])
        
        self.assertTrue(os.path.exists(output_path))
        self.assertLessEqual(info.width, self.processor.max_width)
        self.assertLessEqual(info.height, self.processor.max_height)
        
        # Test RGBA to RGB conversion
        output_path, info = self.processor.optimize_image(self.test_images['rgba'])
        
        self.assertTrue(os.path.exists(output_path))
        # Should be converted to RGB format
        with Image.open(output_path) as img:
            self.assertEqual(img.mode, 'RGB')
    
    def test_exif_extraction(self):
        """Test EXIF data extraction"""
        # Test with image that has no EXIF
        exif_data = self.processor.extract_comprehensive_exif(self.test_images['rgb'])
        self.assertIsInstance(exif_data, dict)
        
        # Test with real sample images (may have EXIF)
        if self.sample_images:
            for sample_path in self.sample_images[:3]:  # Test first 3 images
                exif_data = self.processor.extract_comprehensive_exif(str(sample_path))
                self.assertIsInstance(exif_data, dict)
    
    def test_prompt_extraction(self):
        """Test AI prompt extraction from images"""
        # Test with regular image (should return default)
        prompt = self.processor.extract_prompt_from_image(self.test_images['rgb'])
        self.assertIsInstance(prompt, str)
        
        # Test with sample images (AI generated images with prompts in filenames)
        if self.sample_images:
            for sample_path in self.sample_images[:3]:
                prompt = self.processor.extract_prompt_from_image(str(sample_path))
                self.assertIsInstance(prompt, str)
                self.assertGreater(len(prompt), 0)
    
    def test_base64_conversion(self):
        """Test base64 conversion functionality"""
        base64_data = self.processor.convert_to_base64(self.test_images['rgb'])
        
        self.assertIsInstance(base64_data, str)
        self.assertGreater(len(base64_data), 0)
        
        # Verify it's valid base64
        import base64
        try:
            decoded = base64.b64decode(base64_data)
            self.assertGreater(len(decoded), 0)
        except Exception:
            self.fail("Failed to decode base64 data")
    
    def test_thumbnail_creation(self):
        """Test thumbnail creation"""
        thumbnail_path = self.processor.create_thumbnail(self.test_images['rgb'])
        
        self.assertTrue(os.path.exists(thumbnail_path))
        
        with Image.open(thumbnail_path) as thumb:
            self.assertLessEqual(thumb.size[0], 300)
            self.assertLessEqual(thumb.size[1], 300)
    
    def test_optimal_print_size_calculation(self):
        """Test optimal print size calculations"""
        # Test with 3000x3000 image for t-shirt
        result = self.processor.get_optimal_print_size(3000, 3000, 'tshirt')
        
        self.assertIn('width_inches', result)
        self.assertIn('height_inches', result)
        self.assertIn('dpi', result)
        self.assertEqual(result['dpi'], 300)
        self.assertGreater(result['width_inches'], 0)
        self.assertGreater(result['height_inches'], 0)
        
        # Test with different product types
        for product_type in ['poster', 'mug', 'canvas', 'phone_case']:
            result = self.processor.get_optimal_print_size(3000, 3000, product_type)
            self.assertIsInstance(result, dict)
            self.assertIn('width_inches', result)
    
    def test_batch_processing(self):
        """Test batch processing functionality"""
        image_paths = [self.test_images['rgb'], self.test_images['rgba']]
        
        results = self.processor.batch_process_images(image_paths)
        
        self.assertEqual(len(results), 2)
        for result_path, info in results:
            if result_path:  # Successfully processed
                self.assertTrue(os.path.exists(result_path))
                self.assertIsInstance(info, ImageInfo)
    
    def test_format_support(self):
        """Test support for different image formats"""
        supported_formats = self.processor.supported_formats
        
        # Check that common formats are supported
        self.assertIn('JPEG', supported_formats)
        self.assertIn('PNG', supported_formats)
        self.assertIn('WEBP', supported_formats)
        
        # Test validation with different formats
        for format_name in ['JPEG', 'PNG']:
            # This would require creating images in different formats
            # For now, just check that the format is recognized
            self.assertIn(format_name, supported_formats)
    
    def test_print_requirements(self):
        """Test print requirements for different product types"""
        requirements = self.processor.print_requirements
        
        # Check that all expected product types have requirements
        expected_products = ['tshirt', 'poster', 'mug', 'canvas', 'phone_case']
        for product in expected_products:
            self.assertIn(product, requirements)
            req = requirements[product]
            self.assertIn('min_width', req)
            self.assertIn('min_height', req)
            self.assertIn('dpi', req)
    
    def test_error_handling(self):
        """Test error handling for various edge cases"""
        # Test with non-image file
        text_file = os.path.join(self.test_dir, 'test.txt')
        with open(text_file, 'w') as f:
            f.write('This is not an image')
        
        valid, issues = self.processor.validate_image(text_file)
        self.assertFalse(valid)
        self.assertGreater(len(issues), 0)
        
        # Test with corrupted image file
        corrupted_file = os.path.join(self.test_dir, 'corrupted.jpg')
        with open(corrupted_file, 'wb') as f:
            f.write(b'corrupted image data')
        
        valid, issues = self.processor.validate_image(corrupted_file)
        self.assertFalse(valid)
        self.assertGreater(len(issues), 0)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        # Clean up test files
        import shutil
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

class TestImageProcessorWithRealImages(unittest.TestCase):
    """Test ImageProcessor with real sample images from the project"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test with real images"""
        if not PILLOW_AVAILABLE:
            cls.skipTest(cls, "PIL/Pillow not available")
        
        cls.processor = ImageProcessor()
        cls.project_root = Path(__file__).parent.parent
        
        # Find sample images
        cls.sample_images = []
        for pattern in ['*.jpg', '*.jpeg', '*.png']:
            cls.sample_images.extend(list(cls.project_root.glob(pattern)))
        
        if not cls.sample_images:
            cls.skipTest(cls, "No sample images found in project")
    
    def test_real_image_processing(self):
        """Test processing of real sample images"""
        for image_path in self.sample_images[:5]:  # Test first 5 images
            with self.subTest(image=image_path.name):
                # Test validation
                valid, issues = self.processor.validate_image(str(image_path))
                self.assertIsInstance(valid, bool)
                self.assertIsInstance(issues, list)
                
                # Test optimization
                try:
                    output_path, info = self.processor.optimize_image(str(image_path))
                    self.assertTrue(os.path.exists(output_path))
                    self.assertIsInstance(info, ImageInfo)
                    
                    # Clean up
                    if os.path.exists(output_path):
                        os.remove(output_path)
                except Exception as e:
                    self.fail(f"Failed to optimize {image_path.name}: {e}")
    
    def test_real_image_metadata(self):
        """Test metadata extraction from real images"""
        for image_path in self.sample_images[:3]:  # Test first 3 images
            with self.subTest(image=image_path.name):
                # Test EXIF extraction
                exif_data = self.processor.extract_comprehensive_exif(str(image_path))
                self.assertIsInstance(exif_data, dict)
                
                # Test prompt extraction
                prompt = self.processor.extract_prompt_from_image(str(image_path))
                self.assertIsInstance(prompt, str)
                self.assertGreater(len(prompt), 0)

def run_image_processor_tests():
    """Run comprehensive image processor tests"""
    print("Running Image Processor Tests...")
    print("=" * 50)
    
    # Check if PIL is available
    if not PILLOW_AVAILABLE:
        print("❌ PIL/Pillow not available - cannot run image tests")
        return False
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestImageProcessor))
    suite.addTest(unittest.makeSuite(TestImageProcessorWithRealImages))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall: {'✅ PASSED' if success else '❌ FAILED'}")
    
    return success

if __name__ == "__main__":
    run_image_processor_tests()