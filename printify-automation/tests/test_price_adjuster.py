"""
Test cases for PriceAdjuster
"""

import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from price_adjuster import (
    PriceAdjuster, PriceAdjustment, AdjustmentRule, 
    AdjustmentTrigger, AdjustmentStatus
)
from pricing_monitor import PricingMonitor, PriceAlert
from cost_analyzer import CostAnalyzer


class TestPriceAdjuster:
    def setup_method(self):
        """Set up test fixtures"""
        self.pricing_monitor = PricingMonitor()
        self.cost_analyzer = CostAnalyzer()
        self.adjuster = PriceAdjuster(self.pricing_monitor, self.cost_analyzer)
        
        # Set up mock price update callback
        self.executed_updates = []
        
        def mock_price_update(product_id: str, variant_id: int, new_price: float) -> bool:
            self.executed_updates.append({
                'product_id': product_id,
                'variant_id': variant_id,
                'new_price': new_price,
                'timestamp': datetime.now()
            })
            return True
        
        self.adjuster.set_price_update_callback(mock_price_update)

    def test_adjustment_rule_creation(self):
        """Test AdjustmentRule creation"""
        rule = AdjustmentRule(
            name="Test Rule",
            trigger=AdjustmentTrigger.COST_INCREASE,
            conditions={"min_cost_increase_percent": 5.0},
            action={"pass_through_rate": 0.8},
            auto_execute=False,
            max_adjustment_percent=15.0
        )
        
        assert rule.name == "Test Rule"
        assert rule.trigger == AdjustmentTrigger.COST_INCREASE
        assert rule.enabled == True
        assert rule.cooldown_hours == 24

    def test_price_adjustment_creation(self):
        """Test PriceAdjustment creation and auto-calculation"""
        adjustment = PriceAdjustment(
            product_id="test_product",
            variant_id=12345,
            current_price=1999,
            proposed_price=2199,
            adjustment_percent=0,  # Should be auto-calculated
            trigger=AdjustmentTrigger.COST_INCREASE,
            reason="Test adjustment",
            confidence=0.8,
            impact_analysis={}
        )
        
        expected_percent = ((2199 - 1999) / 1999) * 100
        assert abs(adjustment.adjustment_percent - expected_percent) < 0.01
        assert adjustment.status == AdjustmentStatus.PENDING
        assert isinstance(adjustment.created_at, datetime)
        assert isinstance(adjustment.expires_at, datetime)

    def test_default_rules_initialization(self):
        """Test that default rules are properly initialized"""
        rules = self.adjuster.adjustment_rules
        
        assert len(rules) >= 4  # Should have at least 4 default rules
        
        # Check for specific rule types
        rule_triggers = [rule.trigger for rule in rules]
        assert AdjustmentTrigger.COST_INCREASE in rule_triggers
        assert AdjustmentTrigger.COST_DECREASE in rule_triggers
        assert AdjustmentTrigger.MARGIN_BELOW_THRESHOLD in rule_triggers
        assert AdjustmentTrigger.SEASONAL_ADJUSTMENT in rule_triggers

    def test_process_cost_increase_alert(self):
        """Test processing cost increase alert"""
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
        
        adjustment = self.adjuster.process_cost_change_alert(alert)
        
        assert adjustment is not None
        assert adjustment.trigger == AdjustmentTrigger.COST_INCREASE
        assert adjustment.product_id == "test_product"
        assert adjustment.variant_id == 12345
        assert adjustment.proposed_price > adjustment.current_price
        assert adjustment.confidence > 0

    def test_process_cost_decrease_alert(self):
        """Test processing cost decrease alert"""
        alert = PriceAlert(
            product_id="test_product",
            variant_id=12345,
            alert_type="cost_decrease",
            old_value=1210,  # $12.10
            new_value=1089,  # $10.89 (10% decrease)
            threshold=5.0,
            severity="medium",
            message="Cost decreased by 10%"
        )
        
        adjustment = self.adjuster.process_cost_change_alert(alert)
        
        assert adjustment is not None
        assert adjustment.trigger == AdjustmentTrigger.COST_DECREASE
        assert adjustment.proposed_price < adjustment.current_price

    def test_minor_cost_change_ignored(self):
        """Test that minor cost changes don't trigger adjustments"""
        alert = PriceAlert(
            product_id="test_product",
            variant_id=12345,
            alert_type="cost_increase",
            old_value=1100,  # $11.00
            new_value=1122,  # $11.22 (2% increase, below 5% threshold)
            threshold=5.0,
            severity="low",
            message="Cost increased by 2%"
        )
        
        adjustment = self.adjuster.process_cost_change_alert(alert)
        
        assert adjustment is None  # Should not create adjustment for minor changes

    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        # High severity, large change should have high confidence
        high_confidence = self.adjuster._calculate_adjustment_confidence(
            cost_change_percent=25.0,
            severity="critical",
            rule=self.adjuster.adjustment_rules[0]
        )
        
        # Low severity, small change should have lower confidence
        low_confidence = self.adjuster._calculate_adjustment_confidence(
            cost_change_percent=3.0,
            severity="low",
            rule=self.adjuster.adjustment_rules[0]
        )
        
        assert high_confidence > low_confidence
        assert 0.0 <= high_confidence <= 1.0
        assert 0.0 <= low_confidence <= 1.0

    def test_price_rounding(self):
        """Test price rounding functionality"""
        # Test .99 rounding
        rounded_99 = self.adjuster._round_price(2234, 99)
        assert rounded_99 == 2199  # Should round down to $21.99
        
        # Test .95 rounding
        rounded_95 = self.adjuster._round_price(2234, 95)
        assert rounded_95 == 2195  # Should round down to $21.95
        
        # Test regular rounding
        rounded_regular = self.adjuster._round_price(2234.67, 0)
        assert rounded_regular == 2235  # Should round to nearest cent

    def test_impact_analysis(self):
        """Test adjustment impact analysis"""
        impact = self.adjuster._analyze_adjustment_impact(
            current_price=1999,
            proposed_price=2199,
            new_cost=1210,
            product_id="test_product"
        )
        
        assert "price_change" in impact
        assert "price_change_percent" in impact
        assert "new_margin_percent" in impact
        assert "estimated_demand_change_percent" in impact
        assert "risk_level" in impact
        
        assert impact["price_change"] == 200  # 2199 - 1999
        assert impact["price_change_percent"] > 0

    def test_cooldown_enforcement(self):
        """Test cooldown period enforcement"""
        product_key = "test_product:12345"
        rule = self.adjuster.adjustment_rules[0]
        
        # First check should pass (no previous adjustment)
        assert self.adjuster._check_cooldown(product_key, rule) == True
        
        # Simulate recent adjustment
        self.adjuster.last_adjustment_times[product_key] = datetime.now() - timedelta(hours=1)
        
        # Second check should fail (within cooldown period)
        assert self.adjuster._check_cooldown(product_key, rule) == False
        
        # Simulate old adjustment
        self.adjuster.last_adjustment_times[product_key] = datetime.now() - timedelta(hours=25)
        
        # Third check should pass (outside cooldown period)
        assert self.adjuster._check_cooldown(product_key, rule) == True

    def test_margin_below_threshold_processing(self):
        """Test processing low margin situations"""
        adjustment = self.adjuster.process_margin_alert(
            product_id="test_product",
            variant_id=12345,
            current_margin=12.0  # Below 15% threshold
        )
        
        assert adjustment is not None
        assert adjustment.trigger == AdjustmentTrigger.MARGIN_BELOW_THRESHOLD
        assert adjustment.proposed_price > adjustment.current_price
        assert adjustment.confidence >= 0.7  # Should have decent confidence

    def test_adjustment_approval_workflow(self):
        """Test adjustment approval and execution workflow"""
        # Create an adjustment
        alert = PriceAlert(
            product_id="test_product", variant_id=12345, alert_type="cost_increase",
            old_value=1100, new_value=1210, threshold=5.0, severity="medium",
            message="Cost increased"
        )
        
        adjustment = self.adjuster.process_cost_change_alert(alert)
        assert adjustment is not None
        
        # Check that it's pending
        assert adjustment.status == AdjustmentStatus.PENDING
        
        # Approve the adjustment
        success = self.adjuster.approve_adjustment(0)
        assert success == True
        assert adjustment.status == AdjustmentStatus.APPROVED
        
        # Execute approved adjustments
        executed = self.adjuster.execute_approved_adjustments()
        assert len(executed) == 1
        assert executed[0].status == AdjustmentStatus.EXECUTED
        
        # Check that price update was called
        assert len(self.executed_updates) == 1
        assert self.executed_updates[0]['product_id'] == "test_product"

    def test_adjustment_rejection(self):
        """Test adjustment rejection"""
        # Create an adjustment
        alert = PriceAlert(
            product_id="test_product", variant_id=12345, alert_type="cost_increase",
            old_value=1100, new_value=1210, threshold=5.0, severity="medium",
            message="Cost increased"
        )
        
        adjustment = self.adjuster.process_cost_change_alert(alert)
        assert adjustment is not None
        
        # Reject the adjustment
        success = self.adjuster.reject_adjustment(0, "Manual review required")
        assert success == True
        assert adjustment.status == AdjustmentStatus.REJECTED

    def test_auto_execution(self):
        """Test automatic execution of high-confidence adjustments"""
        # Find an auto-execute rule
        auto_rules = [rule for rule in self.adjuster.adjustment_rules if rule.auto_execute]
        assert len(auto_rules) > 0
        
        # Create alert that should trigger auto-execution
        alert = PriceAlert(
            product_id="test_product", variant_id=12345, alert_type="cost_decrease",
            old_value=1210, new_value=1089, threshold=5.0, severity="medium",
            message="Cost decreased by 10%"
        )
        
        initial_updates = len(self.executed_updates)
        adjustment = self.adjuster.process_cost_change_alert(alert)
        
        # Should have auto-executed if confidence is high enough
        if adjustment and adjustment.confidence >= auto_rules[0].min_confidence:
            assert len(self.executed_updates) > initial_updates

    def test_max_adjustment_limit_enforcement(self):
        """Test that maximum adjustment percentage is enforced"""
        # Create alert with very large cost change
        alert = PriceAlert(
            product_id="test_product", variant_id=12345, alert_type="cost_increase",
            old_value=1100, new_value=1980, threshold=5.0, severity="critical",  # 80% increase
            message="Massive cost increase"
        )
        
        adjustment = self.adjuster.process_cost_change_alert(alert)
        
        if adjustment:
            # Should be capped at rule's max_adjustment_percent
            max_allowed = self.adjuster.adjustment_rules[0].max_adjustment_percent
            assert abs(adjustment.adjustment_percent) <= max_allowed

    def test_expired_adjustment_cleanup(self):
        """Test cleanup of expired adjustments"""
        # Create an adjustment and manually set it to expired
        alert = PriceAlert(
            product_id="test_product", variant_id=12345, alert_type="cost_increase",
            old_value=1100, new_value=1210, threshold=5.0, severity="medium",
            message="Cost increased"
        )
        
        adjustment = self.adjuster.process_cost_change_alert(alert)
        assert adjustment is not None
        
        # Manually expire the adjustment
        adjustment.expires_at = datetime.now() - timedelta(hours=1)
        
        initial_pending = len(self.adjuster.pending_adjustments)
        initial_history = len(self.adjuster.adjustment_history)
        
        # Run cleanup
        self.adjuster.cleanup_expired_adjustments()
        
        # Should have moved expired adjustment to history
        assert len(self.adjuster.pending_adjustments) == initial_pending - 1
        assert len(self.adjuster.adjustment_history) == initial_history + 1

    def test_get_pending_adjustments(self):
        """Test getting pending adjustments"""
        # Create multiple adjustments
        for i in range(3):
            alert = PriceAlert(
                product_id=f"product_{i}", variant_id=12345, alert_type="cost_increase",
                old_value=1100, new_value=1210, threshold=5.0, severity="medium",
                message=f"Cost increased for product {i}"
            )
            self.adjuster.process_cost_change_alert(alert)
        
        # Get all pending
        all_pending = self.adjuster.get_pending_adjustments()
        assert len(all_pending) >= 3
        
        # Get pending for specific product
        product_specific = self.adjuster.get_pending_adjustments("product_1")
        assert len(product_specific) == 1
        assert product_specific[0].product_id == "product_1"

    def test_adjustment_summary(self):
        """Test adjustment summary generation"""
        # Create some test adjustments
        alert = PriceAlert(
            product_id="test_product", variant_id=12345, alert_type="cost_increase",
            old_value=1100, new_value=1210, threshold=5.0, severity="medium",
            message="Cost increased"
        )
        
        adjustment = self.adjuster.process_cost_change_alert(alert)
        if adjustment:
            self.adjuster.approve_adjustment(0)
            self.adjuster.execute_approved_adjustments()
        
        summary = self.adjuster.get_adjustment_summary()
        
        assert "pending_adjustments" in summary
        assert "approved_adjustments" in summary
        assert "executed_adjustments_total" in summary
        assert "rules_active" in summary
        assert isinstance(summary["rules_active"], int)

    def test_custom_trigger_registration(self):
        """Test registration of custom triggers"""
        def custom_trigger(data):
            return data.get("custom_condition", False)
        
        self.adjuster.register_custom_trigger("custom_test", custom_trigger)
        
        assert "custom_test" in self.adjuster.custom_triggers
        assert self.adjuster.custom_triggers["custom_test"] == custom_trigger


