"""
Automatic Price Adjustment System
Handles automated pricing decisions based on cost changes, market conditions, and rules
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time

from pricing_monitor import PricingMonitor, PriceChangeReason, PriceAlert
from cost_analyzer import CostAnalyzer, CostBreakdown, MarketPosition, PricingStrategy

class AdjustmentTrigger(Enum):
    COST_INCREASE = "cost_increase"
    COST_DECREASE = "cost_decrease"
    MARGIN_BELOW_THRESHOLD = "margin_below_threshold"
    COMPETITOR_PRICE_CHANGE = "competitor_price_change"
    DEMAND_CHANGE = "demand_change"
    SEASONAL_ADJUSTMENT = "seasonal_adjustment"
    MANUAL_OVERRIDE = "manual_override"

class AdjustmentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTED = "executed"
    REJECTED = "rejected"
    EXPIRED = "expired"

@dataclass
class PriceAdjustment:
    """Represents a proposed price adjustment"""
    product_id: str
    variant_id: int
    current_price: float
    proposed_price: float
    adjustment_percent: float
    trigger: AdjustmentTrigger
    reason: str
    confidence: float  # 0.0 to 1.0
    impact_analysis: Dict[str, Any]
    created_at: datetime = None
    expires_at: datetime = None
    status: AdjustmentStatus = AdjustmentStatus.PENDING
    executed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(hours=24)  # Expire after 24 hours
        
        if self.adjustment_percent == 0 and self.current_price > 0:
            self.adjustment_percent = ((self.proposed_price - self.current_price) / self.current_price) * 100

@dataclass
class AdjustmentRule:
    """Rule for automatic price adjustments"""
    name: str
    trigger: AdjustmentTrigger
    conditions: Dict[str, Any]
    action: Dict[str, Any]
    enabled: bool = True
    auto_execute: bool = False  # If True, execute without approval
    max_adjustment_percent: float = 15.0
    min_confidence: float = 0.7
    cooldown_hours: int = 24  # Minimum time between adjustments

class PriceAdjuster:
    def __init__(self, pricing_monitor: PricingMonitor = None, cost_analyzer: CostAnalyzer = None):
        self.logger = logging.getLogger(__name__)
        self.pricing_monitor = pricing_monitor or PricingMonitor()
        self.cost_analyzer = cost_analyzer or CostAnalyzer()
        
        # Adjustment queue and history
        self.pending_adjustments: List[PriceAdjustment] = []
        self.adjustment_history: List[PriceAdjustment] = []
        
        # Rules engine
        self.adjustment_rules: List[AdjustmentRule] = []
        self.custom_triggers: Dict[str, Callable] = {}
        
        # Configuration
        self.auto_execute_threshold = 0.8  # Auto-execute adjustments with 80%+ confidence
        self.max_daily_adjustments = 10  # Max adjustments per product per day
        self.adjustment_batch_size = 5  # Process 5 adjustments at a time
        
        # State tracking
        self.last_adjustment_times: Dict[str, datetime] = {}
        self.daily_adjustment_counts: Dict[str, int] = {}
        
        # Initialize default rules
        self._init_default_rules()
        
        # Callback for price updates (to be set by integrating system)
        self.price_update_callback: Optional[Callable] = None

    def _init_default_rules(self):
        """Initialize default adjustment rules"""
        
        # Rule 1: React to significant cost increases
        self.adjustment_rules.append(AdjustmentRule(
            name="Cost Increase Response",
            trigger=AdjustmentTrigger.COST_INCREASE,
            conditions={
                "min_cost_increase_percent": 5.0,
                "max_cost_increase_percent": 50.0
            },
            action={
                "pass_through_rate": 0.8,  # Pass through 80% of cost increase
                "min_adjustment": 1.0,     # Minimum $0.01 adjustment
                "round_to_cents": 99       # Round to .99 pricing
            },
            auto_execute=False,  # Require approval for cost increases
            max_adjustment_percent=25.0
        ))
        
        # Rule 2: React to cost decreases (more conservative)
        self.adjustment_rules.append(AdjustmentRule(
            name="Cost Decrease Response",
            trigger=AdjustmentTrigger.COST_DECREASE,
            conditions={
                "min_cost_decrease_percent": 10.0,
                "maintain_margin_above": 20.0
            },
            action={
                "pass_through_rate": 0.5,  # Pass through 50% of cost decrease
                "delay_hours": 72,         # Wait 72 hours
                "round_to_cents": 99
            },
            auto_execute=True,   # Auto-execute cost decreases
            max_adjustment_percent=15.0,
            cooldown_hours=72
        ))
        
        # Rule 3: Maintain minimum margin
        self.adjustment_rules.append(AdjustmentRule(
            name="Minimum Margin Protection",
            trigger=AdjustmentTrigger.MARGIN_BELOW_THRESHOLD,
            conditions={
                "min_margin_percent": 15.0,
                "target_margin_percent": 25.0
            },
            action={
                "target_margin": 25.0,
                "urgency": "high",
                "round_to_cents": 99
            },
            auto_execute=False,  # Require approval for margin adjustments
            max_adjustment_percent=30.0,
            min_confidence=0.9
        ))
        
        # Rule 4: Seasonal adjustments
        self.adjustment_rules.append(AdjustmentRule(
            name="Seasonal Pricing",
            trigger=AdjustmentTrigger.SEASONAL_ADJUSTMENT,
            conditions={
                "seasons": ["holiday", "back_to_school", "summer"],
                "max_seasonal_markup": 15.0
            },
            action={
                "holiday_markup": 10.0,
                "back_to_school_markup": 15.0,
                "summer_discount": -5.0,
                "duration_days": 30
            },
            auto_execute=True,
            max_adjustment_percent=15.0,
            cooldown_hours=168  # One week
        ))

    def register_custom_trigger(self, name: str, trigger_function: Callable):
        """Register a custom trigger function"""
        self.custom_triggers[name] = trigger_function
        self.logger.info(f"Registered custom trigger: {name}")

    def set_price_update_callback(self, callback: Callable):
        """Set callback function for executing price updates"""
        self.price_update_callback = callback

    def process_cost_change_alert(self, alert: PriceAlert) -> Optional[PriceAdjustment]:
        """Process a cost change alert and create price adjustment if needed"""
        if alert.alert_type not in ["cost_increase", "cost_decrease"]:
            return None
        
        trigger = AdjustmentTrigger.COST_INCREASE if alert.alert_type == "cost_increase" else AdjustmentTrigger.COST_DECREASE
        
        # Find applicable rules
        applicable_rules = [rule for rule in self.adjustment_rules if rule.trigger == trigger and rule.enabled]
        
        if not applicable_rules:
            self.logger.info(f"No applicable rules for {alert.alert_type}")
            return None
        
        # Use the first applicable rule (could be enhanced to select best rule)
        rule = applicable_rules[0]
        
        # Check cooldown
        product_key = f"{alert.product_id}:{alert.variant_id}"
        if not self._check_cooldown(product_key, rule):
            self.logger.info(f"Cooldown period active for {product_key}")
            return None
        
        # Calculate adjustment
        adjustment = self._calculate_cost_change_adjustment(alert, rule)
        
        if adjustment:
            self.pending_adjustments.append(adjustment)
            self.logger.info(f"Created price adjustment: {adjustment.reason}")
            
            # Auto-execute if conditions are met
            if rule.auto_execute and adjustment.confidence >= rule.min_confidence:
                self._execute_adjustment(adjustment)
        
        return adjustment

    def _calculate_cost_change_adjustment(self, alert: PriceAlert, rule: AdjustmentRule) -> Optional[PriceAdjustment]:
        """Calculate price adjustment based on cost change"""
        cost_change_percent = ((alert.new_value - alert.old_value) / alert.old_value) * 100
        
        # Check if change meets rule conditions
        if alert.alert_type == "cost_increase":
            min_threshold = rule.conditions.get("min_cost_increase_percent", 0)
            max_threshold = rule.conditions.get("max_cost_increase_percent", 100)
        else:
            min_threshold = rule.conditions.get("min_cost_decrease_percent", 0)
            max_threshold = rule.conditions.get("max_cost_decrease_percent", 100)
        
        if abs(cost_change_percent) < min_threshold or abs(cost_change_percent) > max_threshold:
            return None
        
        # Get current price (this would come from the pricing monitor)
        current_price = self._get_current_price(alert.product_id, alert.variant_id)
        if not current_price:
            return None
        
        # Calculate proposed adjustment
        cost_change_amount = alert.new_value - alert.old_value
        pass_through_rate = rule.action.get("pass_through_rate", 0.8)
        price_adjustment = cost_change_amount * pass_through_rate
        
        proposed_price = current_price + price_adjustment
        
        # Apply rounding
        round_to_cents = rule.action.get("round_to_cents", 99)
        if round_to_cents:
            proposed_price = self._round_price(proposed_price, round_to_cents)
        
        # Calculate confidence
        confidence = self._calculate_adjustment_confidence(
            cost_change_percent, alert.severity, rule
        )
        
        # Impact analysis
        impact_analysis = self._analyze_adjustment_impact(
            current_price, proposed_price, alert.new_value, alert.product_id
        )
        
        adjustment_percent = ((proposed_price - current_price) / current_price) * 100
        
        # Check max adjustment limit
        if abs(adjustment_percent) > rule.max_adjustment_percent:
            # Scale down to max allowed
            max_change = current_price * (rule.max_adjustment_percent / 100)
            if adjustment_percent > 0:
                proposed_price = current_price + max_change
            else:
                proposed_price = current_price - max_change
            adjustment_percent = rule.max_adjustment_percent if adjustment_percent > 0 else -rule.max_adjustment_percent
        
        return PriceAdjustment(
            product_id=alert.product_id,
            variant_id=alert.variant_id,
            current_price=current_price,
            proposed_price=proposed_price,
            adjustment_percent=adjustment_percent,
            trigger=AdjustmentTrigger.COST_INCREASE if alert.alert_type == "cost_increase" else AdjustmentTrigger.COST_DECREASE,
            reason=f"{rule.name}: {abs(cost_change_percent):.1f}% cost change",
            confidence=confidence,
            impact_analysis=impact_analysis
        )

    def _get_current_price(self, product_id: str, variant_id: int) -> Optional[float]:
        """Get current selling price for a product variant"""
        # This would integrate with your product database/API
        # For now, return a placeholder
        return 1999.0  # $19.99

    def _round_price(self, price: float, round_to_cents: int) -> float:
        """Round price to psychological pricing points"""
        if round_to_cents == 99:
            # Round to .99 pricing
            dollars = int(price // 100)
            return (dollars * 100) + 99
        elif round_to_cents == 95:
            # Round to .95 pricing
            dollars = int(price // 100)
            return (dollars * 100) + 95
        else:
            # Round to nearest cent
            return round(price)

    def _calculate_adjustment_confidence(self, cost_change_percent: float, 
                                       severity: str, rule: AdjustmentRule) -> float:
        """Calculate confidence score for an adjustment"""
        base_confidence = 0.5
        
        # Severity factor
        severity_factors = {"low": 0.1, "medium": 0.2, "high": 0.3, "critical": 0.4}
        base_confidence += severity_factors.get(severity, 0.2)
        
        # Cost change magnitude factor
        if abs(cost_change_percent) > 20:
            base_confidence += 0.3
        elif abs(cost_change_percent) > 10:
            base_confidence += 0.2
        elif abs(cost_change_percent) > 5:
            base_confidence += 0.1
        
        # Rule-specific factors
        if rule.trigger == AdjustmentTrigger.COST_INCREASE:
            base_confidence += 0.1  # More confident about cost increase responses
        
        return min(1.0, base_confidence)

    def _analyze_adjustment_impact(self, current_price: float, proposed_price: float, 
                                 new_cost: float, product_id: str) -> Dict[str, Any]:
        """Analyze the impact of a price adjustment"""
        price_change = proposed_price - current_price
        price_change_percent = (price_change / current_price) * 100
        
        # Calculate new margin
        new_margin = ((proposed_price - new_cost) / proposed_price) * 100 if proposed_price > 0 else 0
        
        # Estimate demand impact (simplified)
        estimated_demand_change = price_change_percent * -1.5  # Assume price elasticity of -1.5
        
        # Revenue impact estimation
        revenue_change = price_change_percent + estimated_demand_change
        
        return {
            "price_change": price_change,
            "price_change_percent": price_change_percent,
            "new_margin_percent": new_margin,
            "estimated_demand_change_percent": estimated_demand_change,
            "estimated_revenue_change_percent": revenue_change,
            "competitiveness_impact": "unknown",  # Would need market data
            "risk_level": "low" if abs(price_change_percent) < 5 else "medium" if abs(price_change_percent) < 15 else "high"
        }

    def _check_cooldown(self, product_key: str, rule: AdjustmentRule) -> bool:
        """Check if enough time has passed since last adjustment"""
        if product_key not in self.last_adjustment_times:
            return True
        
        last_adjustment = self.last_adjustment_times[product_key]
        cooldown_period = timedelta(hours=rule.cooldown_hours)
        
        return datetime.now() - last_adjustment > cooldown_period

    def process_margin_alert(self, product_id: str, variant_id: int, current_margin: float) -> Optional[PriceAdjustment]:
        """Process a low margin alert and create adjustment if needed"""
        applicable_rules = [
            rule for rule in self.adjustment_rules 
            if rule.trigger == AdjustmentTrigger.MARGIN_BELOW_THRESHOLD and rule.enabled
        ]
        
        if not applicable_rules:
            return None
        
        rule = applicable_rules[0]
        min_margin = rule.conditions.get("min_margin_percent", 15.0)
        
        if current_margin >= min_margin:
            return None  # Margin is acceptable
        
        # Calculate required price increase
        current_price = self._get_current_price(product_id, variant_id)
        current_cost = self._get_current_cost(product_id, variant_id)
        
        if not current_price or not current_cost:
            return None
        
        target_margin = rule.action.get("target_margin", 25.0)
        required_price = current_cost / (1 - (target_margin / 100))
        
        # Apply rounding
        round_to_cents = rule.action.get("round_to_cents", 99)
        if round_to_cents:
            required_price = self._round_price(required_price, round_to_cents)
        
        adjustment_percent = ((required_price - current_price) / current_price) * 100
        
        # Check max adjustment limit
        if adjustment_percent > rule.max_adjustment_percent:
            required_price = current_price * (1 + rule.max_adjustment_percent / 100)
            adjustment_percent = rule.max_adjustment_percent
        
        confidence = 0.9 if current_margin < 10 else 0.7  # High confidence for very low margins
        
        impact_analysis = self._analyze_adjustment_impact(
            current_price, required_price, current_cost, product_id
        )
        
        adjustment = PriceAdjustment(
            product_id=product_id,
            variant_id=variant_id,
            current_price=current_price,
            proposed_price=required_price,
            adjustment_percent=adjustment_percent,
            trigger=AdjustmentTrigger.MARGIN_BELOW_THRESHOLD,
            reason=f"Margin protection: {current_margin:.1f}% below {min_margin:.1f}% threshold",
            confidence=confidence,
            impact_analysis=impact_analysis
        )
        
        self.pending_adjustments.append(adjustment)
        return adjustment

    def _get_current_cost(self, product_id: str, variant_id: int) -> Optional[float]:
        """Get current total cost for a product variant"""
        # This would integrate with your cost tracking system
        return 1100.0  # $11.00 placeholder

    def approve_adjustment(self, adjustment_index: int) -> bool:
        """Approve a pending adjustment"""
        if 0 <= adjustment_index < len(self.pending_adjustments):
            adjustment = self.pending_adjustments[adjustment_index]
            if adjustment.status == AdjustmentStatus.PENDING:
                adjustment.status = AdjustmentStatus.APPROVED
                return True
        
        return False

    def reject_adjustment(self, adjustment_index: int, reason: str = "") -> bool:
        """Reject a pending adjustment"""
        if 0 <= adjustment_index < len(self.pending_adjustments):
            adjustment = self.pending_adjustments[adjustment_index]
            if adjustment.status == AdjustmentStatus.PENDING:
                adjustment.status = AdjustmentStatus.REJECTED
                self.logger.info(f"Adjustment rejected: {reason}")
                return True
        
        return False

    def execute_approved_adjustments(self) -> List[PriceAdjustment]:
        """Execute all approved adjustments"""
        executed = []
        
        for adjustment in self.pending_adjustments:
            if adjustment.status == AdjustmentStatus.APPROVED:
                if self._execute_adjustment(adjustment):
                    executed.append(adjustment)
        
        return executed

    def _execute_adjustment(self, adjustment: PriceAdjustment) -> bool:
        """Execute a single price adjustment"""
        try:
            if self.price_update_callback:
                success = self.price_update_callback(
                    adjustment.product_id,
                    adjustment.variant_id,
                    adjustment.proposed_price
                )
                
                if success:
                    adjustment.status = AdjustmentStatus.EXECUTED
                    adjustment.executed_at = datetime.now()
                    
                    # Update tracking
                    product_key = f"{adjustment.product_id}:{adjustment.variant_id}"
                    self.last_adjustment_times[product_key] = datetime.now()
                    
                    # Move to history
                    self.adjustment_history.append(adjustment)
                    if adjustment in self.pending_adjustments:
                        self.pending_adjustments.remove(adjustment)
                    
                    self.logger.info(f"Executed price adjustment: {adjustment.reason}")
                    return True
            else:
                self.logger.warning("No price update callback configured")
        
        except Exception as e:
            self.logger.error(f"Failed to execute adjustment: {e}")
        
        return False

    def cleanup_expired_adjustments(self):
        """Remove expired pending adjustments"""
        now = datetime.now()
        expired = []
        
        for adjustment in self.pending_adjustments:
            if now > adjustment.expires_at and adjustment.status == AdjustmentStatus.PENDING:
                adjustment.status = AdjustmentStatus.EXPIRED
                expired.append(adjustment)
        
        for adj in expired:
            self.pending_adjustments.remove(adj)
            self.adjustment_history.append(adj)
        
        if expired:
            self.logger.info(f"Cleaned up {len(expired)} expired adjustments")

    def get_pending_adjustments(self, product_id: str = None) -> List[PriceAdjustment]:
        """Get pending adjustments, optionally filtered by product"""
        adjustments = [adj for adj in self.pending_adjustments if adj.status == AdjustmentStatus.PENDING]
        
        if product_id:
            adjustments = [adj for adj in adjustments if adj.product_id == product_id]
        
        return adjustments

    def get_adjustment_summary(self) -> Dict[str, Any]:
        """Get summary of adjustment activity"""
        total_pending = len([adj for adj in self.pending_adjustments if adj.status == AdjustmentStatus.PENDING])
        total_approved = len([adj for adj in self.pending_adjustments if adj.status == AdjustmentStatus.APPROVED])
        total_executed = len([adj for adj in self.adjustment_history if adj.status == AdjustmentStatus.EXECUTED])
        
        # Recent activity (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_adjustments = [
            adj for adj in self.adjustment_history 
            if adj.executed_at and adj.executed_at > week_ago
        ]
        
        # Trigger breakdown
        trigger_counts = {}
        for adj in recent_adjustments:
            trigger = adj.trigger.value
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
        
        return {
            "pending_adjustments": total_pending,
            "approved_adjustments": total_approved,
            "executed_adjustments_total": total_executed,
            "executed_last_7_days": len(recent_adjustments),
            "trigger_breakdown": trigger_counts,
            "average_confidence": sum(adj.confidence for adj in recent_adjustments) / len(recent_adjustments) if recent_adjustments else 0,
            "rules_active": len([rule for rule in self.adjustment_rules if rule.enabled])
        }


# Example usage
if __name__ == "__main__":
    # Initialize components
    pricing_monitor = PricingMonitor()
    cost_analyzer = CostAnalyzer()
    price_adjuster = PriceAdjuster(pricing_monitor, cost_analyzer)
    
    # Example: Define a price update callback
    def mock_price_update(product_id: str, variant_id: int, new_price: float) -> bool:
        print(f"Updating price for {product_id}:{variant_id} to ${new_price/100:.2f}")
        return True  # Simulate successful update
    
    price_adjuster.set_price_update_callback(mock_price_update)
    
    # Example: Process a cost increase alert
    from pricing_monitor import PriceAlert
    
    alert = PriceAlert(
        product_id="test_product",
        variant_id=12345,
        alert_type="cost_increase",
        old_value=1100,  # $11.00
        new_value=1210,  # $12.10 (10% increase)
        threshold=5.0,
        severity="medium",
        message="Cost increased by 10%"
    )
    
    adjustment = price_adjuster.process_cost_change_alert(alert)
    if adjustment:
        print(f"Created adjustment: {adjustment.reason}")
        print(f"Proposed price change: ${adjustment.current_price/100:.2f} → ${adjustment.proposed_price/100:.2f}")
        print(f"Confidence: {adjustment.confidence:.2f}")
    
    # Get summary
    summary = price_adjuster.get_adjustment_summary()
    print(f"Summary: {summary}")