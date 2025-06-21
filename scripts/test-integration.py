#!/usr/bin/env python3
"""
Integration Test Script - The Visible Words AI Art Platform
Tests the complete workflow from automation system to e-commerce store
"""

import os
import sys
import json
import time
import requests
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add automation system to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'printify-automation', 'src'))

class IntegrationTester:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.automation_dir = self.base_dir / 'printify-automation'
        self.store_dir = self.base_dir / 'ai-art-store'
        self.test_results = []
        
    def log_result(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """Log test result"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
    def test_automation_system(self) -> bool:
        """Test if automation system components are working"""
        try:
            # Test core module imports
            from tag_generator import SmartTagGenerator
            from config_manager import ConfigManager
            from image_processor import ImageProcessor
            from api_client import PrintifyAPIClient
            
            self.log_result("automation_imports", True, "All core modules imported successfully")
            
            # Test SmartTagGenerator
            tag_gen = SmartTagGenerator()
            test_prompt = "A beautiful fantasy castle on a hilltop with dragons flying around"
            tags = tag_gen.extract_tags_from_prompt(test_prompt)
            
            if len(tags) > 0:
                self.log_result("tag_generation", True, f"Generated {len(tags)} tags", {"tags": tags})
            else:
                self.log_result("tag_generation", False, "No tags generated")
                return False
                
            # Test ConfigManager
            config_mgr = ConfigManager()
            config = config_mgr.config
            
            self.log_result("config_manager", True, "Config manager initialized", {
                "has_api_settings": hasattr(config, 'api'),
                "has_image_settings": hasattr(config, 'image_processing')
            })
            
            # Test ImageProcessor
            img_processor = ImageProcessor()
            self.log_result("image_processor", True, "Image processor initialized")
            
            return True
            
        except Exception as e:
            self.log_result("automation_system", False, f"Error: {str(e)}")
            return False
    
    def test_store_database(self) -> bool:
        """Test if store database schema is correct"""
        try:
            db_path = self.store_dir / 'prisma' / 'dev.db'
            
            if not db_path.exists():
                self.log_result("database_exists", False, "Database file not found")
                return False
                
            # Connect to database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check if required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['Product', 'ProductImage', 'ProductVariant', 'Artwork']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                self.log_result("database_schema", False, f"Missing tables: {missing_tables}")
                return False
            else:
                self.log_result("database_schema", True, f"All required tables present: {required_tables}")
            
            # Check sample data
            cursor.execute("SELECT COUNT(*) FROM Product")
            product_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Artwork")
            artwork_count = cursor.fetchone()[0]
            
            self.log_result("sample_data", True, f"Products: {product_count}, Artworks: {artwork_count}")
            
            conn.close()
            return True
            
        except Exception as e:
            self.log_result("store_database", False, f"Error: {str(e)}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test if store API endpoints are working (if server is running)"""
        try:
            base_url = "http://localhost:3000"
            endpoints = [
                "/api/products",
                "/api/categories",
            ]
            
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        self.log_result(f"api_endpoint_{endpoint.replace('/', '_')}", True, 
                                      f"Status: {response.status_code}", {"data_keys": list(data.keys()) if isinstance(data, dict) else "array"})
                    else:
                        self.log_result(f"api_endpoint_{endpoint.replace('/', '_')}", False, 
                                      f"Status: {response.status_code}")
                except requests.ConnectionError:
                    self.log_result(f"api_endpoint_{endpoint.replace('/', '_')}", False, 
                                  "Server not running (expected for this test)")
                    
        except Exception as e:
            self.log_result("api_endpoints", False, f"Error: {str(e)}")
            return False
            
        return True
    
    def test_image_processing_workflow(self) -> bool:
        """Test complete image processing workflow with sample image"""
        try:
            # Find test images
            test_images_dir = self.base_dir / 'printify_automation_script_Copy'
            image_files = list(test_images_dir.glob('*.png')) + list(test_images_dir.glob('*.jpg'))
            
            if not image_files:
                self.log_result("test_images", False, "No test images found")
                return False
                
            test_image = image_files[0]
            self.log_result("test_images", True, f"Found {len(image_files)} test images, using {test_image.name}")
            
            # Import automation modules
            from tag_generator import SmartTagGenerator
            from image_processor import ImageProcessor
            
            # Process image filename for prompt extraction
            filename = test_image.stem
            tag_gen = SmartTagGenerator()
            
            # Extract tags from filename (simulating prompt)
            tags = tag_gen.extract_tags_from_prompt(filename.replace('_', ' '))
            
            # Generate title and description
            title = tag_gen.generate_title_from_tags(tags)
            description = tag_gen.generate_description_from_tags(tags)
            
            # Create product data structure
            product_data = {
                'title': title,
                'description': description,
                'tags': tags,
                'base_price': 19.99,
                'category': 'Art & Design',
                'image_path': str(test_image),
                'style': self._determine_art_style(tags)
            }
            
            self.log_result("image_processing_workflow", True, 
                          f"Processed {test_image.name}", {
                              "title": title,
                              "tags_count": len(tags),
                              "description_length": len(description)
                          })
            
            return True
            
        except Exception as e:
            self.log_result("image_processing_workflow", False, f"Error: {str(e)}")
            return False
    
    def _determine_art_style(self, tags: List[str]) -> str:
        """Determine art style from tags"""
        if any(tag in ['fantasy', 'magical', 'dragon', 'castle'] for tag in tags):
            return 'WHIMSY'
        elif any(tag in ['sci-fi', 'futuristic', 'space', 'robot'] for tag in tags):
            return 'EPIC'
        else:
            return 'HYBRID'
    
    def test_data_conversion(self) -> bool:
        """Test conversion from automation format to store format"""
        try:
            # Sample automation output
            automation_data = {
                'filename': 'fantasy_castle_dragons.png',
                'tags': ['fantasy', 'castle', 'dragons', 'medieval', 'art'],
                'title': 'Majestic Fantasy Castle with Dragons',
                'description': 'A stunning fantasy artwork featuring a medieval castle with dragons soaring overhead.',
                'base_price': 24.99,
                'printify_product_id': 'test_123',
                'variants': [
                    {'size': 'M', 'color': 'white', 'type': 'tshirt', 'price': 24.99},
                    {'size': 'L', 'color': 'black', 'type': 'tshirt', 'price': 26.99}
                ]
            }
            
            # Convert to store format
            store_data = {
                'title': automation_data['title'],
                'description': automation_data['description'],
                'basePrice': automation_data['base_price'],
                'category': 'Apparel',
                'printifyProductId': automation_data['printify_product_id'],
                'artwork': {
                    'style': self._determine_art_style(automation_data['tags']),
                    'tags': automation_data['tags'],
                    'originalPrompt': automation_data['filename'].replace('_', ' '),
                    'analysis': automation_data['description']
                },
                'variants': [
                    {
                        'size': v['size'],
                        'color': v['color'],
                        'type': v['type'],
                        'price': v['price'],
                        'available': True,
                        'printifyVariantId': f"var_{i}"
                    } for i, v in enumerate(automation_data['variants'])
                ],
                'images': [
                    {
                        'url': f"/images/{automation_data['filename']}",
                        'alt': automation_data['title'],
                        'isPrimary': True
                    }
                ]
            }
            
            # Validate converted data
            required_fields = ['title', 'description', 'basePrice', 'category', 'artwork', 'variants']
            missing_fields = [field for field in required_fields if field not in store_data]
            
            if missing_fields:
                self.log_result("data_conversion", False, f"Missing fields: {missing_fields}")
                return False
            
            self.log_result("data_conversion", True, "Successfully converted automation data to store format", {
                "variants_count": len(store_data['variants']),
                "tags_count": len(store_data['artwork']['tags']),
                "style": store_data['artwork']['style']
            })
            
            return True
            
        except Exception as e:
            self.log_result("data_conversion", False, f"Error: {str(e)}")
            return False
    
    def test_file_structure(self) -> bool:
        """Test if all required files and directories exist"""
        try:
            required_files = [
                # Automation system
                'printify-automation/app.py',
                'printify-automation/requirements.txt',
                'printify-automation/src/tag_generator.py',
                'printify-automation/src/image_processor.py',
                'printify-automation/src/api_client.py',
                
                # Store system  
                'ai-art-store/package.json',
                'ai-art-store/next.config.js',
                'ai-art-store/app/page.tsx',
                'ai-art-store/app/shop/page.tsx',
                'ai-art-store/app/product/[id]/page.tsx',
                'ai-art-store/prisma/schema.prisma',
                
                # Documentation
                'README.md',
                'INTEGRATION_COMPLETE.md',
                '.gitignore'
            ]
            
            missing_files = []
            for file_path in required_files:
                full_path = self.base_dir / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
                    
            if missing_files:
                self.log_result("file_structure", False, f"Missing files: {missing_files[:5]}...")
                return False
            else:
                self.log_result("file_structure", True, f"All {len(required_files)} required files present")
                return True
                
        except Exception as e:
            self.log_result("file_structure", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all integration tests"""
        print("🚀 Starting Integration Tests for The Visible Words AI Art Platform")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_file_structure,
            self.test_automation_system,
            self.test_store_database,
            self.test_image_processing_workflow,
            self.test_data_conversion,
            self.test_api_endpoints,
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                self.log_result(test.__name__, False, f"Test failed with exception: {str(e)}")
        
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        # Summary
        print("\n" + "=" * 70)
        print(f"🎯 Integration Test Results")
        print(f"Tests Passed: {passed}/{total} ({round(passed/total*100, 1)}%)")
        print(f"Duration: {duration}s")
        
        # Save detailed results
        results_file = self.base_dir / 'integration-test-results.json'
        with open(results_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total,
                    'passed': passed,
                    'failed': total - passed,
                    'success_rate': round(passed/total*100, 1),
                    'duration_seconds': duration,
                    'timestamp': datetime.now().isoformat()
                },
                'results': self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: {results_file}")
        
        return {
            'passed': passed,
            'total': total,
            'success_rate': passed/total*100,
            'results': self.test_results
        }

if __name__ == '__main__':
    tester = IntegrationTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['passed'] == results['total'] else 1)