if __name__ == "__main__":
    # Run tests if script is executed directly
    test_adjuster = TestPriceAdjuster()
    
    print("Running PriceAdjuster tests...")
    
    try:
        test_adjuster.setup_method()
        test_adjuster.test_adjustment_rule_creation()
        print("✅ Adjustment rule creation test passed")
        
        test_adjuster.test_price_adjustment_creation()
        print("✅ Price adjustment creation test passed")
        
        test_adjuster.test_default_rules_initialization()
        print("✅ Default rules initialization test passed")
        
        test_adjuster.test_process_cost_increase_alert()
        print("✅ Cost increase alert processing test passed")
        
        test_adjuster.test_process_cost_decrease_alert()
        print("✅ Cost decrease alert processing test passed")
        
        test_adjuster.test_minor_cost_change_ignored()
        print("✅ Minor cost change ignored test passed")
        
        test_adjuster.test_confidence_calculation()
        print("✅ Confidence calculation test passed")
        
        test_adjuster.test_price_rounding()
        print("✅ Price rounding test passed")
        
        test_adjuster.test_impact_analysis()
        print("✅ Impact analysis test passed")
        
        test_adjuster.test_cooldown_enforcement()
        print("✅ Cooldown enforcement test passed")
        
        test_adjuster.test_margin_below_threshold_processing()
        print("✅ Margin below threshold processing test passed")
        
        test_adjuster.test_adjustment_approval_workflow()
        print("✅ Adjustment approval workflow test passed")
        
        test_adjuster.test_adjustment_rejection()
        print("✅ Adjustment rejection test passed")
        
        test_adjuster.test_max_adjustment_limit_enforcement()
        print("✅ Max adjustment limit enforcement test passed")
        
        test_adjuster.test_expired_adjustment_cleanup()
        print("✅ Expired adjustment cleanup test passed")
        
        test_adjuster.test_get_pending_adjustments()
        print("✅ Get pending adjustments test passed")
        
        test_adjuster.test_adjustment_summary()
        print("✅ Adjustment summary test passed")
        
        test_adjuster.test_custom_trigger_registration()
        print("✅ Custom trigger registration test passed")
        
        print("\n🎉 All PriceAdjuster tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()