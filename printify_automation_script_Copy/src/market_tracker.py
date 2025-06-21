"""
Market Data Tracker
Tracks competitor pricing and market conditions for competitive pricing strategies
"""

import json
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import statistics
from pathlib import Path

class MarketDataSource(Enum):
    MANUAL = "manual"
    API = "api"
    SCRAPER = "scraper"
    CSV_IMPORT = "csv_import"

class CompetitorTier(Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    PREMIUM = "premium"
    LUXURY = "luxury"

@dataclass
class CompetitorPrice:
    """Competitor pricing data point"""
    competitor_id: str
    competitor_name: str
    product_name: str
    product_category: str
    price: float  # in cents
    currency: str = "USD"
    url: Optional[str] = None
    availability: str = "in_stock"  # in_stock, out_of_stock, limited
    shipping_cost: Optional[float] = None
    timestamp: datetime = None
    source: MarketDataSource = MarketDataSource.MANUAL
    confidence: float = 1.0  # 0.0 to 1.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class MarketSegment:
    """Market segment analysis"""
    category: str
    tier: CompetitorTier
    competitor_count: int
    price_range: Tuple[float, float]  # min, max
    average_price: float
    median_price: float
    price_volatility: float
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()

@dataclass
class PriceInsight:
    """Market insight based on price analysis"""
    insight_type: str
    title: str
    description: str
    impact: str  # low, medium, high
    confidence: float
    recommendation: str
    data_points: int
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class MarketTracker:
    def __init__(self, data_file: str = "market_data.json"):
        self.logger = logging.getLogger(__name__)
        self.data_file = Path(data_file)
        
        # Data storage
        self.competitor_prices: Dict[str, List[CompetitorPrice]] = {}
        self.market_segments: Dict[str, MarketSegment] = {}
        self.insights: List[PriceInsight] = []
        
        # Configuration
        self.tracking_enabled = True
        self.data_retention_days = 90
        self.min_confidence_threshold = 0.7
        self.update_frequency_hours = 24
        
        # Competitor database
        self.competitors = {}
        
        # Threading for background updates
        self._update_thread = None
        self._stop_updating = threading.Event()
        
        # Load existing data
        self.load_data()
        
        # Initialize default competitors
        self._init_default_competitors()

    def _init_default_competitors(self):
        """Initialize default competitor database"""
        self.competitors = {
            "printful": {
                "name": "Printful",
                "tier": CompetitorTier.MID_RANGE,
                "categories": ["apparel", "accessories", "home-decor"],
                "api_available": False,
                "scraping_config": {
                    "base_url": "https://www.printful.com",
                    "rate_limit": 1.0  # seconds between requests
                }
            },
            "gooten": {
                "name": "Gooten",
                "tier": CompetitorTier.BUDGET,
                "categories": ["apparel", "accessories"],
                "api_available": False,
                "scraping_config": {
                    "base_url": "https://www.gooten.com",
                    "rate_limit": 1.0
                }
            },
            "printify_competitors": {
                "name": "Other Printify Sellers",
                "tier": CompetitorTier.MID_RANGE,
                "categories": ["all"],
                "api_available": False,
                "note": "Data from marketplace analysis"
            }
        }

    def add_competitor(self, competitor_id: str, name: str, tier: CompetitorTier, 
                      categories: List[str], config: Dict[str, Any] = None):
        """Add a new competitor to track"""
        self.competitors[competitor_id] = {
            "name": name,
            "tier": tier,
            "categories": categories,
            "config": config or {},
            "added_date": datetime.now().isoformat()
        }
        
        self.logger.info(f"Added competitor: {name} ({competitor_id})")

    def add_price_data(self, competitor_id: str, product_name: str, 
                      product_category: str, price: float, **kwargs) -> bool:
        """Add a price data point"""
        if competitor_id not in self.competitors:
            self.logger.warning(f"Unknown competitor: {competitor_id}")
            return False
        
        competitor_info = self.competitors[competitor_id]
        
        price_point = CompetitorPrice(
            competitor_id=competitor_id,
            competitor_name=competitor_info["name"],
            product_name=product_name,
            product_category=product_category,
            price=price,
            **kwargs
        )
        
        # Store price data
        key = f"{competitor_id}:{product_category}"
        if key not in self.competitor_prices:
            self.competitor_prices[key] = []
        
        self.competitor_prices[key].append(price_point)
        
        # Cleanup old data
        self._cleanup_old_data(key)
        
        # Update market segments
        self._update_market_segment(product_category)
        
        self.logger.info(f"Added price data: {competitor_info['name']} - {product_name}: ${price/100:.2f}")
        return True

    def _cleanup_old_data(self, key: str):
        """Remove old price data beyond retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        
        if key in self.competitor_prices:
            self.competitor_prices[key] = [
                price for price in self.competitor_prices[key]
                if price.timestamp > cutoff_date
            ]

    def _update_market_segment(self, category: str):
        """Update market segment analysis for a category"""
        # Get all prices for this category
        category_prices = []
        competitor_count = 0
        
        for key, prices in self.competitor_prices.items():
            if key.endswith(f":{category}"):
                competitor_count += 1
                # Get recent prices (last 30 days)
                recent_cutoff = datetime.now() - timedelta(days=30)
                recent_prices = [
                    p.price for p in prices 
                    if p.timestamp > recent_cutoff and p.confidence >= self.min_confidence_threshold
                ]
                category_prices.extend(recent_prices)
        
        if not category_prices:
            return
        
        # Calculate statistics
        min_price = min(category_prices)
        max_price = max(category_prices)
        avg_price = statistics.mean(category_prices)
        median_price = statistics.median(category_prices)
        
        # Calculate volatility (standard deviation)
        volatility = statistics.stdev(category_prices) if len(category_prices) > 1 else 0
        
        # Determine tier based on price range
        if avg_price < 1500:  # Under $15
            tier = CompetitorTier.BUDGET
        elif avg_price < 3000:  # $15-30
            tier = CompetitorTier.MID_RANGE
        elif avg_price < 5000:  # $30-50
            tier = CompetitorTier.PREMIUM
        else:  # Over $50
            tier = CompetitorTier.LUXURY
        
        # Update market segment
        self.market_segments[category] = MarketSegment(
            category=category,
            tier=tier,
            competitor_count=competitor_count,
            price_range=(min_price, max_price),
            average_price=avg_price,
            median_price=median_price,
            price_volatility=volatility
        )

    def get_competitive_prices(self, category: str, days: int = 30) -> List[CompetitorPrice]:
        """Get competitive prices for a category"""
        cutoff_date = datetime.now() - timedelta(days=days)
        competitive_prices = []
        
        for key, prices in self.competitor_prices.items():
            if key.endswith(f":{category}"):
                recent_prices = [
                    price for price in prices
                    if price.timestamp > cutoff_date and price.confidence >= self.min_confidence_threshold
                ]
                competitive_prices.extend(recent_prices)
        
        # Sort by timestamp (newest first)
        competitive_prices.sort(key=lambda x: x.timestamp, reverse=True)
        return competitive_prices

    def analyze_price_position(self, my_price: float, category: str) -> Dict[str, Any]:
        """Analyze where my price stands in the market"""
        competitive_prices = self.get_competitive_prices(category)
        
        if not competitive_prices:
            return {
                "error": "No competitive data available",
                "category": category,
                "my_price": my_price
            }
        
        competitor_prices = [p.price for p in competitive_prices]
        
        # Calculate position metrics
        lower_count = sum(1 for p in competitor_prices if p < my_price)
        higher_count = sum(1 for p in competitor_prices if p > my_price)
        equal_count = sum(1 for p in competitor_prices if p == my_price)
        
        total_competitors = len(competitor_prices)
        percentile = (lower_count / total_competitors) * 100 if total_competitors > 0 else 0
        
        # Determine positioning
        if percentile <= 25:
            position = "budget"
            competitiveness = "very_competitive"
        elif percentile <= 50:
            position = "low_mid_range"
            competitiveness = "competitive"
        elif percentile <= 75:
            position = "high_mid_range"
            competitiveness = "moderate"
        else:
            position = "premium"
            competitiveness = "limited"
        
        # Calculate distance to nearest competitors
        sorted_prices = sorted(competitor_prices)
        nearest_lower = max([p for p in sorted_prices if p < my_price], default=None)
        nearest_higher = min([p for p in sorted_prices if p > my_price], default=None)
        
        return {
            "category": category,
            "my_price": my_price,
            "total_competitors": total_competitors,
            "percentile": percentile,
            "position": position,
            "competitiveness": competitiveness,
            "lower_priced_competitors": lower_count,
            "higher_priced_competitors": higher_count,
            "price_range": {
                "min": min(competitor_prices),
                "max": max(competitor_prices),
                "median": statistics.median(competitor_prices),
                "average": statistics.mean(competitor_prices)
            },
            "nearest_competitors": {
                "lower": nearest_lower,
                "higher": nearest_higher,
                "gap_to_lower": my_price - nearest_lower if nearest_lower else None,
                "gap_to_higher": nearest_higher - my_price if nearest_higher else None
            },
            "data_freshness_days": (datetime.now() - min(p.timestamp for p in competitive_prices)).days
        }

    def find_pricing_opportunities(self, category: str) -> List[PriceInsight]:
        """Find pricing opportunities based on market analysis"""
        insights = []
        competitive_prices = self.get_competitive_prices(category)
        
        if len(competitive_prices) < 3:
            return insights
        
        prices = [p.price for p in competitive_prices]
        sorted_prices = sorted(prices)
        
        # Look for price gaps
        for i in range(1, len(sorted_prices)):
            gap = sorted_prices[i] - sorted_prices[i-1]
            gap_percent = (gap / sorted_prices[i-1]) * 100
            
            if gap_percent > 25:  # Significant gap
                insights.append(PriceInsight(
                    insight_type="price_gap",
                    title=f"Price Gap Opportunity in {category}",
                    description=f"Gap of ${gap/100:.2f} ({gap_percent:.1f}%) between ${sorted_prices[i-1]/100:.2f} and ${sorted_prices[i]/100:.2f}",
                    impact="medium",
                    confidence=0.8,
                    recommendation=f"Consider pricing between ${sorted_prices[i-1]/100:.2f} and ${sorted_prices[i]/100:.2f}",
                    data_points=len(competitive_prices)
                ))
        
        # Look for market concentration
        if len(set(prices)) / len(prices) < 0.5:  # Many similar prices
            mode_price = statistics.mode(prices)
            insights.append(PriceInsight(
                insight_type="price_clustering",
                title=f"Price Clustering in {category}",
                description=f"Many competitors clustered around ${mode_price/100:.2f}",
                impact="high",
                confidence=0.9,
                recommendation="Differentiate with value proposition or find price gap",
                data_points=len(competitive_prices)
            ))
        
        # Look for recent price movements
        recent_prices = [p for p in competitive_prices if p.timestamp > datetime.now() - timedelta(days=7)]
        if len(recent_prices) >= 2:
            old_prices = [p for p in competitive_prices 
                         if datetime.now() - timedelta(days=14) < p.timestamp <= datetime.now() - timedelta(days=7)]
            
            if old_prices:
                recent_avg = statistics.mean([p.price for p in recent_prices])
                old_avg = statistics.mean([p.price for p in old_prices])
                change_percent = ((recent_avg - old_avg) / old_avg) * 100
                
                if abs(change_percent) > 5:
                    direction = "increasing" if change_percent > 0 else "decreasing"
                    insights.append(PriceInsight(
                        insight_type="market_trend",
                        title=f"Market Prices {direction.title()} in {category}",
                        description=f"Average competitor prices {direction} by {abs(change_percent):.1f}% in last week",
                        impact="high",
                        confidence=0.7,
                        recommendation=f"Monitor trend and consider {'increasing' if change_percent > 0 else 'decreasing'} prices",
                        data_points=len(recent_prices) + len(old_prices)
                    ))
        
        return insights

    def get_market_summary(self, category: str = None) -> Dict[str, Any]:
        """Get market summary for category or all categories"""
        if category:
            categories = [category]
        else:
            categories = list(set(key.split(':')[1] for key in self.competitor_prices.keys()))
        
        summary = {
            "categories": {},
            "total_competitors": len(self.competitors),
            "total_data_points": sum(len(prices) for prices in self.competitor_prices.values()),
            "last_updated": datetime.now().isoformat()
        }
        
        for cat in categories:
            competitive_prices = self.get_competitive_prices(cat)
            
            if competitive_prices:
                prices = [p.price for p in competitive_prices]
                
                summary["categories"][cat] = {
                    "competitor_count": len(set(p.competitor_id for p in competitive_prices)),
                    "data_points": len(competitive_prices),
                    "price_range": {
                        "min": min(prices),
                        "max": max(prices),
                        "average": statistics.mean(prices),
                        "median": statistics.median(prices)
                    },
                    "volatility": statistics.stdev(prices) if len(prices) > 1 else 0,
                    "freshness_hours": (datetime.now() - max(p.timestamp for p in competitive_prices)).total_seconds() / 3600
                }
                
                # Add market segment if available
                if cat in self.market_segments:
                    segment = self.market_segments[cat]
                    summary["categories"][cat]["segment"] = {
                        "tier": segment.tier.value,
                        "competitor_count": segment.competitor_count,
                        "last_analysis": segment.last_updated.isoformat()
                    }
        
        return summary

    def import_csv_data(self, file_path: str) -> int:
        """Import competitor price data from CSV file"""
        import csv
        
        imported_count = 0
        
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        success = self.add_price_data(
                            competitor_id=row.get('competitor_id', 'unknown'),
                            product_name=row.get('product_name', 'Unknown Product'),
                            product_category=row.get('category', 'general'),
                            price=float(row.get('price', 0)) * 100,  # Convert to cents
                            url=row.get('url'),
                            availability=row.get('availability', 'in_stock'),
                            source=MarketDataSource.CSV_IMPORT,
                            confidence=float(row.get('confidence', 1.0))
                        )
                        
                        if success:
                            imported_count += 1
                            
                    except (ValueError, KeyError) as e:
                        self.logger.warning(f"Skipping invalid row: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Failed to import CSV data: {e}")
            return 0
        
        self.logger.info(f"Imported {imported_count} price data points from {file_path}")
        self.save_data()
        return imported_count

    def export_data(self, file_path: str, category: str = None, days: int = 30):
        """Export market data to JSON file"""
        if category:
            data = {
                "category": category,
                "prices": [asdict(p) for p in self.get_competitive_prices(category, days)],
                "market_segment": asdict(self.market_segments[category]) if category in self.market_segments else None
            }
        else:
            data = {
                "competitors": self.competitors,
                "market_segments": {k: asdict(v) for k, v in self.market_segments.items()},
                "all_prices": {k: [asdict(p) for p in v] for k, v in self.competitor_prices.items()},
                "export_date": datetime.now().isoformat()
            }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        self.logger.info(f"Exported market data to {file_path}")

    def save_data(self):
        """Save market data to file"""
        try:
            data = {
                "competitors": self.competitors,
                "competitor_prices": {},
                "market_segments": {},
                "insights": [asdict(insight) for insight in self.insights],
                "last_saved": datetime.now().isoformat()
            }
            
            # Convert competitor prices to serializable format
            for key, prices in self.competitor_prices.items():
                data["competitor_prices"][key] = [
                    {
                        **asdict(price),
                        "timestamp": price.timestamp.isoformat(),
                        "source": price.source.value,
                        "tier": price.competitor_id  # Keep reference
                    }
                    for price in prices
                ]
            
            # Convert market segments
            for key, segment in self.market_segments.items():
                data["market_segments"][key] = {
                    **asdict(segment),
                    "tier": segment.tier.value,
                    "last_updated": segment.last_updated.isoformat()
                }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save market data: {e}")

    def load_data(self):
        """Load market data from file"""
        try:
            if not self.data_file.exists():
                return
            
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Load competitors
            self.competitors = data.get("competitors", {})
            
            # Load competitor prices
            for key, price_data in data.get("competitor_prices", {}).items():
                prices = []
                for price_dict in price_data:
                    price = CompetitorPrice(
                        competitor_id=price_dict["competitor_id"],
                        competitor_name=price_dict["competitor_name"],
                        product_name=price_dict["product_name"],
                        product_category=price_dict["product_category"],
                        price=price_dict["price"],
                        currency=price_dict.get("currency", "USD"),
                        url=price_dict.get("url"),
                        availability=price_dict.get("availability", "in_stock"),
                        shipping_cost=price_dict.get("shipping_cost"),
                        timestamp=datetime.fromisoformat(price_dict["timestamp"]),
                        source=MarketDataSource(price_dict.get("source", "manual")),
                        confidence=price_dict.get("confidence", 1.0)
                    )
                    prices.append(price)
                
                self.competitor_prices[key] = prices
            
            # Load market segments
            for key, segment_data in data.get("market_segments", {}).items():
                segment = MarketSegment(
                    category=segment_data["category"],
                    tier=CompetitorTier(segment_data["tier"]),
                    competitor_count=segment_data["competitor_count"],
                    price_range=tuple(segment_data["price_range"]),
                    average_price=segment_data["average_price"],
                    median_price=segment_data["median_price"],
                    price_volatility=segment_data["price_volatility"],
                    last_updated=datetime.fromisoformat(segment_data["last_updated"])
                )
                self.market_segments[key] = segment
            
            # Load insights
            for insight_data in data.get("insights", []):
                insight = PriceInsight(
                    insight_type=insight_data["insight_type"],
                    title=insight_data["title"],
                    description=insight_data["description"],
                    impact=insight_data["impact"],
                    confidence=insight_data["confidence"],
                    recommendation=insight_data["recommendation"],
                    data_points=insight_data["data_points"],
                    timestamp=datetime.fromisoformat(insight_data["timestamp"])
                )
                self.insights.append(insight)
                
        except Exception as e:
            self.logger.error(f"Failed to load market data: {e}")


# Example usage
if __name__ == "__main__":
    # Initialize market tracker
    tracker = MarketTracker()
    
    # Add some sample competitor data
    tracker.add_price_data(
        competitor_id="printful",
        product_name="Unisex T-Shirt",
        product_category="apparel",
        price=1595,  # $15.95
        url="https://example.com/product"
    )
    
    tracker.add_price_data(
        competitor_id="gooten",
        product_name="Basic T-Shirt",
        product_category="apparel",
        price=1299,  # $12.99
    )
    
    # Analyze position of my price
    position = tracker.analyze_price_position(1999, "apparel")  # My price: $19.99
    print(f"My price position: {position}")
    
    # Find opportunities
    opportunities = tracker.find_pricing_opportunities("apparel")
    for opp in opportunities:
        print(f"Opportunity: {opp.title} - {opp.recommendation}")
    
    # Get market summary
    summary = tracker.get_market_summary("apparel")
    print(f"Market summary: {summary}")