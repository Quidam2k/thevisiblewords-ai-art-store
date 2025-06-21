"""
Multi-Position Print Area Manager
Handles complex print area configurations for different product types and positions
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import math

class PrintPosition(Enum):
    FRONT = "front"
    BACK = "back"
    LEFT_SLEEVE = "left_sleeve"
    RIGHT_SLEEVE = "right_sleeve"
    SLEEVE = "sleeve"
    CHEST = "chest"
    POCKET = "pocket"
    FULL_WRAP = "full_wrap"
    INSIDE = "inside"
    OUTSIDE = "outside"
    TOP = "top"
    BOTTOM = "bottom"
    HANDLE = "handle"

@dataclass
class PrintAreaDimensions:
    """Physical dimensions of a print area"""
    width: int  # pixels
    height: int  # pixels
    x_offset: int = 0  # pixels from left
    y_offset: int = 0  # pixels from top
    dpi: int = 300
    
    @property
    def width_inches(self) -> float:
        return self.width / self.dpi
    
    @property
    def height_inches(self) -> float:
        return self.height / self.dpi

@dataclass
class ImagePlacement:
    """Image placement configuration"""
    x: float  # 0.0 to 1.0 (left to right)
    y: float  # 0.0 to 1.0 (top to bottom)
    scale: float  # scaling factor
    angle: float = 0.0  # rotation angle in degrees
    fit_mode: str = "fill"  # fill, fit, stretch

@dataclass
class PrintAreaConfig:
    """Configuration for a print area"""
    position: PrintPosition
    dimensions: PrintAreaDimensions
    placement: ImagePlacement
    variant_ids: List[int]
    enabled: bool = True
    priority: int = 1  # 1 = highest priority

class PrintAreaManager:
    def __init__(self):
        # Product-specific print area templates
        self.product_templates = self._initialize_product_templates()
        
        # Default placement strategies
        self.placement_strategies = {
            "center": lambda w, h: ImagePlacement(0.5, 0.5, 1.0),
            "top_center": lambda w, h: ImagePlacement(0.5, 0.3, 0.8),
            "bottom_center": lambda w, h: ImagePlacement(0.5, 0.7, 0.8),
            "left_center": lambda w, h: ImagePlacement(0.3, 0.5, 0.8),
            "right_center": lambda w, h: ImagePlacement(0.7, 0.5, 0.8),
            "full_coverage": lambda w, h: ImagePlacement(0.5, 0.5, 1.0, fit_mode="fill"),
            "fit_area": lambda w, h: ImagePlacement(0.5, 0.5, 0.95, fit_mode="fit")
        }

    def _initialize_product_templates(self) -> Dict[str, Dict[PrintPosition, PrintAreaDimensions]]:
        """Initialize print area templates for different product types"""
        return {
            # T-Shirts (Blueprint ID: 384)
            "tshirt": {
                PrintPosition.FRONT: PrintAreaDimensions(3153, 3995, dpi=300),
                PrintPosition.BACK: PrintAreaDimensions(3153, 3995, dpi=300),
                PrintPosition.LEFT_SLEEVE: PrintAreaDimensions(1000, 1000, dpi=300),
                PrintPosition.RIGHT_SLEEVE: PrintAreaDimensions(1000, 1000, dpi=300),
                PrintPosition.POCKET: PrintAreaDimensions(800, 800, dpi=300),
            },
            
            # Hoodies
            "hoodie": {
                PrintPosition.FRONT: PrintAreaDimensions(3153, 3995, dpi=300),
                PrintPosition.BACK: PrintAreaDimensions(3153, 3995, dpi=300),
                PrintPosition.LEFT_SLEEVE: PrintAreaDimensions(1200, 1200, dpi=300),
                PrintPosition.RIGHT_SLEEVE: PrintAreaDimensions(1200, 1200, dpi=300),
            },
            
            # Mugs (Blueprint ID: 9)
            "mug": {
                PrintPosition.FULL_WRAP: PrintAreaDimensions(2550, 1050, dpi=300),
                PrintPosition.FRONT: PrintAreaDimensions(1275, 1050, dpi=300),
                PrintPosition.HANDLE: PrintAreaDimensions(400, 800, dpi=300),
            },
            
            # Posters (Blueprint ID: 5)
            "poster": {
                PrintPosition.FRONT: PrintAreaDimensions(3600, 3600, dpi=300),
            },
            
            # Canvas (Blueprint ID: 6)
            "canvas": {
                PrintPosition.FRONT: PrintAreaDimensions(3600, 3600, dpi=300),
            },
            
            # Phone Cases (Blueprint ID: 12)
            "phone_case": {
                PrintPosition.FRONT: PrintAreaDimensions(1800, 3200, dpi=300),
                PrintPosition.BACK: PrintAreaDimensions(1800, 3200, dpi=300),
            },
            
            # Tote Bags
            "tote_bag": {
                PrintPosition.FRONT: PrintAreaDimensions(2400, 2400, dpi=300),
                PrintPosition.BACK: PrintAreaDimensions(2400, 2400, dpi=300),
            },
            
            # Notebooks/Journals
            "notebook": {
                PrintPosition.FRONT: PrintAreaDimensions(2100, 2700, dpi=300),
                PrintPosition.BACK: PrintAreaDimensions(2100, 2700, dpi=300),
                PrintPosition.INSIDE: PrintAreaDimensions(2000, 2600, dpi=300),
            }
        }

    def get_available_positions(self, product_type: str) -> List[PrintPosition]:
        """Get available print positions for a product type"""
        if product_type in self.product_templates:
            return list(self.product_templates[product_type].keys())
        return [PrintPosition.FRONT]  # Default fallback

    def get_print_area_config(self, product_type: str, position: PrintPosition, 
                            variant_ids: List[int], image_width: int, image_height: int,
                            placement_strategy: str = "center") -> PrintAreaConfig:
        """Generate print area configuration for specific position"""
        
        # Get dimensions template
        if product_type in self.product_templates and position in self.product_templates[product_type]:
            dimensions = self.product_templates[product_type][position]
        else:
            # Default dimensions
            dimensions = PrintAreaDimensions(2400, 2400, dpi=300)
        
        # Calculate optimal placement
        placement = self._calculate_optimal_placement(
            image_width, image_height, dimensions, placement_strategy
        )
        
        return PrintAreaConfig(
            position=position,
            dimensions=dimensions,
            placement=placement,
            variant_ids=variant_ids,
            enabled=True,
            priority=self._get_position_priority(position)
        )

    def _calculate_optimal_placement(self, image_width: int, image_height: int,
                                   area_dims: PrintAreaDimensions, strategy: str) -> ImagePlacement:
        """Calculate optimal image placement within print area"""
        
        if strategy in self.placement_strategies:
            base_placement = self.placement_strategies[strategy](image_width, image_height)
        else:
            base_placement = self.placement_strategies["center"](image_width, image_height)
        
        # Calculate optimal scale based on image and area dimensions
        image_ratio = image_width / image_height
        area_ratio = area_dims.width / area_dims.height
        
        if base_placement.fit_mode == "fit":
            # Fit entire image within area
            if image_ratio > area_ratio:
                # Image is wider - fit to width
                scale = 0.95
            else:
                # Image is taller - fit to height
                scale = 0.95
        elif base_placement.fit_mode == "fill":
            # Fill entire area (may crop image)
            if image_ratio > area_ratio:
                # Image is wider - fill height
                scale = 1.0
            else:
                # Image is taller - fill width
                scale = 1.0
        else:
            # Use specified scale
            scale = base_placement.scale
        
        return ImagePlacement(
            x=base_placement.x,
            y=base_placement.y,
            scale=scale,
            angle=base_placement.angle,
            fit_mode=base_placement.fit_mode
        )

    def _get_position_priority(self, position: PrintPosition) -> int:
        """Get priority for print position (1 = highest)"""
        priority_map = {
            PrintPosition.FRONT: 1,
            PrintPosition.BACK: 2,
            PrintPosition.CHEST: 3,
            PrintPosition.POCKET: 4,
            PrintPosition.LEFT_SLEEVE: 5,
            PrintPosition.RIGHT_SLEEVE: 6,
            PrintPosition.FULL_WRAP: 1,
            PrintPosition.INSIDE: 7,
            PrintPosition.HANDLE: 8
        }
        return priority_map.get(position, 9)

    def create_multi_position_product(self, product_type: str, variant_ids: List[int],
                                    image_width: int, image_height: int,
                                    enabled_positions: List[PrintPosition] = None,
                                    placement_strategy: str = "center") -> List[Dict[str, Any]]:
        """Create print areas for multiple positions"""
        
        if enabled_positions is None:
            # Use default positions based on product type
            enabled_positions = self._get_default_positions(product_type)
        
        print_areas = []
        
        for position in enabled_positions:
            config = self.get_print_area_config(
                product_type, position, variant_ids, 
                image_width, image_height, placement_strategy
            )
            
            # Convert to API format
            print_area = {
                "variant_ids": config.variant_ids,
                "placeholders": [
                    {
                        "position": config.position.value,
                        "images": [
                            {
                                "x": config.placement.x,
                                "y": config.placement.y,
                                "scale": config.placement.scale,
                                "angle": config.placement.angle
                            }
                        ]
                    }
                ]
            }
            print_areas.append(print_area)
        
        return print_areas

    def _get_default_positions(self, product_type: str) -> List[PrintPosition]:
        """Get default print positions for product type"""
        defaults = {
            "tshirt": [PrintPosition.FRONT],
            "hoodie": [PrintPosition.FRONT],
            "mug": [PrintPosition.FRONT],
            "poster": [PrintPosition.FRONT],
            "canvas": [PrintPosition.FRONT],
            "phone_case": [PrintPosition.FRONT],
            "tote_bag": [PrintPosition.FRONT],
            "notebook": [PrintPosition.FRONT]
        }
        
        return defaults.get(product_type, [PrintPosition.FRONT])

    def get_position_recommendations(self, image_width: int, image_height: int,
                                   product_type: str) -> Dict[PrintPosition, Dict[str, Any]]:
        """Get position recommendations based on image characteristics"""
        recommendations = {}
        available_positions = self.get_available_positions(product_type)
        
        image_ratio = image_width / image_height
        
        for position in available_positions:
            if product_type in self.product_templates:
                area_dims = self.product_templates[product_type][position]
                area_ratio = area_dims.width / area_dims.height
                
                # Calculate compatibility score
                ratio_diff = abs(image_ratio - area_ratio)
                compatibility = max(0, 1 - ratio_diff)
                
                # Determine best strategy
                if ratio_diff < 0.2:
                    strategy = "center"
                elif image_ratio > area_ratio:
                    strategy = "fit_area"
                else:
                    strategy = "center"
                
                recommendations[position] = {
                    "compatibility_score": compatibility,
                    "recommended_strategy": strategy,
                    "area_dimensions": asdict(area_dims),
                    "notes": self._get_position_notes(position, image_ratio, area_ratio)
                }
        
        return recommendations

    def _get_position_notes(self, position: PrintPosition, image_ratio: float, area_ratio: float) -> str:
        """Get helpful notes for position selection"""
        if position == PrintPosition.FRONT:
            if image_ratio > 1.5:
                return "Wide image - consider landscape orientation"
            elif image_ratio < 0.7:
                return "Tall image - good for portrait designs"
            else:
                return "Square-ish image - ideal for front placement"
        
        elif position == PrintPosition.FULL_WRAP:
            return "Panoramic image recommended for wrap-around effect"
        
        elif position in [PrintPosition.LEFT_SLEEVE, PrintPosition.RIGHT_SLEEVE]:
            return "Small area - simple designs work best"
        
        elif position == PrintPosition.POCKET:
            return "Tiny area - logos and simple graphics only"
        
        else:
            return "Standard placement area"

    def optimize_for_multiple_positions(self, image_width: int, image_height: int,
                                      product_type: str, max_positions: int = 3) -> List[PrintPosition]:
        """Optimize image for multiple print positions"""
        recommendations = self.get_position_recommendations(image_width, image_height, product_type)
        
        # Sort by compatibility score
        sorted_positions = sorted(
            recommendations.items(),
            key=lambda x: x[1]["compatibility_score"],
            reverse=True
        )
        
        # Return top positions up to max_positions
        return [pos for pos, _ in sorted_positions[:max_positions]]

    def create_position_preview_data(self, product_type: str, position: PrintPosition) -> Dict[str, Any]:
        """Create data for position preview in UI"""
        if product_type in self.product_templates and position in self.product_templates[product_type]:
            dims = self.product_templates[product_type][position]
            
            return {
                "position": position.value,
                "width_inches": dims.width_inches,
                "height_inches": dims.height_inches,
                "width_pixels": dims.width,
                "height_pixels": dims.height,
                "dpi": dims.dpi,
                "area_description": self._get_area_description(position),
                "placement_tips": self._get_placement_tips(position)
            }
        
        return {}

    def _get_area_description(self, position: PrintPosition) -> str:
        """Get human-readable description of print area"""
        descriptions = {
            PrintPosition.FRONT: "Main front design area",
            PrintPosition.BACK: "Full back design area",
            PrintPosition.LEFT_SLEEVE: "Left sleeve design area",
            PrintPosition.RIGHT_SLEEVE: "Right sleeve design area",
            PrintPosition.POCKET: "Small pocket area",
            PrintPosition.CHEST: "Upper chest area",
            PrintPosition.FULL_WRAP: "Full wrap-around design",
            PrintPosition.HANDLE: "Handle area (mugs)",
            PrintPosition.INSIDE: "Inside cover (notebooks)"
        }
        return descriptions.get(position, "Design area")

    def _get_placement_tips(self, position: PrintPosition) -> List[str]:
        """Get placement tips for specific position"""
        tips = {
            PrintPosition.FRONT: [
                "Center placement works best for most designs",
                "Leave margin for hem and collar",
                "Consider garment color when designing"
            ],
            PrintPosition.BACK: [
                "Larger designs can work well here",
                "Avoid text that needs to be read",
                "Consider shoulder seam placement"
            ],
            PrintPosition.LEFT_SLEEVE: [
                "Keep designs simple and bold",
                "Avoid fine details",
                "Consider arm movement"
            ],
            PrintPosition.POCKET: [
                "Logos and simple graphics only",
                "High contrast designs work best",
                "Keep text minimal"
            ],
            PrintPosition.FULL_WRAP: [
                "Design should work as continuous image",
                "Mind the seam placement",
                "Test with handle visibility"
            ]
        }
        return tips.get(position, ["Follow general design guidelines"])

# Example usage
if __name__ == "__main__":
    manager = PrintAreaManager()
    
    # Test position recommendations
    recommendations = manager.get_position_recommendations(2000, 2000, "tshirt")
    print("Position recommendations for square image:")
    for pos, rec in recommendations.items():
        print(f"  {pos.value}: {rec['compatibility_score']:.2f} - {rec['recommended_strategy']}")
    
    # Test multi-position product creation
    print_areas = manager.create_multi_position_product(
        "tshirt", [12345, 12346], 2000, 2000, 
        [PrintPosition.FRONT, PrintPosition.BACK]
    )
    print(f"\nCreated {len(print_areas)} print areas")
    
    # Test optimization
    optimal_positions = manager.optimize_for_multiple_positions(3000, 1500, "tshirt")
    print(f"\nOptimal positions for wide image: {[p.value for p in optimal_positions]}")