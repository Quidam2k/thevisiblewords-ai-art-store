#!/usr/bin/env python3
"""
Comprehensive Printify Automation Workflow Test
Tests image processing, tag generation, and workflow validation without actual API calls
"""

import os
import sys
import json
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from tag_generator import SmartTagGenerator
    from image_processor import ImageProcessor
    from config_manager import ConfigManager
    from print_area_manager import PrintAreaManager
    from PIL import Image
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required dependencies: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PrintifyAutomationTester:
    """Comprehensive tester for Printify automation workflow"""
    
    def __init__(self, test_images_dir: str):
        self.test_images_dir = Path(test_images_dir)
        self.test_results = []
        self.failed_tests = []
        
        # Initialize components
        self.tag_generator = SmartTagGenerator()
        self.image_processor = ImageProcessor()
        self.print_area_manager = PrintAreaManager()
        
        # Test configuration
        self.test_config = {
            'max_test_images': 5,
            'target_tag_count': 10,
            'required_image_width': 2000,
            'required_image_height': 2000
        }
        
        logger.info(f"Initialized tester with images from: {self.test_images_dir}")
    
    def run_comprehensive_test(self) -> Dict:
        """Run all test scenarios and return results"""
        logger.info("Starting comprehensive Printify automation workflow test...")
        
        # Get test images
        test_images = self.get_test_images()
        if not test_images:
            return {"error": "No test images found", "status": "failed"}
        
        logger.info(f"Found {len(test_images)} test images")
        
        # Run test scenarios
        results = {
            "timestamp": datetime.now().isoformat(),
            "test_images_count": len(test_images),
            "scenarios": {}
        }
        
        try:
            # Test 1: Image Processing
            results["scenarios"]["image_processing"] = self.test_image_processing(test_images[:self.test_config['max_test_images']])
            
            # Test 2: Tag Generation
            results["scenarios"]["tag_generation"] = self.test_tag_generation(test_images[:self.test_config['max_test_images']])
            
            # Test 3: Workflow Validation
            results["scenarios"]["workflow_validation"] = self.test_workflow_validation(test_images[:3])
            
            # Test 4: Print Area Management
            results["scenarios"]["print_area_management"] = self.test_print_area_management()
            
            # Test 5: Error Handling
            results["scenarios"]["error_handling"] = self.test_error_handling()
            
            # Calculate overall success rate
            results["summary"] = self.calculate_test_summary(results["scenarios"])
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            results["error"] = str(e)
            results["status"] = "failed"
        
        return results
    
    def get_test_images(self) -> List[Path]:
        """Get list of test images"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
        
        images = []
        for ext in image_extensions:
            images.extend(self.test_images_dir.glob(f'*{ext}'))
            images.extend(self.test_images_dir.glob(f'*{ext.upper()}'))
        
        return sorted(images)[:20]  # Limit to first 20 images
    
    def test_image_processing(self, test_images: List[Path]) -> Dict:
        """Test image processing functionality"""
        logger.info("Testing image processing...")
        
        results = {
            "tested_images": 0,
            "successful_validations": 0,
            "successful_optimizations": 0,
            "prompt_extractions": 0,
            "details": [],
            "issues": []
        }
        
        for image_path in test_images:
            try:
                logger.info(f"Processing image: {image_path.name}")
                
                # Test image validation
                is_valid, issues = self.image_processor.validate_image(str(image_path))
                validation_result = {
                    "image": image_path.name,
                    "valid": is_valid,
                    "issues": issues
                }
                
                if is_valid:
                    results["successful_validations"] += 1
                    
                    # Test image optimization
                    try:
                        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                            optimized_path, image_info = self.image_processor.optimize_image(
                                str(image_path), tmp.name
                            )
                            
                            validation_result["optimization"] = {
                                "success": True,
                                "original_size": image_info.original_size,
                                "optimized_size": image_info.size_bytes,
                                "compression_ratio": ((image_info.original_size - image_info.size_bytes) / image_info.original_size) * 100,
                                "dimensions": f"{image_info.width}x{image_info.height}"
                            }
                            
                            results["successful_optimizations"] += 1
                            
                            # Clean up
                            os.unlink(tmp.name)
                            
                    except Exception as e:
                        validation_result["optimization"] = {
                            "success": False,
                            "error": str(e)
                        }
                
                # Test prompt extraction
                try:
                    prompt = self.image_processor.extract_prompt_from_image(str(image_path))
                    validation_result["prompt"] = prompt
                    
                    if prompt and prompt != "AI generated artwork":
                        results["prompt_extractions"] += 1
                        
                except Exception as e:
                    validation_result["prompt_error"] = str(e)
                
                results["details"].append(validation_result)
                results["tested_images"] += 1
                
            except Exception as e:
                error_msg = f"Failed to process {image_path.name}: {str(e)}"
                logger.error(error_msg)
                results["issues"].append(error_msg)
        
        results["success_rate"] = (results["successful_validations"] / results["tested_images"]) * 100 if results["tested_images"] > 0 else 0
        
        return results
    
    def test_tag_generation(self, test_images: List[Path]) -> Dict:
        """Test tag generation functionality"""
        logger.info("Testing tag generation...")
        
        results = {
            "tested_prompts": 0,
            "successful_generations": 0,
            "total_tags_generated": 0,
            "unique_tags": set(),
            "tag_examples": [],
            "details": []
        }
        
        for image_path in test_images:
            try:
                # Extract prompt from filename (since these are AI-generated images)
                filename = image_path.stem
                prompt = self.extract_prompt_from_filename(filename)
                
                if not prompt:
                    # Try to extract from image metadata
                    prompt = self.image_processor.extract_prompt_from_image(str(image_path))
                
                logger.info(f"Testing tag generation for: {image_path.name}")
                logger.info(f"Extracted prompt: {prompt[:100]}...")
                
                # Generate tags
                tags = self.tag_generator.extract_tags_from_prompt(prompt)
                title = self.tag_generator.generate_product_title(prompt)
                description = self.tag_generator.generate_description(prompt, title, tags)
                
                tag_result = {
                    "image": image_path.name,
                    "prompt": prompt,
                    "tags": tags,
                    "tag_count": len(tags),
                    "title": title,
                    "description_length": len(description)
                }
                
                results["details"].append(tag_result)
                results["tested_prompts"] += 1
                results["total_tags_generated"] += len(tags)
                results["unique_tags"].update(tags)
                
                if len(tags) > 0:
                    results["successful_generations"] += 1
                
                # Store some examples
                if len(results["tag_examples"]) < 3:
                    results["tag_examples"].append({
                        "image": image_path.name,
                        "prompt": prompt[:200],
                        "tags": tags[:10],
                        "title": title
                    })
                
            except Exception as e:
                error_msg = f"Tag generation failed for {image_path.name}: {str(e)}"
                logger.error(error_msg)
                results["issues"] = results.get("issues", [])
                results["issues"].append(error_msg)
        
        results["unique_tags"] = list(results["unique_tags"])
        results["average_tags_per_image"] = results["total_tags_generated"] / results["tested_prompts"] if results["tested_prompts"] > 0 else 0
        results["success_rate"] = (results["successful_generations"] / results["tested_prompts"]) * 100 if results["tested_prompts"] > 0 else 0
        
        return results
    
    def test_workflow_validation(self, test_images: List[Path]) -> Dict:
        """Test end-to-end workflow validation"""
        logger.info("Testing workflow validation...")
        
        results = {
            "tested_workflows": 0,
            "successful_workflows": 0,
            "workflow_steps": [],
            "details": []
        }
        
        for image_path in test_images:
            try:
                workflow_result = {
                    "image": image_path.name,
                    "steps": {},
                    "success": True,
                    "errors": []
                }
                
                # Step 1: Image validation
                try:
                    is_valid, issues = self.image_processor.validate_image(str(image_path))
                    workflow_result["steps"]["validation"] = {
                        "success": is_valid,
                        "issues": issues
                    }
                    if not is_valid:
                        workflow_result["success"] = False
                        workflow_result["errors"].extend(issues)
                except Exception as e:
                    workflow_result["steps"]["validation"] = {"success": False, "error": str(e)}
                    workflow_result["success"] = False
                    workflow_result["errors"].append(f"Validation failed: {str(e)}")
                
                # Step 2: Image optimization
                if workflow_result["steps"]["validation"]["success"]:
                    try:
                        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                            optimized_path, image_info = self.image_processor.optimize_image(
                                str(image_path), tmp.name
                            )
                            workflow_result["steps"]["optimization"] = {
                                "success": True,
                                "size_reduction": ((image_info.original_size - image_info.size_bytes) / image_info.original_size) * 100
                            }
                            os.unlink(tmp.name)
                    except Exception as e:
                        workflow_result["steps"]["optimization"] = {"success": False, "error": str(e)}
                        workflow_result["success"] = False
                        workflow_result["errors"].append(f"Optimization failed: {str(e)}")
                
                # Step 3: Prompt extraction
                try:
                    filename = image_path.stem
                    prompt = self.extract_prompt_from_filename(filename)
                    if not prompt:
                        prompt = self.image_processor.extract_prompt_from_image(str(image_path))
                    
                    workflow_result["steps"]["prompt_extraction"] = {
                        "success": bool(prompt),
                        "prompt_length": len(prompt) if prompt else 0
                    }
                except Exception as e:
                    workflow_result["steps"]["prompt_extraction"] = {"success": False, "error": str(e)}
                    workflow_result["success"] = False
                    workflow_result["errors"].append(f"Prompt extraction failed: {str(e)}")
                
                # Step 4: Tag generation
                if workflow_result["steps"]["prompt_extraction"]["success"]:
                    try:
                        tags = self.tag_generator.extract_tags_from_prompt(prompt)
                        title = self.tag_generator.generate_product_title(prompt)
                        description = self.tag_generator.generate_description(prompt, title, tags)
                        
                        workflow_result["steps"]["tag_generation"] = {
                            "success": True,
                            "tag_count": len(tags),
                            "has_title": bool(title),
                            "has_description": bool(description)
                        }
                    except Exception as e:
                        workflow_result["steps"]["tag_generation"] = {"success": False, "error": str(e)}
                        workflow_result["success"] = False
                        workflow_result["errors"].append(f"Tag generation failed: {str(e)}")
                
                # Step 5: Print area simulation
                try:
                    if workflow_result["steps"]["optimization"]["success"]:
                        # Simulate print area calculations
                        print_positions = self.print_area_manager.get_available_positions("tshirt")
                        workflow_result["steps"]["print_area"] = {
                            "success": True,
                            "available_positions": len(print_positions)
                        }
                    else:
                        workflow_result["steps"]["print_area"] = {"success": False, "error": "No optimized image"}
                except Exception as e:
                    workflow_result["steps"]["print_area"] = {"success": False, "error": str(e)}
                    workflow_result["success"] = False
                    workflow_result["errors"].append(f"Print area calculation failed: {str(e)}")
                
                results["details"].append(workflow_result)
                results["tested_workflows"] += 1
                
                if workflow_result["success"]:
                    results["successful_workflows"] += 1
                
            except Exception as e:
                error_msg = f"Workflow test failed for {image_path.name}: {str(e)}"
                logger.error(error_msg)
                results["issues"] = results.get("issues", [])
                results["issues"].append(error_msg)
        
        results["success_rate"] = (results["successful_workflows"] / results["tested_workflows"]) * 100 if results["tested_workflows"] > 0 else 0
        
        return results
    
    def test_print_area_management(self) -> Dict:
        """Test print area management functionality"""
        logger.info("Testing print area management...")
        
        results = {
            "tested_products": 0,
            "available_positions": {},
            "position_recommendations": {},
            "success": True
        }
        
        product_types = ["tshirt", "poster", "mug", "canvas", "phone_case"]
        
        for product_type in product_types:
            try:
                # Test available positions
                positions = self.print_area_manager.get_available_positions(product_type)
                results["available_positions"][product_type] = [pos.value for pos in positions]
                
                # Test position recommendations
                recommendations = self.print_area_manager.get_position_recommendations(
                    3000, 3000, product_type
                )
                results["position_recommendations"][product_type] = {
                    pos.value: {
                        "compatibility": rec["compatibility_score"],
                        "strategy": rec["recommended_strategy"]
                    }
                    for pos, rec in recommendations.items()
                }
                
                results["tested_products"] += 1
                
            except Exception as e:
                error_msg = f"Print area test failed for {product_type}: {str(e)}"
                logger.error(error_msg)
                results["issues"] = results.get("issues", [])
                results["issues"].append(error_msg)
                results["success"] = False
        
        return results
    
    def test_error_handling(self) -> Dict:
        """Test error handling capabilities"""
        logger.info("Testing error handling...")
        
        results = {
            "tested_scenarios": 0,
            "handled_errors": 0,
            "error_scenarios": []
        }
        
        # Test invalid image path
        try:
            is_valid, issues = self.image_processor.validate_image("nonexistent_image.jpg")
            results["error_scenarios"].append({
                "scenario": "Invalid image path",
                "handled": len(issues) > 0,
                "issues": issues
            })
            if len(issues) > 0:
                results["handled_errors"] += 1
        except Exception as e:
            results["error_scenarios"].append({
                "scenario": "Invalid image path",
                "handled": False,
                "error": str(e)
            })
        
        results["tested_scenarios"] += 1
        
        # Test invalid prompt
        try:
            tags = self.tag_generator.extract_tags_from_prompt("")
            results["error_scenarios"].append({
                "scenario": "Empty prompt",
                "handled": len(tags) > 0,  # Should return default tags
                "tags": tags
            })
            if len(tags) > 0:
                results["handled_errors"] += 1
        except Exception as e:
            results["error_scenarios"].append({
                "scenario": "Empty prompt",
                "handled": False,
                "error": str(e)
            })
        
        results["tested_scenarios"] += 1
        
        results["success_rate"] = (results["handled_errors"] / results["tested_scenarios"]) * 100 if results["tested_scenarios"] > 0 else 0
        
        return results
    
    def extract_prompt_from_filename(self, filename: str) -> str:
        """Extract prompt from filename (for AI-generated images)"""
        # Remove common prefixes and suffixes
        cleaned = filename.replace('quidamn_', '').replace('00001-', '').replace('00002-', '').replace('00011-', '')
        
        # Replace underscores with spaces
        cleaned = cleaned.replace('_', ' ')
        
        # Remove UUIDs and other generated suffixes
        import re
        cleaned = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '', cleaned)
        cleaned = re.sub(r'--[a-z0-9]+', '', cleaned)  # Remove --ar and other parameters
        
        # Clean up extra spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip() if len(cleaned.strip()) > 10 else ""
    
    def calculate_test_summary(self, scenarios: Dict) -> Dict:
        """Calculate overall test summary"""
        total_tests = 0
        successful_tests = 0
        
        for scenario_name, scenario_data in scenarios.items():
            if isinstance(scenario_data, dict) and "success_rate" in scenario_data:
                total_tests += 1
                if scenario_data["success_rate"] > 70:  # Consider >70% as successful
                    successful_tests += 1
        
        return {
            "total_scenarios": len(scenarios),
            "successful_scenarios": successful_tests,
            "overall_success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "status": "PASS" if (successful_tests / total_tests) > 0.7 else "FAIL" if total_tests > 0 else "NO_DATA"
        }
    
    def generate_report(self, results: Dict) -> str:
        """Generate a comprehensive test report"""
        report = []
        
        report.append("# Printify Automation Workflow Test Report")
        report.append(f"Generated: {results.get('timestamp', 'Unknown')}")
        report.append(f"Test Images: {results.get('test_images_count', 0)}")
        report.append("")
        
        # Summary
        if "summary" in results:
            summary = results["summary"]
            report.append("## Summary")
            report.append(f"- Total Scenarios: {summary['total_scenarios']}")
            report.append(f"- Successful Scenarios: {summary['successful_scenarios']}")
            report.append(f"- Overall Success Rate: {summary['overall_success_rate']:.1f}%")
            report.append(f"- Status: {summary['status']}")
            report.append("")
        
        # Detailed results
        for scenario_name, scenario_data in results.get("scenarios", {}).items():
            report.append(f"## {scenario_name.replace('_', ' ').title()}")
            
            if isinstance(scenario_data, dict):
                # Success rate
                if "success_rate" in scenario_data:
                    status = "✅ PASS" if scenario_data["success_rate"] > 70 else "❌ FAIL"
                    report.append(f"**Status:** {status} ({scenario_data['success_rate']:.1f}%)")
                
                # Key metrics
                for key, value in scenario_data.items():
                    if key not in ["details", "tag_examples", "issues", "success_rate"]:
                        if isinstance(value, (int, float)):
                            report.append(f"- {key.replace('_', ' ').title()}: {value}")
                        elif isinstance(value, list) and len(value) < 20:
                            report.append(f"- {key.replace('_', ' ').title()}: {len(value)} items")
                
                # Examples
                if "tag_examples" in scenario_data:
                    report.append("### Tag Generation Examples:")
                    for example in scenario_data["tag_examples"][:2]:
                        report.append(f"**{example['image']}:**")
                        report.append(f"- Prompt: {example['prompt'][:100]}...")
                        report.append(f"- Tags: {', '.join(example['tags'][:8])}")
                        report.append(f"- Title: {example['title']}")
                        report.append("")
                
                # Issues
                if "issues" in scenario_data and scenario_data["issues"]:
                    report.append("### Issues:")
                    for issue in scenario_data["issues"][:5]:
                        report.append(f"- {issue}")
                    report.append("")
            
            report.append("")
        
        return "\n".join(report)

def main():
    """Main test execution function"""
    # Configuration
    test_images_dir = "/mnt/h/Development/www.thevisiblewords.com/printify_automation_script_Copy"
    
    if not os.path.exists(test_images_dir):
        print(f"Error: Test images directory not found: {test_images_dir}")
        return
    
    # Initialize tester
    tester = PrintifyAutomationTester(test_images_dir)
    
    # Run comprehensive tests
    print("Starting Printify Automation Workflow Tests...")
    results = tester.run_comprehensive_test()
    
    # Generate and save report
    report = tester.generate_report(results)
    
    # Save results
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    with open("test_report.md", "w") as f:
        f.write(report)
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    if "summary" in results:
        summary = results["summary"]
        print(f"Overall Status: {summary['status']}")
        print(f"Success Rate: {summary['overall_success_rate']:.1f}%")
        print(f"Scenarios Tested: {summary['total_scenarios']}")
        print(f"Successful Scenarios: {summary['successful_scenarios']}")
    
    print(f"\nDetailed results saved to:")
    print(f"- test_results.json")
    print(f"- test_report.md")
    
    return results

if __name__ == "__main__":
    main()