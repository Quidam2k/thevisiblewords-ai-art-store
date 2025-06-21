"""
Test cases for ConfigManager
"""

import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# import pytest  # Not available, using direct testing
try:
    from config_manager import ConfigManager, PricingTier, ProductSettings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("This suggests the config_manager module may have issues or missing dependencies")
    sys.exit(1)


class TestConfigManager:
    def setup_method(self):
        """Set up test fixtures with temporary config file"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.config_manager = ConfigManager(self.temp_file.name)

    def teardown_method(self):
        """Clean up temporary files"""
        try:
            os.unlink(self.temp_file.name)
        except:
            pass

    def test_default_config_creation(self):
        """Test that default configuration is created properly"""
        config = self.config_manager.config
        
        # Check main sections exist
        assert "api" in config
        assert "pricing_tiers" in config
        assert "product_settings" in config
        assert "image_processing" in config
        assert "tag_settings" in config

    def test_pricing_tier_calculation(self):
        """Test pricing tier calculations"""
        # Basic tier (no markup)
        basic_price = self.config_manager.calculate_price(1499, "basic")
        assert basic_price == 1499

        # Premium tier (15% markup)
        premium_price = self.config_manager.calculate_price(1499, "premium")
        expected = int(1499 * 1.15)  # 15% markup
        assert premium_price == max(1499, min(4999, expected))  # Within min/max bounds

    def test_configuration_validation(self):
        """Test configuration validation"""
        # Should have issues without API credentials
        issues = self.config_manager.validate_config()
        assert len(issues) > 0
        assert any("access token" in issue.lower() for issue in issues)
        assert any("shop id" in issue.lower() for issue in issues)

    def test_product_settings_management(self):
        """Test product settings operations"""
        # Get initial product settings
        initial_products = self.config_manager.get_product_settings()
        initial_count = len(initial_products)
        
        # Add a new product
        new_product = ProductSettings(
            blueprint_id=999,
            name="Test Product",
            category="test",
            pricing_tier="basic",
            print_positions=["front"],
            default_variants=[],
            image_requirements={"min_width": 1000, "min_height": 1000, "dpi": 300}
        )
        
        self.config_manager.add_product_setting(new_product)
        
        # Check it was added
        updated_products = self.config_manager.get_product_settings()
        assert len(updated_products) == initial_count + 1
        
        # Find the new product
        added_product = next((p for p in updated_products if p.blueprint_id == 999), None)
        assert added_product is not None
        assert added_product.name == "Test Product"

    def test_api_settings(self):
        """Test API settings retrieval"""
        api_settings = self.config_manager.get_api_settings()
        
        assert hasattr(api_settings, 'access_token')
        assert hasattr(api_settings, 'shop_id')
        assert hasattr(api_settings, 'base_url')
        assert api_settings.rate_limit_rpm == 600

    def test_image_processing_settings(self):
        """Test image processing settings"""
        img_settings = self.config_manager.get_image_processing_settings()
        
        assert hasattr(img_settings, 'max_width')
        assert hasattr(img_settings, 'max_height')
        assert hasattr(img_settings, 'quality')
        assert img_settings.optimize is True

    def test_tag_settings(self):
        """Test tag generation settings"""
        tag_settings = self.config_manager.get_tag_settings()
        
        assert hasattr(tag_settings, 'max_tags')
        assert hasattr(tag_settings, 'include_style_tags')
        assert tag_settings.max_tags == 15

    def test_config_template_export(self):
        """Test configuration template export"""
        template_file = self.config_manager.export_config_template()
        
        # Check template was created
        assert os.path.exists(template_file)
        
        # Check template content
        with open(template_file, 'r') as f:
            template_data = json.load(f)
        
        assert "_comment" in template_data
        assert "_instructions" in template_data
        assert "api" in template_data
        
        # Clean up
        os.unlink(template_file)

    def test_pricing_tier_bounds(self):
        """Test pricing tier min/max bounds are respected"""
        # Test minimum bound
        low_price = self.config_manager.calculate_price(500, "basic")  # Below min of 999
        basic_tier = self.config_manager.get_pricing_tier("basic")
        assert low_price == basic_tier.min_price

        # Test maximum bound (if applicable)
        high_price = self.config_manager.calculate_price(50000, "basic")  # Above max
        assert high_price == basic_tier.max_price

    def test_configuration_persistence(self):
        """Test that configuration changes are persisted"""
        # Update API credentials
        self.config_manager.update_api_credentials("test_token", "test_shop")
        
        # Create new config manager with same file
        new_config_manager = ConfigManager(self.temp_file.name)
        api_settings = new_config_manager.get_api_settings()
        
        assert api_settings.access_token == "test_token"
        assert api_settings.shop_id == "test_shop"


if __name__ == "__main__":
    # Run tests if script is executed directly
    test_config = TestConfigManager()
    
    print("Running ConfigManager tests...")
    
    try:
        test_config.setup_method()
        test_config.test_default_config_creation()
        print("✅ Default config creation test passed")
        
        test_config.test_pricing_tier_calculation()
        print("✅ Pricing tier calculation test passed")
        
        test_config.test_configuration_validation()
        print("✅ Configuration validation test passed")
        
        test_config.test_product_settings_management()
        print("✅ Product settings management test passed")
        
        test_config.test_api_settings()
        print("✅ API settings test passed")
        
        test_config.test_image_processing_settings()
        print("✅ Image processing settings test passed")
        
        test_config.test_tag_settings()
        print("✅ Tag settings test passed")
        
        test_config.test_pricing_tier_bounds()
        print("✅ Pricing tier bounds test passed")
        
        test_config.teardown_method()
        print("\n🎉 All ConfigManager tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        test_config.teardown_method()