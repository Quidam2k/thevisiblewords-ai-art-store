"""
Advanced Cost Analyzer
Analyzes costs, calculates profit margins, and provides pricing recommendations
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, NamedTuple
from dataclasses import dataclass
from enum import Enum
import statistics
import math

class PricingStrategy(Enum):
    COST_PLUS = "cost_plus"  # Cost + fixed margin
    COMPETITIVE = "competitive"  # Match market prices
    VALUE_BASED = "value_based"  # Price based on perceived value
    PENETRATION = "penetration"  # Low price to gain market share
    PREMIUM = "premium"  # High price for premium positioning
    DYNAMIC = "dynamic"  # Adjust based on demand/supply

class MarketPosition(Enum):
    BUDGET = "budget"
    MID_RANGE = "mid_range"
    PREMIUM = "premium"
    LUXURY = "luxury"

@dataclass
class CostBreakdown:
    """Detailed cost breakdown for a product"""
    base_cost: float  # Provider's base cost
    shipping_cost: float  # Shipping cost
    processing_fee: float  # Platform processing fee
    transaction_fee: float  # Payment processing fee
    packaging_cost: float  # Additional packaging costs
    marketing_cost: float  # Marketing/advertising allocation
    overhead_cost: float  # General business overhead
    total_cost: float = 0  # Total cost (auto-calculated)
    
    def __post_init__(self):
        if self.total_cost == 0:
            self.total_cost = (
                self.base_cost + self.shipping_cost + self.processing_fee +
                self.transaction_fee + self.packaging_cost + 
                self.marketing_cost + self.overhead_cost
            )

@dataclass
class ProfitAnalysis:
    """Profit analysis results"""
    selling_price: float
    total_cost: float
    gross_profit: float
    gross_margin_percent: float
    break_even_price: float
    recommended_price: float
    min_viable_price: float
    max_competitive_price: float
    roi_percent: float
    
class CostAnalyzer:
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Default analysis parameters
        self.default_target_margin = self.config.get('target_margin', 30.0)  # 30%
        self.min_margin_threshold = self.config.get('min_margin', 15.0)  # 15%
        self.max_margin_threshold = self.config.get('max_margin', 80.0)  # 80%
        
        # Cost calculation factors
        self.transaction_fee_rate = self.config.get('transaction_fee_rate', 0.029)  # 2.9%
        self.marketing_cost_rate = self.config.get('marketing_cost_rate', 0.10)  # 10% of selling price
        self.overhead_rate = self.config.get('overhead_rate', 0.05)  # 5% of selling price
        
        # Market analysis data
        self.market_data = {}
        self.competitor_prices = {}
        
    def analyze_cost_structure(self, base_cost: float, selling_price: float, 
                             additional_costs: Dict[str, float] = None) -> CostBreakdown:
        """Analyze the cost structure of a product"""
        additional_costs = additional_costs or {}
        
        # Calculate transaction fee (percentage of selling price)
        transaction_fee = selling_price * self.transaction_fee_rate
        
        # Calculate marketing cost allocation
        marketing_cost = selling_price * self.marketing_cost_rate
        
        # Calculate overhead allocation
        overhead_cost = selling_price * self.overhead_rate
        
        breakdown = CostBreakdown(
            base_cost=base_cost,
            shipping_cost=additional_costs.get('shipping_cost', 0),
            processing_fee=additional_costs.get('processing_fee', 0),
            transaction_fee=transaction_fee,
            packaging_cost=additional_costs.get('packaging_cost', 0),
            marketing_cost=marketing_cost,
            overhead_cost=overhead_cost
        )
        
        return breakdown

    def calculate_profit_analysis(self, selling_price: float, cost_breakdown: CostBreakdown) -> ProfitAnalysis:
        """Calculate comprehensive profit analysis"""
        gross_profit = selling_price - cost_breakdown.total_cost
        gross_margin_percent = (gross_profit / selling_price) * 100 if selling_price > 0 else 0
        
        # Calculate break-even price (cost + minimum margin)
        break_even_price = cost_breakdown.total_cost / (1 - (self.min_margin_threshold / 100))
        
        # Calculate recommended price based on target margin
        recommended_price = cost_breakdown.total_cost / (1 - (self.default_target_margin / 100))
        
        # Calculate minimum viable price (covers all costs)
        min_viable_price = cost_breakdown.total_cost * 1.01  # 1% minimum profit
        
        # Estimate max competitive price (this would normally come from market data)
        max_competitive_price = recommended_price * 1.5  # Placeholder: 50% above recommended
        
        # Calculate ROI
        roi_percent = (gross_profit / cost_breakdown.total_cost) * 100 if cost_breakdown.total_cost > 0 else 0
        
        return ProfitAnalysis(
            selling_price=selling_price,
            total_cost=cost_breakdown.total_cost,
            gross_profit=gross_profit,
            gross_margin_percent=gross_margin_percent,
            break_even_price=break_even_price,
            recommended_price=recommended_price,
            min_viable_price=min_viable_price,
            max_competitive_price=max_competitive_price,
            roi_percent=roi_percent
        )

    def recommend_pricing_strategy(self, cost_breakdown: CostBreakdown, 
                                 market_position: MarketPosition = MarketPosition.MID_RANGE,
                                 competitor_prices: List[float] = None) -> Dict[str, Any]:
        """Recommend pricing strategy based on costs and market position"""
        competitor_prices = competitor_prices or []
        
        strategies = {}
        
        # Cost-plus strategy
        cost_plus_price = cost_breakdown.total_cost / (1 - (self.default_target_margin / 100))
        strategies[PricingStrategy.COST_PLUS] = {
            "price": cost_plus_price,
            "margin": self.default_target_margin,
            "rationale": f"Cost + {self.default_target_margin}% margin",
            "risk": "low",
            "market_fit": self._assess_market_fit(cost_plus_price, market_position)
        }
        
        # Competitive strategy
        if competitor_prices:
            competitive_price = statistics.median(competitor_prices)
            competitive_margin = ((competitive_price - cost_breakdown.total_cost) / competitive_price) * 100
            
            strategies[PricingStrategy.COMPETITIVE] = {
                "price": competitive_price,
                "margin": competitive_margin,
                "rationale": f"Median competitor price ({len(competitor_prices)} competitors)",
                "risk": "medium",
                "market_fit": "good" if competitive_margin > self.min_margin_threshold else "poor"
            }
        
        # Value-based strategy (based on market position)
        value_multipliers = {
            MarketPosition.BUDGET: 1.2,
            MarketPosition.MID_RANGE: 1.5,
            MarketPosition.PREMIUM: 2.0,
            MarketPosition.LUXURY: 3.0
        }
        
        value_price = cost_breakdown.total_cost * value_multipliers[market_position]
        value_margin = ((value_price - cost_breakdown.total_cost) / value_price) * 100
        
        strategies[PricingStrategy.VALUE_BASED] = {
            "price": value_price,
            "margin": value_margin,
            "rationale": f"Value-based pricing for {market_position.value} position",
            "risk": "medium" if market_position in [MarketPosition.BUDGET, MarketPosition.MID_RANGE] else "high",
            "market_fit": self._assess_market_fit(value_price, market_position)
        }
        
        # Penetration strategy (lower price for market entry)
        penetration_price = cost_breakdown.total_cost * 1.1  # 10% margin
        strategies[PricingStrategy.PENETRATION] = {
            "price": penetration_price,
            "margin": 10.0,
            "rationale": "Low margin for market penetration",
            "risk": "high",
            "market_fit": "excellent",
            "duration": "short-term only"
        }
        
        # Premium strategy
        premium_price = cost_breakdown.total_cost / (1 - 0.6)  # 60% margin
        strategies[PricingStrategy.PREMIUM] = {
            "price": premium_price,
            "margin": 60.0,
            "rationale": "Premium positioning with high margin",
            "risk": "high",
            "market_fit": self._assess_market_fit(premium_price, MarketPosition.PREMIUM)
        }
        
        # Recommend best strategy
        best_strategy = self._select_best_strategy(strategies, market_position, competitor_prices)
        
        return {
            "strategies": strategies,
            "recommended": best_strategy,
            "market_analysis": self._analyze_market_conditions(competitor_prices),
            "risk_factors": self._identify_risk_factors(cost_breakdown, strategies)
        }

    def _assess_market_fit(self, price: float, market_position: MarketPosition) -> str:
        """Assess how well a price fits the market position"""
        # This is a simplified assessment - in reality, you'd have market data
        position_ranges = {
            MarketPosition.BUDGET: (5, 15),
            MarketPosition.MID_RANGE: (15, 35),
            MarketPosition.PREMIUM: (35, 70),
            MarketPosition.LUXURY: (70, 200)
        }
        
        min_price, max_price = position_ranges[market_position]
        
        if min_price <= price <= max_price:
            return "excellent"
        elif price < min_price:
            return "too_low"
        elif price <= max_price * 1.2:
            return "acceptable"
        else:
            return "too_high"

    def _select_best_strategy(self, strategies: Dict[PricingStrategy, Dict], 
                            market_position: MarketPosition, 
                            competitor_prices: List[float]) -> Dict[str, Any]:
        """Select the best pricing strategy based on analysis"""
        scores = {}
        
        for strategy, data in strategies.items():
            score = 0
            
            # Margin score (higher is better, but not too high)
            margin = data["margin"]
            if self.min_margin_threshold <= margin <= self.max_margin_threshold:
                score += 30
            elif margin > self.max_margin_threshold:
                score += 10  # Too high margin
            else:
                score += 0   # Too low margin
            
            # Market fit score
            fit = data.get("market_fit", "poor")
            fit_scores = {"excellent": 25, "good": 20, "acceptable": 15, "poor": 5, "too_low": 8, "too_high": 3}
            score += fit_scores.get(fit, 0)
            
            # Risk score (lower risk is better)
            risk = data.get("risk", "medium")
            risk_scores = {"low": 20, "medium": 15, "high": 5}
            score += risk_scores.get(risk, 10)
            
            # Strategy-specific bonuses
            if strategy == PricingStrategy.COST_PLUS and not competitor_prices:
                score += 15  # Good default when no market data
            elif strategy == PricingStrategy.COMPETITIVE and competitor_prices:
                score += 15  # Good when we have competitive data
            elif strategy == PricingStrategy.VALUE_BASED:
                score += 10  # Generally solid approach
            
            scores[strategy] = score
        
        best_strategy = max(scores, key=scores.get)
        
        return {
            "strategy": best_strategy,
            "data": strategies[best_strategy],
            "confidence": scores[best_strategy] / 100,  # Normalize to 0-1
            "alternatives": sorted(scores.items(), key=lambda x: x[1], reverse=True)[1:3]
        }

    def _analyze_market_conditions(self, competitor_prices: List[float]) -> Dict[str, Any]:
        """Analyze market conditions based on competitor pricing"""
        if not competitor_prices:
            return {"status": "insufficient_data", "competitors": 0}
        
        analysis = {
            "competitors": len(competitor_prices),
            "price_range": {
                "min": min(competitor_prices),
                "max": max(competitor_prices),
                "median": statistics.median(competitor_prices),
                "mean": statistics.mean(competitor_prices)
            }
        }
        
        # Calculate price dispersion
        if len(competitor_prices) > 1:
            std_dev = statistics.stdev(competitor_prices)
            mean_price = statistics.mean(competitor_prices)
            coefficient_variation = (std_dev / mean_price) * 100
            
            analysis["price_dispersion"] = {
                "standard_deviation": std_dev,
                "coefficient_of_variation": coefficient_variation,
                "market_maturity": "mature" if coefficient_variation < 20 else "developing"
            }
        
        # Market positioning opportunities
        sorted_prices = sorted(competitor_prices)
        analysis["gaps"] = self._find_price_gaps(sorted_prices)
        
        return analysis

    def _find_price_gaps(self, sorted_prices: List[float]) -> List[Dict[str, float]]:
        """Find significant gaps in competitor pricing"""
        gaps = []
        
        for i in range(1, len(sorted_prices)):
            gap_size = sorted_prices[i] - sorted_prices[i-1]
            gap_percent = (gap_size / sorted_prices[i-1]) * 100
            
            # Consider gaps >25% significant
            if gap_percent > 25:
                gaps.append({
                    "lower_price": sorted_prices[i-1],
                    "upper_price": sorted_prices[i],
                    "gap_size": gap_size,
                    "gap_percent": gap_percent,
                    "opportunity": "pricing_gap"
                })
        
        return gaps

    def _identify_risk_factors(self, cost_breakdown: CostBreakdown, 
                             strategies: Dict[PricingStrategy, Dict]) -> List[Dict[str, str]]:
        """Identify potential risk factors in pricing"""
        risks = []
        
        # High cost sensitivity
        if cost_breakdown.base_cost / cost_breakdown.total_cost > 0.7:
            risks.append({
                "type": "cost_sensitivity",
                "severity": "medium",
                "description": "Product cost heavily dependent on base cost - vulnerable to supplier price changes"
            })
        
        # Low margin strategies
        low_margin_strategies = [s for s, data in strategies.items() if data["margin"] < self.min_margin_threshold]
        if low_margin_strategies:
            risks.append({
                "type": "margin_risk",
                "severity": "high",
                "description": f"Strategies {[s.value for s in low_margin_strategies]} have margins below {self.min_margin_threshold}%"
            })
        
        # High price point
        max_price = max(data["price"] for data in strategies.values())
        if max_price > cost_breakdown.total_cost * 3:
            risks.append({
                "type": "price_point_risk",
                "severity": "medium",
                "description": "Some strategies result in very high price points - may limit market size"
            })
        
        return risks

    def calculate_price_elasticity_impact(self, base_price: float, price_change_percent: float,
                                        estimated_demand_change_percent: float) -> Dict[str, float]:
        """Calculate the impact of price changes on revenue and profit"""
        new_price = base_price * (1 + price_change_percent / 100)
        new_demand_multiplier = 1 + (estimated_demand_change_percent / 100)
        
        # Assume baseline values
        baseline_revenue = base_price * 100  # 100 units
        new_revenue = new_price * 100 * new_demand_multiplier
        
        return {
            "price_change_percent": price_change_percent,
            "demand_change_percent": estimated_demand_change_percent,
            "new_price": new_price,
            "revenue_change_percent": ((new_revenue - baseline_revenue) / baseline_revenue) * 100,
            "elasticity": estimated_demand_change_percent / price_change_percent if price_change_percent != 0 else 0
        }

    def optimize_pricing_for_volume(self, cost_breakdown: CostBreakdown, 
                                  volume_tiers: List[Tuple[int, float]]) -> Dict[str, Any]:
        """Optimize pricing for different volume levels"""
        # volume_tiers: [(min_quantity, price), ...]
        optimized_pricing = {}
        
        for min_qty, price in volume_tiers:
            # Calculate economics at this volume level
            total_revenue = price * min_qty
            total_cost = cost_breakdown.total_cost * min_qty
            total_profit = total_revenue - total_cost
            margin_percent = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
            
            # Calculate cost efficiencies at higher volumes
            volume_discount = 0
            if min_qty >= 1000:
                volume_discount = 0.05  # 5% cost reduction for 1000+
            elif min_qty >= 100:
                volume_discount = 0.02  # 2% cost reduction for 100+
            
            adjusted_cost = cost_breakdown.total_cost * (1 - volume_discount)
            adjusted_profit = total_revenue - (adjusted_cost * min_qty)
            adjusted_margin = (adjusted_profit / total_revenue) * 100 if total_revenue > 0 else 0
            
            optimized_pricing[min_qty] = {
                "price": price,
                "standard_margin": margin_percent,
                "volume_adjusted_margin": adjusted_margin,
                "cost_savings": volume_discount * 100,
                "breakeven_quantity": math.ceil(cost_breakdown.total_cost / (price - adjusted_cost)) if price > adjusted_cost else float('inf')
            }
        
        return optimized_pricing

    def generate_pricing_report(self, product_id: str, cost_breakdown: CostBreakdown,
                              current_price: float, market_position: MarketPosition,
                              competitor_prices: List[float] = None) -> Dict[str, Any]:
        """Generate comprehensive pricing analysis report"""
        competitor_prices = competitor_prices or []
        
        # Core analysis
        profit_analysis = self.calculate_profit_analysis(current_price, cost_breakdown)
        pricing_recommendations = self.recommend_pricing_strategy(
            cost_breakdown, market_position, competitor_prices
        )
        
        # Additional analyses
        price_sensitivity = []
        for change in [-20, -10, -5, 5, 10, 20]:
            elasticity = self.calculate_price_elasticity_impact(
                current_price, change, change * -1.5  # Assume 1.5x demand elasticity
            )
            price_sensitivity.append(elasticity)
        
        # Volume pricing
        volume_tiers = [(1, current_price), (10, current_price * 0.95), (50, current_price * 0.9)]
        volume_analysis = self.optimize_pricing_for_volume(cost_breakdown, volume_tiers)
        
        return {
            "product_id": product_id,
            "analysis_date": datetime.now().isoformat(),
            "current_price": current_price,
            "cost_breakdown": cost_breakdown.__dict__,
            "profit_analysis": profit_analysis.__dict__,
            "pricing_recommendations": pricing_recommendations,
            "price_sensitivity_analysis": price_sensitivity,
            "volume_pricing_analysis": volume_analysis,
            "market_position": market_position.value,
            "summary": {
                "current_margin": profit_analysis.gross_margin_percent,
                "recommended_price": pricing_recommendations["recommended"]["data"]["price"],
                "margin_improvement": pricing_recommendations["recommended"]["data"]["margin"] - profit_analysis.gross_margin_percent,
                "risk_level": pricing_recommendations["recommended"]["data"]["risk"],
                "confidence": pricing_recommendations["recommended"]["confidence"]
            }
        }


# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = CostAnalyzer()
    
    # Example cost analysis
    cost_breakdown = analyzer.analyze_cost_structure(
        base_cost=800,  # $8.00
        selling_price=1999,  # $19.99
        additional_costs={
            "shipping_cost": 200,  # $2.00
            "processing_fee": 100,  # $1.00
            "packaging_cost": 50   # $0.50
        }
    )
    
    print(f"Cost breakdown: {cost_breakdown}")
    
    # Profit analysis
    profit_analysis = analyzer.calculate_profit_analysis(1999, cost_breakdown)
    print(f"Profit analysis: {profit_analysis}")
    
    # Pricing recommendations
    recommendations = analyzer.recommend_pricing_strategy(
        cost_breakdown, 
        MarketPosition.MID_RANGE,
        [1599, 1799, 2199, 2499]  # Competitor prices
    )
    
    print(f"Best strategy: {recommendations['recommended']['strategy'].value}")
    print(f"Recommended price: ${recommendations['recommended']['data']['price']/100:.2f}")
    
    # Full report
    report = analyzer.generate_pricing_report(
        "test_product", cost_breakdown, 1999, 
        MarketPosition.MID_RANGE, [1599, 1799, 2199, 2499]
    )
    
    print(f"Report summary: {report['summary']}")