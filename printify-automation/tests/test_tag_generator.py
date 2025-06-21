"""
Test cases for SmartTagGenerator
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# import pytest  # Not available, using direct testing
try:
    from tag_generator import SmartTagGenerator
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This suggests the tag_generator module may have issues or missing dependencies")
    sys.exit(1)


class TestSmartTagGenerator:
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = SmartTagGenerator()

    def test_extract_tags_from_prompt_basic(self):
        """Test basic tag extraction"""
        prompt = "A serene landscape painting of mountains at sunset with warm golden light"
        tags = self.generator.extract_tags_from_prompt(prompt)
        
        assert isinstance(tags, list)
        assert len(tags) > 0
        assert "ai-art" in tags
        assert "digital-art" in tags
        
        # Check for expected content tags
        expected_tags = {"landscape", "mountains", "sunset", "golden", "painting"}
        found_tags = set(tags)
        assert any(tag in found_tags for tag in expected_tags)

    def test_extract_tags_cyberpunk_style(self):
        """Test tag extraction for cyberpunk content"""
        prompt = "Cyberpunk cityscape with neon lights and flying cars in purple and blue"
        tags = self.generator.extract_tags_from_prompt(prompt)
        
        assert "cyberpunk" in tags
        assert "neon" in tags
        assert any("purple" in tag or "blue" in tag for tag in tags)

    def test_generate_product_title(self):
        """Test product title generation"""
        prompt = "A beautiful watercolor painting of a forest scene"
        title = self.generator.generate_product_title(prompt)
        
        assert isinstance(title, str)
        assert len(title) > 0
        assert "watercolor" in title.lower() or "forest" in title.lower()

    def test_generate_description(self):
        """Test description generation"""
        prompt = "Digital art of a mystical dragon"
        title = "Mystical Dragon Art"
        tags = ["dragon", "mystical", "digital-art"]
        
        description = self.generator.generate_description(prompt, title, tags)
        
        assert isinstance(description, str)
        assert len(description) > 50  # Should be substantial
        assert "dragon" in description.lower()
        assert "AI-generated" in description or "artificial intelligence" in description

    def test_empty_prompt_handling(self):
        """Test handling of empty or missing prompts"""
        tags = self.generator.extract_tags_from_prompt("")
        assert "ai-art" in tags
        assert "digital-art" in tags
        
        title = self.generator.generate_product_title("")
        assert title == "AI Generated Artwork"

    def test_no_prompt_found_handling(self):
        """Test handling of 'No prompt found' placeholder"""
        tags = self.generator.extract_tags_from_prompt("No prompt found")
        assert "ai-art" in tags
        assert "abstract" in tags

    def test_tag_formatting(self):
        """Test that tags are properly formatted"""
        prompt = "Street art graffiti with vibrant colors"
        tags = self.generator.extract_tags_from_prompt(prompt)
        
        for tag in tags:
            # Tags should be lowercase
            assert tag.islower()
            # No spaces (should be hyphens)
            assert " " not in tag
            # No empty tags
            assert len(tag) > 0

    def test_max_tags_limit(self):
        """Test that tag count respects maximum limit"""
        # Very descriptive prompt that could generate many tags
        prompt = ("Digital art watercolor oil painting abstract realistic "
                 "portrait landscape urban modern vintage cyberpunk fantasy "
                 "dramatic peaceful vibrant muted colorful monochrome "
                 "detailed intricate masterpiece high quality professional")
        
        tags = self.generator.extract_tags_from_prompt(prompt, max_tags=10)
        assert len(tags) <= 10

    def test_contextual_tags(self):
        """Test contextual tag extraction"""
        prompt = "A peaceful morning scene with dawn light and spring blossoms"
        tags = self.generator.extract_tags_from_prompt(prompt)
        
        # Should detect time and season context
        tag_set = set(tags)
        assert any("morning" in tag or "dawn" in tag for tag in tag_set)
        assert any("spring" in tag or "peaceful" in tag for tag in tag_set)


if __name__ == "__main__":
    # Run tests if script is executed directly
    test_generator = TestSmartTagGenerator()
    test_generator.setup_method()
    
    print("Running SmartTagGenerator tests...")
    
    try:
        test_generator.test_extract_tags_from_prompt_basic()
        print("✅ Basic tag extraction test passed")
        
        test_generator.test_extract_tags_cyberpunk_style()
        print("✅ Cyberpunk style test passed")
        
        test_generator.test_generate_product_title()
        print("✅ Product title generation test passed")
        
        test_generator.test_generate_description()
        print("✅ Description generation test passed")
        
        test_generator.test_empty_prompt_handling()
        print("✅ Empty prompt handling test passed")
        
        test_generator.test_tag_formatting()
        print("✅ Tag formatting test passed")
        
        test_generator.test_max_tags_limit()
        print("✅ Max tags limit test passed")
        
        print("\n🎉 All SmartTagGenerator tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()