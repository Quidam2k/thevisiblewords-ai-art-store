"""
Advanced Pricing Monitor System
Tracks cost changes, profit margins, and market conditions for dynamic pricing
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path

class PriceChangeReason(Enum):
    COST_INCREASE = "cost_increase"
    COST_DECREASE = "cost_decrease"
    MARKET_COMPETITION = "market_competition"
    DEMAND_SURGE = "demand_surge"
    DEMAND_DROP = "demand_drop"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    SEASONAL_ADJUSTMENT = "seasonal_adjustment"
    PROMOTION = "promotion"

class PriceDirection(Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"

@dataclass
class CostData:
    """Cost information for a product variant"""
    variant_id: int
    base_cost: float  # Provider's base cost in cents
    shipping_cost: float  # Shipping cost in cents
    processing_fee: float  # Printify processing fee in cents
    total_cost: float  # Total cost to produce in cents
    currency: str = "USD"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Auto-calculate total if not provided
        if self.total_cost == 0:
            self.total_cost = self.base_cost + self.shipping_cost + self.processing_fee

@dataclass
class PricePoint:
    """Historical price point"""
    product_id: str
    variant_id: int
    selling_price: float  # Current selling price in cents
    cost_data: CostData
    profit_margin: float  # Profit margin percentage
    profit_amount: float  # Profit amount in cents
    timestamp: datetime = None
    reason: PriceChangeReason = PriceChangeReason.MANUAL_ADJUSTMENT
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        
        # Auto-calculate profit metrics
        if self.profit_amount == 0:
            self.profit_amount = self.selling_price - self.cost_data.total_cost
        
        if self.profit_margin == 0 and self.selling_price > 0:
            self.profit_margin = (self.profit_amount / self.selling_price) * 100

@dataclass
class PriceAlert:
    """Price change alert"""
    product_id: str
    variant_id: int
    alert_type: str  # "cost_increase", "margin_below_threshold", "competitor_price_drop"
    old_value: float
    new_value: float
    threshold: float
    severity: str  # "low", "medium", "high", "critical"
    message: str
    timestamp: datetime = None
    acknowledged: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class PricingMonitor:
    def __init__(self, data_file: str = "pricing_data.json", alert_file: str = "price_alerts.json"):
        self.logger = logging.getLogger(__name__)
        self.data_file = Path(data_file)
        self.alert_file = Path(alert_file)
        
        # Configuration
        self.monitoring_enabled = True
        self.check_interval = 3600  # Check every hour
        self.cost_increase_threshold = 5.0  # 5% increase triggers alert
        self.margin_threshold = 20.0  # Minimum 20% profit margin
        self.price_history_days = 90  # Keep 90 days of price history
        
        # Data storage
        self.price_history: Dict[str, List[PricePoint]] = {}
        self.current_costs: Dict[str, CostData] = {}
        self.active_alerts: List[PriceAlert] = []
        self.pricing_rules: Dict[str, Any] = {}
        
        # Threading
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()
        
        # Load existing data
        self.load_data()
        self.load_alerts()
        
        # Initialize default pricing rules
        self._init_default_rules()

    def _init_default_rules(self):
        """Initialize default pricing rules"""
        self.pricing_rules = {
            "min_profit_margin": 20.0,  # Minimum 20% profit margin
            "max_profit_margin": 80.0,  # Maximum 80% profit margin
            "cost_increase_reaction": {
                "threshold": 5.0,  # React to 5%+ cost increases
                "pass_through_rate": 0.8,  # Pass through 80% of cost increase
                "delay_hours": 24  # Wait 24 hours before adjusting
            },
            "cost_decrease_reaction": {
                "threshold": 10.0,  # React to 10%+ cost decreases
                "pass_through_rate": 0.5,  # Pass through 50% of cost decrease
                "delay_hours": 72  # Wait 72 hours before adjusting
            },
            "market_adjustment": {
                "enabled": True,
                "check_competitors": True,
                "max_adjustment": 15.0  # Max 15% price adjustment
            },
            "seasonal_factors": {
                "holiday_markup": 10.0,  # 10% markup during holidays
                "summer_discount": 5.0,  # 5% discount in summer
                "back_to_school_markup": 15.0  # 15% markup in fall
            }
        }

    def track_cost_change(self, product_id: str, variant_id: int, new_cost_data: CostData) -> Optional[PriceAlert]:
        """Track a cost change and generate alerts if needed"""
        cost_key = f"{product_id}:{variant_id}"
        
        # Get previous cost data
        old_cost_data = self.current_costs.get(cost_key)
        
        # Update current costs
        self.current_costs[cost_key] = new_cost_data
        
        if old_cost_data is None:
            # First time tracking this product
            self.logger.info(f"Started tracking costs for {product_id}:{variant_id}")
            return None
        
        # Calculate cost change percentage
        cost_change = ((new_cost_data.total_cost - old_cost_data.total_cost) / old_cost_data.total_cost) * 100
        
        if abs(cost_change) < 1.0:
            # Less than 1% change, ignore
            return None
        
        # Determine alert severity
        severity = self._determine_cost_alert_severity(cost_change)
        
        # Create alert
        alert_type = "cost_increase" if cost_change > 0 else "cost_decrease"
        alert = PriceAlert(
            product_id=product_id,
            variant_id=variant_id,
            alert_type=alert_type,
            old_value=old_cost_data.total_cost,
            new_value=new_cost_data.total_cost,
            threshold=self.cost_increase_threshold,
            severity=severity,
            message=f"Cost {alert_type.replace('_', ' ')} of {abs(cost_change):.1f}% detected"
        )
        
        self.active_alerts.append(alert)
        self.save_alerts()
        
        self.logger.warning(f"Cost change alert: {alert.message} for {product_id}:{variant_id}")
        
        return alert

    def _determine_cost_alert_severity(self, cost_change_percent: float) -> str:
        """Determine alert severity based on cost change percentage"""
        abs_change = abs(cost_change_percent)
        
        if abs_change >= 25.0:
            return "critical"
        elif abs_change >= 15.0:
            return "high"
        elif abs_change >= 5.0:
            return "medium"
        else:
            return "low"

    def add_price_point(self, product_id: str, variant_id: int, selling_price: float, 
                       cost_data: CostData, reason: PriceChangeReason = PriceChangeReason.MANUAL_ADJUSTMENT):
        """Add a new price point to history"""
        price_point = PricePoint(
            product_id=product_id,
            variant_id=variant_id,
            selling_price=selling_price,
            cost_data=cost_data,
            profit_margin=0,  # Will be auto-calculated
            profit_amount=0,  # Will be auto-calculated
            reason=reason
        )
        
        history_key = f"{product_id}:{variant_id}"
        if history_key not in self.price_history:
            self.price_history[history_key] = []
        
        self.price_history[history_key].append(price_point)
        
        # Cleanup old history
        self._cleanup_old_history(history_key)
        
        # Check profit margin
        self._check_profit_margin(price_point)
        
        self.save_data()

    def _cleanup_old_history(self, history_key: str):
        """Remove price history older than configured days"""
        cutoff_date = datetime.now() - timedelta(days=self.price_history_days)
        
        if history_key in self.price_history:
            self.price_history[history_key] = [
                point for point in self.price_history[history_key]
                if point.timestamp > cutoff_date
            ]

    def _check_profit_margin(self, price_point: PricePoint):
        """Check if profit margin is below threshold"""
        if price_point.profit_margin < self.margin_threshold:
            alert = PriceAlert(
                product_id=price_point.product_id,
                variant_id=price_point.variant_id,
                alert_type="margin_below_threshold",
                old_value=self.margin_threshold,
                new_value=price_point.profit_margin,
                threshold=self.margin_threshold,
                severity="high" if price_point.profit_margin < 10.0 else "medium",
                message=f"Profit margin ({price_point.profit_margin:.1f}%) below threshold ({self.margin_threshold:.1f}%)"
            )
            
            self.active_alerts.append(alert)
            self.save_alerts()

    def get_current_margins(self) -> Dict[str, Dict[str, float]]:
        """Get current profit margins for all tracked products"""
        margins = {}
        
        for history_key, history in self.price_history.items():
            if history:
                latest_point = history[-1]
                product_id, variant_id = history_key.split(':', 1)
                
                if product_id not in margins:
                    margins[product_id] = {}
                
                margins[product_id][variant_id] = {
                    "profit_margin": latest_point.profit_margin,
                    "profit_amount": latest_point.profit_amount,
                    "selling_price": latest_point.selling_price,
                    "total_cost": latest_point.cost_data.total_cost,
                    "last_updated": latest_point.timestamp.isoformat()
                }
        
        return margins

    def get_price_trends(self, product_id: str, variant_id: int, days: int = 30) -> Dict[str, Any]:
        """Analyze price trends for a specific product variant"""
        history_key = f"{product_id}:{variant_id}"
        
        if history_key not in self.price_history:
            return {"error": "No price history found"}
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_history = [
            point for point in self.price_history[history_key]
            if point.timestamp > cutoff_date
        ]
        
        if len(recent_history) < 2:
            return {"error": "Insufficient data for trend analysis"}
        
        # Calculate trends
        first_point = recent_history[0]
        last_point = recent_history[-1]
        
        price_change = last_point.selling_price - first_point.selling_price
        price_change_percent = (price_change / first_point.selling_price) * 100
        
        cost_change = last_point.cost_data.total_cost - first_point.cost_data.total_cost
        cost_change_percent = (cost_change / first_point.cost_data.total_cost) * 100
        
        margin_change = last_point.profit_margin - first_point.profit_margin
        
        # Determine trend direction
        if abs(price_change_percent) < 2.0:
            trend = PriceDirection.STABLE
        elif price_change_percent > 0:
            trend = PriceDirection.UP
        else:
            trend = PriceDirection.DOWN
        
        return {
            "product_id": product_id,
            "variant_id": variant_id,
            "period_days": days,
            "data_points": len(recent_history),
            "trend_direction": trend.value,
            "price_change": {
                "absolute": price_change,
                "percentage": price_change_percent
            },
            "cost_change": {
                "absolute": cost_change,
                "percentage": cost_change_percent
            },
            "margin_change": margin_change,
            "current_margin": last_point.profit_margin,
            "price_volatility": self._calculate_volatility(recent_history),
            "recommendations": self._generate_trend_recommendations(recent_history, trend)
        }

    def _calculate_volatility(self, history: List[PricePoint]) -> float:
        """Calculate price volatility (standard deviation of price changes)"""
        if len(history) < 3:
            return 0.0
        
        price_changes = []
        for i in range(1, len(history)):
            change = ((history[i].selling_price - history[i-1].selling_price) / history[i-1].selling_price) * 100
            price_changes.append(change)
        
        if not price_changes:
            return 0.0
        
        mean_change = sum(price_changes) / len(price_changes)
        variance = sum((x - mean_change) ** 2 for x in price_changes) / len(price_changes)
        
        return variance ** 0.5

    def _generate_trend_recommendations(self, history: List[PricePoint], trend: PriceDirection) -> List[str]:
        """Generate recommendations based on price trends"""
        recommendations = []
        
        if not history:
            return recommendations
        
        latest_point = history[-1]
        
        # Margin-based recommendations
        if latest_point.profit_margin < 15.0:
            recommendations.append("Consider increasing price - profit margin is below 15%")
        elif latest_point.profit_margin > 60.0:
            recommendations.append("Consider decreasing price - high margin may hurt competitiveness")
        
        # Trend-based recommendations
        if trend == PriceDirection.UP:
            recommendations.append("Monitor customer response to recent price increases")
        elif trend == PriceDirection.DOWN:
            recommendations.append("Consider if price decreases are improving sales volume")
        
        # Cost analysis
        cost_increases = sum(1 for i in range(1, len(history)) 
                           if history[i].cost_data.total_cost > history[i-1].cost_data.total_cost)
        
        if cost_increases > len(history) / 2:
            recommendations.append("Costs are trending upward - consider price adjustment")
        
        return recommendations

    def get_active_alerts(self, severity: Optional[str] = None) -> List[PriceAlert]:
        """Get active price alerts, optionally filtered by severity"""
        if severity:
            return [alert for alert in self.active_alerts 
                   if alert.severity == severity and not alert.acknowledged]
        
        return [alert for alert in self.active_alerts if not alert.acknowledged]

    def acknowledge_alert(self, alert_index: int) -> bool:
        """Acknowledge an alert by index"""
        if 0 <= alert_index < len(self.active_alerts):
            self.active_alerts[alert_index].acknowledged = True
            self.save_alerts()
            return True
        
        return False

    def start_monitoring(self, api_client=None):
        """Start continuous price monitoring"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self.logger.warning("Monitoring already running")
            return
        
        self.monitoring_enabled = True
        self._stop_monitoring.clear()
        
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(api_client,),
            daemon=True
        )
        self._monitor_thread.start()
        
        self.logger.info("Price monitoring started")

    def stop_monitoring(self):
        """Stop continuous price monitoring"""
        self.monitoring_enabled = False
        self._stop_monitoring.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        
        self.logger.info("Price monitoring stopped")

    def _monitoring_loop(self, api_client):
        """Main monitoring loop"""
        while self.monitoring_enabled and not self._stop_monitoring.is_set():
            try:
                if api_client:
                    self._check_cost_updates(api_client)
                
                # Wait for next check
                self._stop_monitoring.wait(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                # Wait before retrying
                self._stop_monitoring.wait(60)

    def _check_cost_updates(self, api_client):
        """Check for cost updates from API"""
        # This would integrate with Printify API to check for cost changes
        # For now, we'll skip the actual API calls
        self.logger.debug("Checking for cost updates...")

    def save_data(self):
        """Save price history to file"""
        try:
            data = {
                "price_history": {},
                "current_costs": {},
                "pricing_rules": self.pricing_rules,
                "last_updated": datetime.now().isoformat()
            }
            
            # Convert price history to serializable format
            for key, history in self.price_history.items():
                data["price_history"][key] = [
                    {
                        **asdict(point),
                        "timestamp": point.timestamp.isoformat(),
                        "cost_data": {
                            **asdict(point.cost_data),
                            "timestamp": point.cost_data.timestamp.isoformat()
                        },
                        "reason": point.reason.value
                    }
                    for point in history
                ]
            
            # Convert current costs to serializable format
            for key, cost_data in self.current_costs.items():
                data["current_costs"][key] = {
                    **asdict(cost_data),
                    "timestamp": cost_data.timestamp.isoformat()
                }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save pricing data: {e}")

    def load_data(self):
        """Load price history from file"""
        try:
            if not self.data_file.exists():
                return
            
            with open(self.data_file, 'r') as f:
                data = json.load(f)
            
            # Load pricing rules
            if "pricing_rules" in data:
                self.pricing_rules.update(data["pricing_rules"])
            
            # Load price history
            for key, history_data in data.get("price_history", {}).items():
                history = []
                for point_data in history_data:
                    cost_data = CostData(
                        variant_id=point_data["cost_data"]["variant_id"],
                        base_cost=point_data["cost_data"]["base_cost"],
                        shipping_cost=point_data["cost_data"]["shipping_cost"],
                        processing_fee=point_data["cost_data"]["processing_fee"],
                        total_cost=point_data["cost_data"]["total_cost"],
                        currency=point_data["cost_data"]["currency"],
                        timestamp=datetime.fromisoformat(point_data["cost_data"]["timestamp"])
                    )
                    
                    price_point = PricePoint(
                        product_id=point_data["product_id"],
                        variant_id=point_data["variant_id"],
                        selling_price=point_data["selling_price"],
                        cost_data=cost_data,
                        profit_margin=point_data["profit_margin"],
                        profit_amount=point_data["profit_amount"],
                        timestamp=datetime.fromisoformat(point_data["timestamp"]),
                        reason=PriceChangeReason(point_data["reason"])
                    )
                    
                    history.append(price_point)
                
                self.price_history[key] = history
            
            # Load current costs
            for key, cost_data in data.get("current_costs", {}).items():
                self.current_costs[key] = CostData(
                    variant_id=cost_data["variant_id"],
                    base_cost=cost_data["base_cost"],
                    shipping_cost=cost_data["shipping_cost"],
                    processing_fee=cost_data["processing_fee"],
                    total_cost=cost_data["total_cost"],
                    currency=cost_data["currency"],
                    timestamp=datetime.fromisoformat(cost_data["timestamp"])
                )
                
        except Exception as e:
            self.logger.error(f"Failed to load pricing data: {e}")

    def save_alerts(self):
        """Save alerts to file"""
        try:
            data = {
                "alerts": [
                    {
                        **asdict(alert),
                        "timestamp": alert.timestamp.isoformat()
                    }
                    for alert in self.active_alerts
                ],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.alert_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save alerts: {e}")

    def load_alerts(self):
        """Load alerts from file"""
        try:
            if not self.alert_file.exists():
                return
            
            with open(self.alert_file, 'r') as f:
                data = json.load(f)
            
            # Load alerts
            for alert_data in data.get("alerts", []):
                alert = PriceAlert(
                    product_id=alert_data["product_id"],
                    variant_id=alert_data["variant_id"],
                    alert_type=alert_data["alert_type"],
                    old_value=alert_data["old_value"],
                    new_value=alert_data["new_value"],
                    threshold=alert_data["threshold"],
                    severity=alert_data["severity"],
                    message=alert_data["message"],
                    timestamp=datetime.fromisoformat(alert_data["timestamp"]),
                    acknowledged=alert_data.get("acknowledged", False)
                )
                
                self.active_alerts.append(alert)
                
        except Exception as e:
            self.logger.error(f"Failed to load alerts: {e}")

    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the pricing monitor"""
        total_products = len(self.price_history)
        total_alerts = len(self.active_alerts)
        unacknowledged_alerts = len(self.get_active_alerts())
        
        # Calculate average margin
        current_margins = self.get_current_margins()
        all_margins = []
        for product_margins in current_margins.values():
            all_margins.extend([data["profit_margin"] for data in product_margins.values()])
        
        avg_margin = sum(all_margins) / len(all_margins) if all_margins else 0
        
        # Alert breakdown by severity
        alert_breakdown = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for alert in self.get_active_alerts():
            alert_breakdown[alert.severity] += 1
        
        return {
            "total_products_tracked": total_products,
            "total_alerts": total_alerts,
            "unacknowledged_alerts": unacknowledged_alerts,
            "average_profit_margin": round(avg_margin, 2),
            "alert_breakdown": alert_breakdown,
            "monitoring_enabled": self.monitoring_enabled,
            "last_check": datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    # Create pricing monitor
    monitor = PricingMonitor()
    
    # Example: Track a cost change
    cost_data = CostData(
        variant_id=12345,
        base_cost=800,  # $8.00
        shipping_cost=200,  # $2.00
        processing_fee=100,  # $1.00
        total_cost=1100  # $11.00
    )
    
    # Add initial price point
    monitor.add_price_point(
        product_id="test_product_1",
        variant_id=12345,
        selling_price=1999,  # $19.99
        cost_data=cost_data,
        reason=PriceChangeReason.MANUAL_ADJUSTMENT
    )
    
    # Simulate cost increase
    new_cost_data = CostData(
        variant_id=12345,
        base_cost=850,  # $8.50 (increase)
        shipping_cost=200,
        processing_fee=100,
        total_cost=1150  # $11.50
    )
    
    alert = monitor.track_cost_change("test_product_1", 12345, new_cost_data)
    if alert:
        print(f"Alert generated: {alert.message}")
    
    # Get price trends
    trends = monitor.get_price_trends("test_product_1", 12345)
    print(f"Price trends: {trends}")
    
    # Get summary stats
    stats = monitor.get_summary_stats()
    print(f"Summary: {stats}")