"""
Enhanced Configuration Manager for Printify Automation
Handles pricing, product settings, and advanced configuration options
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class PricingTier:
    """Pricing configuration for different product types"""
    base_price: int  # Price in cents
    markup_percentage: float  # Additional markup as percentage
    min_price: int  # Minimum price in cents
    max_price: int  # Maximum price in cents

@dataclass
class ProductSettings:
    """Product-specific settings"""
    blueprint_id: int
    name: str
    category: str
    pricing_tier: str
    print_positions: List[str]  # e.g., ['front', 'back']
    default_variants: List[int]  # Default variant IDs to enable
    image_requirements: Dict[str, Any]  # Size, DPI, etc.

@dataclass
class APISettings:
    """API-related settings"""
    access_token: str
    shop_id: str
    base_url: str = "https://api.printify.com/v1"
    v2_base_url: str = "https://api.printify.com/v2"
    user_agent: str = "Printify-Automation-Tool"
    rate_limit_rpm: int = 600  # Requests per minute
    rate_limit_product_creation: int = 200  # Products per 30 minutes
    retry_attempts: int = 3
    retry_delay: float = 1.0  # Base delay in seconds

@dataclass
class ImageProcessingSettings:
    """Image processing configuration"""
    max_width: int = 4000
    max_height: int = 4000
    quality: int = 90
    format: str = "JPEG"  # Output format
    optimize: bool = True
    auto_orient: bool = True
    strip_metadata: bool = False  # Keep AI prompts in EXIF

@dataclass
class TagSettings:
    """Tag generation settings"""
    max_tags: int = 15
    min_tag_length: int = 3
    include_style_tags: bool = True
    include_color_tags: bool = True
    include_mood_tags: bool = True
    custom_tag_templates: List[str] = None

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config_dir = Path(config_file).parent
        self.ensure_config_directory()
        
        # Default configurations
        self.default_pricing_tiers = {
            "basic": PricingTier(1499, 0.0, 999, 9999),      # $14.99, no markup
            "premium": PricingTier(1999, 15.0, 1499, 4999),  # $19.99, 15% markup
            "luxury": PricingTier(2999, 25.0, 2499, 9999),   # $29.99, 25% markup
            "custom": PricingTier(1999, 10.0, 999, 19999)    # Configurable
        }
        
        self.default_product_settings = [
            ProductSettings(
                blueprint_id=384,
                name="Unisex Heavy Cotton Tee",
                category="apparel",
                pricing_tier="basic",
                print_positions=["front"],
                default_variants=[],
                image_requirements={"min_width": 2400, "min_height": 2400, "dpi": 300}
            ),
            ProductSettings(
                blueprint_id=5,
                name="Premium Poster",
                category="wall-art",
                pricing_tier="premium",
                print_positions=["front"],
                default_variants=[],
                image_requirements={"min_width": 3000, "min_height": 3000, "dpi": 300}
            ),
            ProductSettings(
                blueprint_id=9,
                name="Coffee Mug",
                category="drinkware",
                pricing_tier="basic",
                print_positions=["front"],
                default_variants=[],
                image_requirements={"min_width": 2000, "min_height": 1200, "dpi": 300}
            ),
            ProductSettings(
                blueprint_id=6,
                name="Canvas Print",
                category="wall-art",
                pricing_tier="luxury",
                print_positions=["front"],
                default_variants=[],
                image_requirements={"min_width": 3600, "min_height": 3600, "dpi": 300}
            ),
            ProductSettings(
                blueprint_id=12,
                name="Phone Case",
                category="accessories",
                pricing_tier="premium",
                print_positions=["front"],
                default_variants=[],
                image_requirements={"min_width": 1800, "min_height": 3200, "dpi": 300}
            )
        ]
        
        self.config = self.load_config()

    def ensure_config_directory(self):
        """Ensure the configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return self.merge_with_defaults(config)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading config: {e}. Using defaults.")
                return self.create_default_config()
        else:
            return self.create_default_config()

    def create_default_config(self) -> Dict[str, Any]:
        """Create a default configuration"""
        default_config = {
            "api": asdict(APISettings(
                access_token="",
                shop_id="",
            )),
            "pricing_tiers": {k: asdict(v) for k, v in self.default_pricing_tiers.items()},
            "product_settings": [asdict(ps) for ps in self.default_product_settings],
            "image_processing": asdict(ImageProcessingSettings()),
            "tag_settings": asdict(TagSettings(custom_tag_templates=["ai-art", "digital-art"])),
            "general": {
                "auto_save": True,
                "backup_count": 5,
                "log_level": "INFO",
                "theme": "default"
            }
        }
        
        # Save the default config
        self.save_config(default_config)
        return default_config

    def merge_with_defaults(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults"""
        default_config = self.create_default_config()
        
        # Deep merge the configurations
        def deep_merge(default: Dict, user: Dict) -> Dict:
            result = default.copy()
            for key, value in user.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(default_config, user_config)

    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        # Create backup if file exists
        if os.path.exists(self.config_file):
            backup_file = f"{self.config_file}.backup"
            os.rename(self.config_file, backup_file)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def get_api_settings(self) -> APISettings:
        """Get API settings as a dataclass"""
        api_config = self.config.get("api", {})
        return APISettings(**api_config)

    def get_pricing_tier(self, tier_name: str) -> Optional[PricingTier]:
        """Get pricing tier configuration"""
        tier_config = self.config.get("pricing_tiers", {}).get(tier_name)
        if tier_config:
            return PricingTier(**tier_config)
        return None

    def get_product_settings(self) -> List[ProductSettings]:
        """Get all product settings"""
        product_configs = self.config.get("product_settings", [])
        return [ProductSettings(**config) for config in product_configs]

    def get_image_processing_settings(self) -> ImageProcessingSettings:
        """Get image processing settings"""
        img_config = self.config.get("image_processing", {})
        return ImageProcessingSettings(**img_config)

    def get_tag_settings(self) -> TagSettings:
        """Get tag generation settings"""
        tag_config = self.config.get("tag_settings", {})
        return TagSettings(**tag_config)

    def calculate_price(self, base_price: int, pricing_tier: str) -> int:
        """Calculate final price based on pricing tier"""
        tier = self.get_pricing_tier(pricing_tier)
        if not tier:
            return base_price
        
        # Apply markup
        markup_amount = int(base_price * (tier.markup_percentage / 100))
        final_price = base_price + markup_amount
        
        # Apply min/max constraints
        final_price = max(tier.min_price, min(tier.max_price, final_price))
        
        return final_price

    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check API settings
        api_settings = self.get_api_settings()
        if not api_settings.access_token:
            issues.append("API access token is required")
        if not api_settings.shop_id:
            issues.append("Shop ID is required")
        
        # Check product settings
        product_settings = self.get_product_settings()
        if not product_settings:
            issues.append("At least one product configuration is required")
        
        for product in product_settings:
            if product.blueprint_id <= 0:
                issues.append(f"Invalid blueprint ID for {product.name}")
            
            pricing_tier = self.get_pricing_tier(product.pricing_tier)
            if not pricing_tier:
                issues.append(f"Invalid pricing tier '{product.pricing_tier}' for {product.name}")
        
        return issues

    def is_configured(self) -> bool:
        """Check if the basic configuration is complete"""
        issues = self.validate_config()
        return len(issues) == 0

    def update_api_credentials(self, access_token: str, shop_id: str):
        """Update API credentials"""
        self.config["api"]["access_token"] = access_token
        self.config["api"]["shop_id"] = shop_id
        self.save_config()

    def add_product_setting(self, product_setting: ProductSettings):
        """Add a new product setting"""
        self.config["product_settings"].append(asdict(product_setting))
        self.save_config()

    def remove_product_setting(self, blueprint_id: int):
        """Remove a product setting by blueprint ID"""
        self.config["product_settings"] = [
            ps for ps in self.config["product_settings"]
            if ps["blueprint_id"] != blueprint_id
        ]
        self.save_config()

    def export_config_template(self, filename: str = "config-template.json"):
        """Export a configuration template with explanations"""
        template = {
            "_comment": "Printify Automation Tool Configuration",
            "_instructions": {
                "api": "Get your access token and shop ID from Printify dashboard",
                "pricing_tiers": "Define pricing strategies for different product types",
                "product_settings": "Configure which products to create and their settings",
                "image_processing": "Control how images are optimized before upload",
                "tag_settings": "Customize tag generation behavior"
            },
            "api": {
                "access_token": "YOUR_PRINTIFY_ACCESS_TOKEN_HERE",
                "shop_id": "YOUR_SHOP_ID_HERE",
                "user_agent": "Printify-Automation-Tool",
                "rate_limit_rpm": 600,
                "retry_attempts": 3
            },
            "pricing_tiers": self.config["pricing_tiers"],
            "product_settings": self.config["product_settings"],
            "image_processing": self.config["image_processing"],
            "tag_settings": self.config["tag_settings"],
            "general": self.config["general"]
        }
        
        with open(filename, 'w') as f:
            json.dump(template, f, indent=4)
        
        return filename

# Example usage
if __name__ == "__main__":
    config_manager = ConfigManager()
    
    # Check configuration status
    if config_manager.is_configured():
        print("✅ Configuration is complete")
    else:
        print("❌ Configuration issues found:")
        for issue in config_manager.validate_config():
            print(f"  - {issue}")
    
    # Example: Calculate price for a product
    price = config_manager.calculate_price(1499, "premium")
    print(f"Premium tier price: ${price/100:.2f}")
    
    # Export template
    template_file = config_manager.export_config_template()
    print(f"Configuration template exported to: {template_file}")