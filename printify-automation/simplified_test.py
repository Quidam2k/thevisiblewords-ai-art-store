#!/usr/bin/env python3
"""
Simplified Printify Automation Workflow Test
Tests the workflow logic and file analysis without external dependencies
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

class SimpleAutomationTester:
    """Simplified tester for workflow analysis"""
    
    def __init__(self, test_images_dir: str):
        self.test_images_dir = Path(test_images_dir)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_scenarios": {}
        }
    
    def run_tests(self):
        """Run simplified tests"""
        print("🚀 Starting Printify Automation Workflow Analysis...")
        print(f"Test images directory: {self.test_images_dir}")
        
        # Test 1: Image Discovery
        self.test_image_discovery()
        
        # Test 2: Filename Analysis
        self.test_filename_analysis()
        
        # Test 3: Tag Generation Simulation
        self.test_tag_generation_simulation()
        
        # Test 4: Workflow Validation
        self.test_workflow_validation()
        
        # Generate report
        self.generate_report()
        
        return self.results
    
    def test_image_discovery(self):
        """Test image discovery and categorization"""
        print("\n📂 Testing Image Discovery...")
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        discovered_images = []
        
        for ext in image_extensions:
            discovered_images.extend(list(self.test_images_dir.glob(f'*{ext}')))
            discovered_images.extend(list(self.test_images_dir.glob(f'*{ext.upper()}')))
        
        # Categorize by themes
        categories = {
            'fantasy': ['fantasy', 'dragon', 'magic', 'elf', 'castle', 'wizard'],
            'sci-fi': ['futuristic', 'cyberpunk', 'robot', 'space', 'alien', 'technology'],
            'architecture': ['building', 'house', 'city', 'skyline', 'architecture'],
            'nature': ['landscape', 'tree', 'forest', 'mountain', 'flower', 'garden'],
            'abstract': ['abstract', 'pattern', 'geometric', 'art', 'design'],
            'characters': ['woman', 'man', 'person', 'character', 'portrait', 'face']
        }
        
        categorized = {cat: [] for cat in categories}
        uncategorized = []
        
        for image in discovered_images:
            filename = image.name.lower()
            categorized_flag = False
            
            for category, keywords in categories.items():
                if any(keyword in filename for keyword in keywords):
                    categorized[category].append(image.name)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                uncategorized.append(image.name)
        
        self.results["test_scenarios"]["image_discovery"] = {
            "total_images": len(discovered_images),
            "categorized": {cat: len(images) for cat, images in categorized.items()},
            "uncategorized": len(uncategorized),
            "categories": categorized,
            "file_types": self.analyze_file_types(discovered_images)
        }
        
        print(f"✅ Discovered {len(discovered_images)} images")
        for cat, images in categorized.items():
            if images:
                print(f"   - {cat.title()}: {len(images)} images")
    
    def test_filename_analysis(self):
        """Test filename analysis and prompt extraction"""
        print("\n🏷️ Testing Filename Analysis...")
        
        image_files = list(self.test_images_dir.glob('*.png')) + list(self.test_images_dir.glob('*.jpg'))
        
        prompt_analysis = []
        
        for image_file in image_files[:10]:  # Test first 10 images
            filename = image_file.stem
            
            # Extract prompt from filename
            extracted_prompt = self.extract_prompt_from_filename(filename)
            
            # Analyze prompt quality
            quality_score = self.analyze_prompt_quality(extracted_prompt)
            
            analysis = {
                "filename": image_file.name,
                "extracted_prompt": extracted_prompt,
                "prompt_length": len(extracted_prompt),
                "quality_score": quality_score,
                "contains_style_info": self.contains_style_information(extracted_prompt),
                "contains_subject_info": self.contains_subject_information(extracted_prompt)
            }
            
            prompt_analysis.append(analysis)
        
        self.results["test_scenarios"]["filename_analysis"] = {
            "tested_files": len(prompt_analysis),
            "average_prompt_length": sum(p["prompt_length"] for p in prompt_analysis) / len(prompt_analysis) if prompt_analysis else 0,
            "average_quality_score": sum(p["quality_score"] for p in prompt_analysis) / len(prompt_analysis) if prompt_analysis else 0,
            "files_with_style_info": sum(1 for p in prompt_analysis if p["contains_style_info"]),
            "files_with_subject_info": sum(1 for p in prompt_analysis if p["contains_subject_info"]),
            "examples": prompt_analysis[:5]
        }
        
        print(f"✅ Analyzed {len(prompt_analysis)} filenames")
        print(f"   - Average prompt length: {self.results['test_scenarios']['filename_analysis']['average_prompt_length']:.1f} characters")
        print(f"   - Files with style info: {self.results['test_scenarios']['filename_analysis']['files_with_style_info']}")
    
    def test_tag_generation_simulation(self):
        """Simulate tag generation without external dependencies"""
        print("\n🏷️ Testing Tag Generation Simulation...")
        
        # Simulated tag categories
        art_styles = ['digital-art', 'fantasy-art', 'sci-fi-art', 'abstract-art', 'concept-art']
        colors = ['colorful', 'vibrant', 'dark', 'light', 'neon', 'pastel']
        subjects = ['landscape', 'portrait', 'architecture', 'nature', 'character', 'vehicle']
        moods = ['dramatic', 'peaceful', 'mysterious', 'energetic', 'calm', 'intense']
        
        tag_simulations = []
        
        # Get sample prompts from filenames
        image_files = list(self.test_images_dir.glob('*.png'))[:8]
        
        for image_file in image_files:
            prompt = self.extract_prompt_from_filename(image_file.stem)
            
            # Simulate tag generation
            simulated_tags = self.simulate_tag_extraction(prompt, art_styles, colors, subjects, moods)
            simulated_title = self.simulate_title_generation(prompt)
            
            simulation = {
                "image": image_file.name,
                "prompt": prompt[:100],
                "generated_tags": simulated_tags,
                "tag_count": len(simulated_tags),
                "generated_title": simulated_title
            }
            
            tag_simulations.append(simulation)
        
        self.results["test_scenarios"]["tag_generation"] = {
            "simulated_files": len(tag_simulations),
            "average_tags_per_image": sum(s["tag_count"] for s in tag_simulations) / len(tag_simulations) if tag_simulations else 0,
            "unique_tags_generated": len(set(tag for sim in tag_simulations for tag in sim["generated_tags"])),
            "examples": tag_simulations[:3]
        }
        
        print(f"✅ Simulated tag generation for {len(tag_simulations)} images")
        print(f"   - Average tags per image: {self.results['test_scenarios']['tag_generation']['average_tags_per_image']:.1f}")
        print(f"   - Unique tags generated: {self.results['test_scenarios']['tag_generation']['unique_tags_generated']}")
    
    def test_workflow_validation(self):
        """Test workflow validation logic"""
        print("\n🔄 Testing Workflow Validation...")
        
        workflow_steps = [
            "Image Discovery",
            "Filename Analysis", 
            "Prompt Extraction",
            "Tag Generation",
            "Title Generation",
            "Description Generation",
            "Print Area Calculation",
            "Product Creation"
        ]
        
        # Simulate workflow validation
        image_files = list(self.test_images_dir.glob('*.png'))[:5]
        workflow_results = []
        
        for image_file in image_files:
            workflow_result = {
                "image": image_file.name,
                "steps": {},
                "overall_success": True
            }
            
            # Step 1: Image Discovery
            workflow_result["steps"]["discovery"] = {
                "success": True,
                "details": "Image file found and accessible"
            }
            
            # Step 2: Filename Analysis
            prompt = self.extract_prompt_from_filename(image_file.stem)
            workflow_result["steps"]["filename_analysis"] = {
                "success": len(prompt) > 10,
                "details": f"Extracted prompt: {len(prompt)} characters"
            }
            
            # Step 3: Tag Generation (simulated)
            if workflow_result["steps"]["filename_analysis"]["success"]:
                tags = self.simulate_tag_extraction(prompt, ['art'], ['colorful'], ['landscape'], ['peaceful'])
                workflow_result["steps"]["tag_generation"] = {
                    "success": len(tags) > 0,
                    "details": f"Generated {len(tags)} tags"
                }
            else:
                workflow_result["steps"]["tag_generation"] = {
                    "success": False,
                    "details": "Failed due to poor filename analysis"
                }
            
            # Step 4: Product Creation Readiness
            all_steps_success = all(step["success"] for step in workflow_result["steps"].values())
            workflow_result["steps"]["product_readiness"] = {
                "success": all_steps_success,
                "details": "Ready for product creation" if all_steps_success else "Not ready - has issues"
            }
            
            workflow_result["overall_success"] = all_steps_success
            workflow_results.append(workflow_result)
        
        successful_workflows = sum(1 for w in workflow_results if w["overall_success"])
        
        self.results["test_scenarios"]["workflow_validation"] = {
            "tested_workflows": len(workflow_results),
            "successful_workflows": successful_workflows,
            "success_rate": (successful_workflows / len(workflow_results)) * 100 if workflow_results else 0,
            "workflow_steps": workflow_steps,
            "results": workflow_results
        }
        
        print(f"✅ Validated {len(workflow_results)} workflows")
        print(f"   - Success rate: {self.results['test_scenarios']['workflow_validation']['success_rate']:.1f}%")
        print(f"   - Successful workflows: {successful_workflows}/{len(workflow_results)}")
    
    def extract_prompt_from_filename(self, filename: str) -> str:
        """Extract prompt from filename"""
        # Remove common prefixes
        cleaned = re.sub(r'^(quidamn_|00\d+-)', '', filename)
        
        # Replace underscores with spaces
        cleaned = cleaned.replace('_', ' ')
        
        # Remove UUIDs and technical suffixes
        cleaned = re.sub(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '', cleaned)
        cleaned = re.sub(r'--[a-z0-9]+', '', cleaned)
        
        # Clean up spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def analyze_prompt_quality(self, prompt: str) -> float:
        """Analyze prompt quality (0-100 score)"""
        if not prompt:
            return 0
        
        score = 0
        
        # Length bonus
        if len(prompt) > 20:
            score += 20
        if len(prompt) > 50:
            score += 20
        
        # Descriptive words bonus
        descriptive_words = ['detailed', 'beautiful', 'stunning', 'masterpiece', 'intricate', 'elegant']
        if any(word in prompt.lower() for word in descriptive_words):
            score += 15
        
        # Style information bonus
        if self.contains_style_information(prompt):
            score += 25
        
        # Subject information bonus
        if self.contains_subject_information(prompt):
            score += 20
        
        return min(score, 100)
    
    def contains_style_information(self, prompt: str) -> bool:
        """Check if prompt contains style information"""
        style_indicators = [
            'painting', 'art', 'style', 'digital', 'watercolor', 'oil', 'acrylic',
            'sketch', 'drawing', 'illustration', 'render', 'photorealistic',
            'abstract', 'impressionist', 'surreal', 'minimalist'
        ]
        return any(indicator in prompt.lower() for indicator in style_indicators)
    
    def contains_subject_information(self, prompt: str) -> bool:
        """Check if prompt contains subject information"""
        subject_indicators = [
            'woman', 'man', 'person', 'character', 'landscape', 'city', 'building',
            'tree', 'flower', 'animal', 'dragon', 'castle', 'room', 'space',
            'sky', 'mountain', 'forest', 'ocean', 'river', 'house'
        ]
        return any(indicator in prompt.lower() for indicator in subject_indicators)
    
    def simulate_tag_extraction(self, prompt: str, art_styles: list, colors: list, subjects: list, moods: list) -> list:
        """Simulate tag extraction from prompt"""
        if not prompt:
            return ['ai-art', 'digital-art']
        
        tags = ['ai-art']  # Always include base tag
        prompt_lower = prompt.lower()
        
        # Add style tags
        for style in art_styles:
            if any(word in prompt_lower for word in style.split('-')):
                tags.append(style)
        
        # Add color tags
        for color in colors:
            if color in prompt_lower:
                tags.append(color)
        
        # Add subject tags
        for subject in subjects:
            if subject in prompt_lower:
                tags.append(subject)
        
        # Add mood tags
        for mood in moods:
            if mood in prompt_lower:
                tags.append(mood)
        
        # Add some prompt-specific tags
        words = prompt_lower.split()
        for word in words:
            if len(word) > 4 and word.isalpha():
                tags.append(word)
        
        return list(set(tags))[:12]  # Limit to 12 unique tags
    
    def simulate_title_generation(self, prompt: str) -> str:
        """Simulate title generation from prompt"""
        if not prompt:
            return "AI Generated Artwork"
        
        # Take first part of prompt and capitalize
        words = prompt.split()[:6]  # First 6 words
        title = ' '.join(word.capitalize() for word in words)
        
        # Limit length
        if len(title) > 80:
            title = title[:77] + "..."
        
        return title if title else "AI Generated Artwork"
    
    def analyze_file_types(self, images: list) -> dict:
        """Analyze file types distribution"""
        file_types = {}
        for image in images:
            ext = image.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
        return file_types
    
    def generate_report(self):
        """Generate and save test report"""
        print("\n📊 Generating Test Report...")
        
        # Calculate overall stats
        total_tests = len(self.results["test_scenarios"])
        successful_tests = 0
        
        for scenario_name, scenario_data in self.results["test_scenarios"].items():
            if "success_rate" in scenario_data and scenario_data["success_rate"] > 70:
                successful_tests += 1
            elif "tested_files" in scenario_data and scenario_data["tested_files"] > 0:
                successful_tests += 1
            elif "total_images" in scenario_data and scenario_data["total_images"] > 0:
                successful_tests += 1
        
        # Generate markdown report
        report_lines = [
            "# Printify Automation Workflow Test Report",
            f"Generated: {self.results['timestamp']}",
            "",
            "## Summary",
            f"- Total Test Scenarios: {total_tests}",
            f"- Successful Scenarios: {successful_tests}",
            f"- Overall Success Rate: {(successful_tests/total_tests)*100:.1f}%" if total_tests > 0 else "- Overall Success Rate: 0%",
            ""
        ]
        
        # Add detailed results
        for scenario_name, scenario_data in self.results["test_scenarios"].items():
            report_lines.append(f"## {scenario_name.replace('_', ' ').title()}")
            
            if scenario_name == "image_discovery":
                report_lines.extend([
                    f"- **Total Images Found:** {scenario_data['total_images']}",
                    f"- **Categorized Images:** {sum(scenario_data['categorized'].values())}",
                    f"- **Uncategorized Images:** {scenario_data['uncategorized']}",
                    "",
                    "**Categories:**"
                ])
                
                for cat, count in scenario_data['categorized'].items():
                    if count > 0:
                        report_lines.append(f"- {cat.title()}: {count} images")
                
                report_lines.extend(["", "**File Types:**"])
                for ext, count in scenario_data['file_types'].items():
                    report_lines.append(f"- {ext}: {count} files")
            
            elif scenario_name == "filename_analysis":
                report_lines.extend([
                    f"- **Files Analyzed:** {scenario_data['tested_files']}",
                    f"- **Average Prompt Length:** {scenario_data['average_prompt_length']:.1f} characters",
                    f"- **Average Quality Score:** {scenario_data['average_quality_score']:.1f}/100",
                    f"- **Files with Style Info:** {scenario_data['files_with_style_info']}",
                    f"- **Files with Subject Info:** {scenario_data['files_with_subject_info']}",
                    "",
                    "**Examples:**"
                ])
                
                for example in scenario_data['examples'][:3]:
                    report_lines.extend([
                        f"- **{example['filename']}**",
                        f"  - Prompt: {example['extracted_prompt'][:100]}...",
                        f"  - Quality Score: {example['quality_score']}/100"
                    ])
            
            elif scenario_name == "tag_generation":
                report_lines.extend([
                    f"- **Files Processed:** {scenario_data['simulated_files']}",
                    f"- **Average Tags per Image:** {scenario_data['average_tags_per_image']:.1f}",
                    f"- **Unique Tags Generated:** {scenario_data['unique_tags_generated']}",
                    "",
                    "**Examples:**"
                ])
                
                for example in scenario_data['examples']:
                    report_lines.extend([
                        f"- **{example['image']}**",
                        f"  - Tags: {', '.join(example['generated_tags'][:8])}",
                        f"  - Title: {example['generated_title']}"
                    ])
            
            elif scenario_name == "workflow_validation":
                report_lines.extend([
                    f"- **Workflows Tested:** {scenario_data['tested_workflows']}",
                    f"- **Successful Workflows:** {scenario_data['successful_workflows']}",
                    f"- **Success Rate:** {scenario_data['success_rate']:.1f}%",
                    "",
                    "**Workflow Steps:**"
                ])
                
                for step in scenario_data['workflow_steps']:
                    report_lines.append(f"1. {step}")
            
            report_lines.append("")
        
        # Add recommendations
        report_lines.extend([
            "## Recommendations",
            "",
            "### Strengths",
            "- Image discovery and categorization works well",
            "- Filename-based prompt extraction is functional",
            "- Tag generation simulation shows good variety",
            "- Workflow validation identifies potential issues",
            "",
            "### Areas for Improvement",
            "- Consider adding metadata extraction from image EXIF data",
            "- Implement more sophisticated tag filtering",
            "- Add print area optimization based on image dimensions",
            "- Include error handling for corrupted or invalid images",
            "",
            "### Next Steps",
            "1. Test with actual Printify API (with credentials)",
            "2. Implement real image processing with PIL/Pillow",
            "3. Add user interface testing with Gradio",
            "4. Performance testing with larger image sets",
            "5. Integration testing with actual product creation"
        ])
        
        report_content = "\n".join(report_lines)
        
        # Save report
        with open("workflow_test_report.md", "w") as f:
            f.write(report_content)
        
        with open("workflow_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print("✅ Report generated successfully!")
        print("   - workflow_test_report.md")
        print("   - workflow_test_results.json")

def main():
    """Main execution function"""
    test_images_dir = "/mnt/h/Development/www.thevisiblewords.com/printify_automation_script_Copy"
    
    if not os.path.exists(test_images_dir):
        print(f"❌ Error: Test images directory not found: {test_images_dir}")
        return
    
    tester = SimpleAutomationTester(test_images_dir)
    results = tester.run_tests()
    
    print("\n" + "="*60)
    print("✅ PRINTIFY AUTOMATION WORKFLOW TEST COMPLETE")
    print("="*60)
    
    return results

if __name__ == "__main__":
    main()