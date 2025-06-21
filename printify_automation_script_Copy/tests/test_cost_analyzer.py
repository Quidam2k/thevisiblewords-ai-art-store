"""
Test cases for CostAnalyzer
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from cost_analyzer import (
    CostAnalyzer, CostBreakdown, ProfitAnalysis, 
    PricingStrategy, MarketPosition
)


class TestCostAnalyzer:
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = CostAnalyzer({
            'target_margin': 30.0,
            'min_margin': 15.0,
            'transaction_fee_rate': 0.029,
            'marketing_cost_rate': 0.10,
            'overhead_rate': 0.05
        })

    def test_cost_breakdown_creation(self):
        """Test CostBreakdown creation and auto-calculation"""
        breakdown = CostBreakdown(
            base_cost=800,
            shipping_cost=200,
            processing_fee=100,
            transaction_fee=50,
            packaging_cost=25,
            marketing_cost=150,
            overhead_cost=75,
            total_cost=0  # Should be auto-calculated
        )
        
        expected_total = 800 + 200 + 100 + 50 + 25 + 150 + 75
        assert breakdown.total_cost == expected_total

    def test_analyze_cost_structure(self):
        """Test cost structure analysis"""
        breakdown = self.analyzer.analyze_cost_structure(
            base_cost=800,
            selling_price=1999,
            additional_costs={
                'shipping_cost': 200,
                'processing_fee': 100,
                'packaging_cost': 25
            }
        )
        
        # Check that all costs are calculated
        assert breakdown.base_cost == 800
        assert breakdown.shipping_cost == 200
        assert breakdown.processing_fee == 100
        assert breakdown.packaging_cost == 25
        
        # Check calculated costs
        expected_transaction_fee = 1999 * 0.029
        expected_marketing_cost = 1999 * 0.10
        expected_overhead_cost = 1999 * 0.05
        
        assert abs(breakdown.transaction_fee - expected_transaction_fee) < 0.01
        assert abs(breakdown.marketing_cost - expected_marketing_cost) < 0.01
        assert abs(breakdown.overhead_cost - expected_overhead_cost) < 0.01
        
        assert breakdown.total_cost > 0

    def test_profit_analysis_calculation(self):
        """Test profit analysis calculations"""
        breakdown = CostBreakdown(
            base_cost=800,
            shipping_cost=200,
            processing_fee=100,
            transaction_fee=58,
            packaging_cost=25,
            marketing_cost=200,
            overhead_cost=100,
            total_cost=1483
        )
        
        analysis = self.analyzer.calculate_profit_analysis(1999, breakdown)
        
        assert analysis.selling_price == 1999
        assert analysis.total_cost == 1483
        assert analysis.gross_profit == 516  # 1999 - 1483
        
        expected_margin = (516 / 1999) * 100
        assert abs(analysis.gross_margin_percent - expected_margin) < 0.01
        
        assert analysis.break_even_price > analysis.total_cost
        assert analysis.recommended_price > analysis.break_even_price
        assert analysis.min_viable_price >= analysis.total_cost

    def test_pricing_strategy_recommendations(self):
        """Test pricing strategy recommendations"""
        breakdown = CostBreakdown(
            base_cost=800, shipping_cost=200, processing_fee=100,
            transaction_fee=58, packaging_cost=25, marketing_cost=200,
            overhead_cost=100, total_cost=1483
        )
        
        competitor_prices = [1599, 1799, 2199, 2499]
        
        recommendations = self.analyzer.recommend_pricing_strategy(
            breakdown, MarketPosition.MID_RANGE, competitor_prices
        )
        
        assert "strategies" in recommendations
        assert "recommended" in recommendations
        assert "market_analysis" in recommendations
        
        # Check that different strategies are present
        strategies = recommendations["strategies"]
        assert PricingStrategy.COST_PLUS in strategies
        assert PricingStrategy.COMPETITIVE in strategies
        assert PricingStrategy.VALUE_BASED in strategies
        
        # Check competitive strategy uses competitor data
        competitive = strategies[PricingStrategy.COMPETITIVE]
        assert competitive["price"] == 1999  # Median of [1599, 1799, 2199, 2499]

    def test_market_fit_assessment(self):
        """Test market fit assessment for different positions"""
        # Test budget position
        budget_fit = self.analyzer._assess_market_fit(10, MarketPosition.BUDGET)
        assert budget_fit == "excellent"  # $10 is in budget range
        
        # Test premium position
        premium_fit = self.analyzer._assess_market_fit(50, MarketPosition.PREMIUM)
        assert premium_fit == "excellent"  # $50 is in premium range
        
        # Test overpriced
        overpriced_fit = self.analyzer._assess_market_fit(100, MarketPosition.BUDGET)
        assert overpriced_fit == "too_high"

    def test_price_elasticity_impact(self):
        """Test price elasticity impact calculation"""
        impact = self.analyzer.calculate_price_elasticity_impact(
            base_price=1999,
            price_change_percent=10.0,  # 10% price increase
            estimated_demand_change_percent=-15.0  # 15% demand decrease
        )
        
        assert impact["price_change_percent"] == 10.0
        assert impact["demand_change_percent"] == -15.0
        assert impact["new_price"] == 1999 * 1.1
        assert impact["elasticity"] == -1.5  # -15% / 10%
        assert impact["revenue_change_percent"] < 0  # Should be negative

    def test_volume_pricing_optimization(self):
        """Test volume pricing optimization"""
        breakdown = CostBreakdown(
            base_cost=800, shipping_cost=200, processing_fee=100,
            transaction_fee=58, packaging_cost=25, marketing_cost=200,
            overhead_cost=100, total_cost=1483
        )
        
        volume_tiers = [(1, 1999), (10, 1899), (50, 1799)]
        
        optimization = self.analyzer.optimize_pricing_for_volume(breakdown, volume_tiers)
        
        assert 1 in optimization
        assert 10 in optimization
        assert 50 in optimization
        
        # Check that higher volumes have better margins due to cost savings
        tier_1 = optimization[1]
        tier_50 = optimization[50]
        
        assert tier_50["volume_adjusted_margin"] > tier_1["volume_adjusted_margin"]
        assert tier_50["cost_savings"] > tier_1["cost_savings"]

    def test_pricing_report_generation(self):
        """Test comprehensive pricing report generation"""
        breakdown = CostBreakdown(
            base_cost=800, shipping_cost=200, processing_fee=100,
            transaction_fee=58, packaging_cost=25, marketing_cost=200,
            overhead_cost=100, total_cost=1483
        )
        
        report = self.analyzer.generate_pricing_report(
            product_id="test_product",
            cost_breakdown=breakdown,
            current_price=1999,
            market_position=MarketPosition.MID_RANGE,
            competitor_prices=[1599, 1799, 2199, 2499]
        )
        
        # Check report structure
        assert report["product_id"] == "test_product"
        assert report["current_price"] == 1999
        assert "cost_breakdown" in report
        assert "profit_analysis" in report
        assert "pricing_recommendations" in report
        assert "price_sensitivity_analysis" in report
        assert "volume_pricing_analysis" in report
        assert "summary" in report
        
        # Check summary data
        summary = report["summary"]
        assert "current_margin" in summary
        assert "recommended_price" in summary
        assert "risk_level" in summary
        assert "confidence" in summary

    def test_strategy_selection_logic(self):
        """Test strategy selection logic"""
        breakdown = CostBreakdown(
            base_cost=800, shipping_cost=200, processing_fee=100,
            transaction_fee=58, packaging_cost=25, marketing_cost=200,
            overhead_cost=100, total_cost=1483
        )
        
        # Test with no competitor data (should favor cost-plus)
        recommendations_no_comp = self.analyzer.recommend_pricing_strategy(
            breakdown, MarketPosition.MID_RANGE, []
        )
        
        # Test with competitor data (should consider competitive)
        recommendations_with_comp = self.analyzer.recommend_pricing_strategy(
            breakdown, MarketPosition.MID_RANGE, [1599, 1799, 2199, 2499]
        )
        
        # Both should have valid recommendations
        assert recommendations_no_comp["recommended"]["confidence"] > 0
        assert recommendations_with_comp["recommended"]["confidence"] > 0

    def test_market_analysis(self):
        """Test market condition analysis"""
        competitor_prices = [1500, 1600, 1700, 1800, 2000, 2200, 2500]
        
        analysis = self.analyzer._analyze_market_conditions(competitor_prices)
        
        assert analysis["competitors"] == 7
        assert "price_range" in analysis
        assert analysis["price_range"]["min"] == 1500
        assert analysis["price_range"]["max"] == 2500
        assert analysis["price_range"]["median"] == 1800
        
        # Check price dispersion calculation
        assert "price_dispersion" in analysis
        assert "standard_deviation" in analysis["price_dispersion"]
        assert "market_maturity" in analysis["price_dispersion"]

    def test_price_gap_identification(self):
        """Test identification of pricing gaps"""
        # Create prices with significant gaps
        sorted_prices = [1000, 1100, 1800, 1900, 2500]  # Big gap between 1100-1800 and 1900-2500
        
        gaps = self.analyzer._find_price_gaps(sorted_prices)
        
        assert len(gaps) >= 1  # Should find at least one significant gap
        
        # Check first gap
        first_gap = gaps[0]
        assert "gap_percent" in first_gap
        assert first_gap["gap_percent"] > 25  # Should be significant gap

    def test_risk_factor_identification(self):
        """Test risk factor identification"""
        # Create high-cost-sensitivity breakdown
        high_cost_breakdown = CostBreakdown(
            base_cost=1400,  # 70% of total cost
            shipping_cost=100, processing_fee=50, transaction_fee=58,
            packaging_cost=25, marketing_cost=200, overhead_cost=100,
            total_cost=1933
        )
        
        strategies = {
            PricingStrategy.COST_PLUS: {"price": 2000, "margin": 3.5},  # Low margin
            PricingStrategy.PREMIUM: {"price": 5000, "margin": 60.0}    # High price
        }
        
        risks = self.analyzer._identify_risk_factors(high_cost_breakdown, strategies)
        
        # Should identify cost sensitivity and margin risk
        risk_types = [risk["type"] for risk in risks]
        assert "cost_sensitivity" in risk_types
        assert "margin_risk" in risk_types

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with zero selling price
        breakdown = CostBreakdown(
            base_cost=800, shipping_cost=200, processing_fee=100,
            transaction_fee=0, packaging_cost=25, marketing_cost=0,
            overhead_cost=0, total_cost=1125
        )
        
        analysis = self.analyzer.calculate_profit_analysis(0, breakdown)
        assert analysis.gross_margin_percent == 0
        
        # Test with negative costs (shouldn't happen but should handle gracefully)
        try:
            negative_breakdown = CostBreakdown(
                base_cost=-100, shipping_cost=200, processing_fee=100,
                transaction_fee=58, packaging_cost=25, marketing_cost=200,
                overhead_cost=100, total_cost=583
            )
            analysis = self.analyzer.calculate_profit_analysis(1999, negative_breakdown)
            # Should not crash
            assert isinstance(analysis, ProfitAnalysis)
        except Exception as e:
            # If it does throw an exception, that's also acceptable
            pass


if __name__ == "__main__":
    # Run tests if script is executed directly
    test_analyzer = TestCostAnalyzer()
    
    print("Running CostAnalyzer tests...")
    
    try:
        test_analyzer.setup_method()
        test_analyzer.test_cost_breakdown_creation()
        print("✅ Cost breakdown creation test passed")
        
        test_analyzer.test_analyze_cost_structure()
        print("✅ Cost structure analysis test passed")
        
        test_analyzer.test_profit_analysis_calculation()
        print("✅ Profit analysis calculation test passed")
        
        test_analyzer.test_pricing_strategy_recommendations()
        print("✅ Pricing strategy recommendations test passed")
        
        test_analyzer.test_market_fit_assessment()
        print("✅ Market fit assessment test passed")
        
        test_analyzer.test_price_elasticity_impact()
        print("✅ Price elasticity impact test passed")
        
        test_analyzer.test_volume_pricing_optimization()
        print("✅ Volume pricing optimization test passed")
        
        test_analyzer.test_pricing_report_generation()
        print("✅ Pricing report generation test passed")
        
        test_analyzer.test_strategy_selection_logic()
        print("✅ Strategy selection logic test passed")
        
        test_analyzer.test_market_analysis()
        print("✅ Market analysis test passed")
        
        test_analyzer.test_price_gap_identification()
        print("✅ Price gap identification test passed")
        
        test_analyzer.test_risk_factor_identification()
        print("✅ Risk factor identification test passed")
        
        test_analyzer.test_edge_cases()
        print("✅ Edge cases test passed")
        
        print("\n🎉 All CostAnalyzer tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()