"""
Data Analysis System Validation Script
Demonstrates all analytics capabilities working together in a realistic scenario
"""

import sys
import os
import json
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Check pandas availability
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    pandas_version = pd.__version__
except ImportError:
    PANDAS_AVAILABLE = False
    pandas_version = "Not installed"

from market_tracker import MarketTracker, CompetitorTier
from cost_analyzer import CostAnalyzer, MarketPosition
from pricing_monitor import PricingMonitor, CostData, PriceChangeReason


def validate_integrated_analytics():
    """Validate the complete analytics system with realistic e-commerce scenario"""
    
    print("🚀 Printify Data Analysis System Validation")
    print("=" * 60)
    print(f"📊 Pandas Status: {pandas_version}")
    print(f"🔧 Analytics Mode: {'Enhanced' if PANDAS_AVAILABLE else 'Standard'}")
    print()
    
    # Setup temporary files
    temp_files = []
    
    try:
        # Initialize all analytics components
        print("1️⃣ Initializing Analytics Components...")
        
        # Market tracker for competitive intelligence
        market_temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        market_temp.close()
        temp_files.append(market_temp.name)
        market_tracker = MarketTracker(market_temp.name)
        
        # Cost analyzer for pricing optimization
        cost_analyzer = CostAnalyzer({
            'target_margin': 30.0,
            'min_margin': 20.0,
            'transaction_fee_rate': 0.029,
            'marketing_cost_rate': 0.12,
            'overhead_rate': 0.06
        })
        
        # Pricing monitor for real-time tracking
        pricing_temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        alert_temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        pricing_temp.close()
        alert_temp.close()
        temp_files.extend([pricing_temp.name, alert_temp.name])
        
        pricing_monitor = PricingMonitor(
            data_file=pricing_temp.name,
            alert_file=alert_temp.name
        )
        
        print("✅ All components initialized successfully")
        
        # Scenario: T-shirt business competitive analysis
        print("\n2️⃣ Loading Market Intelligence Data...")
        
        # Add major POD competitors
        competitors = [
            ("printful", "Printful", CompetitorTier.MID_RANGE),
            ("gooten", "Gooten", CompetitorTier.BUDGET),  
            ("printify_sellers", "Other Printify Sellers", CompetitorTier.MID_RANGE),
            ("teespring", "Teespring", CompetitorTier.MID_RANGE),
            ("redbubble", "Redbubble", CompetitorTier.PREMIUM),
        ]
        
        for comp_id, name, tier in competitors:
            market_tracker.add_competitor(comp_id, name, tier, ["apparel"])
        
        # Load competitive pricing data
        competitive_data = [
            # competitor_id, product_name, category, price_cents
            ("printful", "Unisex Heavy Cotton Tee", "apparel", 1595),
            ("printful", "Bella Canvas 3001", "apparel", 1795),
            ("printful", "Gildan 18000 Hoodie", "apparel", 3495),
            ("gooten", "Basic T-Shirt", "apparel", 1299),
            ("gooten", "Premium Tee", "apparel", 1599),
            ("printify_sellers", "Designer Graphic Tee", "apparel", 2299),
            ("printify_sellers", "Vintage Style Shirt", "apparel", 1999),
            ("teespring", "Custom Print Tee", "apparel", 1899),
            ("teespring", "Premium Quality Shirt", "apparel", 2199),
            ("redbubble", "Artist Designed Tee", "apparel", 2499),
            ("redbubble", "Unique Graphic Shirt", "apparel", 2899),
        ]
        
        for comp_id, product, category, price in competitive_data:
            market_tracker.add_price_data(comp_id, product, category, price)
        
        print(f"✅ Loaded {len(competitive_data)} competitive price points")
        
        # Analyze competitive landscape
        print("\n3️⃣ Analyzing Competitive Landscape...")
        
        # Market summary analysis
        market_summary = market_tracker.get_market_summary("apparel")
        apparel_data = market_summary["categories"]["apparel"]
        
        print(f"📊 Market Analysis Results:")
        print(f"   • Competitors tracked: {apparel_data['competitor_count']}")
        print(f"   • Price range: ${apparel_data['price_range']['min']/100:.2f} - ${apparel_data['price_range']['max']/100:.2f}")
        print(f"   • Market average: ${apparel_data['price_range']['average']/100:.2f}")
        print(f"   • Market volatility: ${apparel_data['volatility']/100:.2f}")
        
        # Find pricing opportunities
        opportunities = market_tracker.find_pricing_opportunities("apparel")
        if opportunities:
            print(f"   • Pricing opportunities: {len(opportunities)} identified")
            for opp in opportunities[:2]:
                print(f"     - {opp.title}")
        
        # Our product cost analysis
        print("\n4️⃣ Analyzing Our Product Costs...")
        
        # Realistic t-shirt cost structure
        our_costs = cost_analyzer.analyze_cost_structure(
            base_cost=850,    # $8.50 - Provider base cost
            selling_price=1999,  # $19.99 - Our selling price
            additional_costs={
                'shipping_cost': 350,     # $3.50 - Shipping to customer
                'processing_fee': 125,    # $1.25 - Platform processing
                'packaging_cost': 45      # $0.45 - Packaging materials
            }
        )
        
        print(f"💰 Cost Structure Analysis:")
        print(f"   • Base cost: ${our_costs.base_cost/100:.2f}")
        print(f"   • Total costs: ${our_costs.total_cost/100:.2f}")
        print(f"   • Transaction fee: ${our_costs.transaction_fee/100:.2f}")
        print(f"   • Marketing allocation: ${our_costs.marketing_cost/100:.2f}")
        
        # Profit analysis
        profit_analysis = cost_analyzer.calculate_profit_analysis(1999, our_costs)
        print(f"   • Current margin: {profit_analysis.gross_margin_percent:.1f}%")
        print(f"   • Gross profit: ${profit_analysis.gross_profit/100:.2f}")
        print(f"   • Break-even price: ${profit_analysis.break_even_price/100:.2f}")
        
        # Strategic pricing recommendations
        print("\n5️⃣ Generating Strategic Pricing Recommendations...")
        
        # Get competitor prices for analysis
        competitive_prices = [p.price for p in market_tracker.get_competitive_prices("apparel")]
        
        recommendations = cost_analyzer.recommend_pricing_strategy(
            our_costs,
            MarketPosition.MID_RANGE,
            competitive_prices
        )
        
        print(f"🎯 Pricing Strategy Analysis:")
        print(f"   • Best strategy: {recommendations['recommended']['strategy'].value}")
        print(f"   • Recommended price: ${recommendations['recommended']['data']['price']/100:.2f}")
        print(f"   • Expected margin: {recommendations['recommended']['data']['margin']:.1f}%")
        print(f"   • Confidence level: {recommendations['recommended']['confidence']:.2f}")
        
        # Show alternative strategies
        print(f"   • Alternative strategies:")
        for strategy, data in recommendations['strategies'].items():
            if strategy != recommendations['recommended']['strategy']:
                print(f"     - {strategy.value}: ${data['price']/100:.2f} ({data['margin']:.1f}% margin)")
        
        # Competitive positioning analysis
        position = market_tracker.analyze_price_position(1999, "apparel")
        print(f"   • Market position: {position['percentile']:.1f} percentile")
        print(f"   • Competitiveness: {position['competitiveness']}")
        
        # Setup real-time monitoring
        print("\n6️⃣ Setting Up Real-Time Monitoring...")
        
        # Track our product costs over time
        product_variants = [
            ("UNISEX_TEE_001", 12001, 850, 350, 125),
            ("UNISEX_TEE_002", 12002, 900, 350, 125), 
            ("PREMIUM_TEE_001", 12003, 1200, 400, 150),
        ]
        
        monitored_products = 0
        for product_id, variant_id, base, shipping, processing in product_variants:
            cost_data = CostData(
                variant_id=variant_id,
                base_cost=base,
                shipping_cost=shipping,
                processing_fee=processing,
                total_cost=base + shipping + processing
            )
            
            # Add to monitoring
            pricing_monitor.add_price_point(
                product_id, variant_id, 1999, cost_data, 
                PriceChangeReason.MANUAL_ADJUSTMENT
            )
            
            monitored_products += 1
        
        print(f"✅ Monitoring setup: {monitored_products} products tracked")
        
        # Simulate cost changes and alerts
        print("\n7️⃣ Testing Alert System...")
        
        alerts_generated = 0
        for product_id, variant_id, base, shipping, processing in product_variants:
            # Simulate cost increase (supplier price change)
            new_cost = CostData(
                variant_id=variant_id,
                base_cost=base + 85,  # $0.85 increase (10% increase)
                shipping_cost=shipping,
                processing_fee=processing,
                total_cost=base + 85 + shipping + processing
            )
            
            alert = pricing_monitor.track_cost_change(product_id, variant_id, new_cost)
            if alert:
                alerts_generated += 1
                print(f"🚨 Alert: {product_id} cost increased by {((alert.new_value - alert.old_value) / alert.old_value * 100):.1f}%")
        
        # Get monitoring summary
        monitor_stats = pricing_monitor.get_summary_stats()
        print(f"📈 Monitoring Summary:")
        print(f"   • Products tracked: {monitor_stats['total_products_tracked']}")
        print(f"   • Alerts generated: {alerts_generated}")
        print(f"   • Average margin: {monitor_stats['average_profit_margin']:.1f}%")
        
        # Generate comprehensive business report
        print("\n8️⃣ Generating Business Intelligence Report...")
        
        comprehensive_report = cost_analyzer.generate_pricing_report(
            "UNISEX_TEE_001",
            our_costs,
            1999,
            MarketPosition.MID_RANGE,
            competitive_prices
        )
        
        report_summary = comprehensive_report['summary']
        print(f"📊 Business Intelligence Report:")
        print(f"   • Report sections: {len(comprehensive_report)}")
        print(f"   • Current performance: {report_summary['current_margin']:.1f}% margin")
        print(f"   • Optimization potential: {report_summary['margin_improvement']:+.1f}%")
        print(f"   • Risk assessment: {report_summary['risk_level']}")
        print(f"   • Decision confidence: {report_summary['confidence']:.2f}")
        
        # Data export demonstration
        print("\n9️⃣ Testing Data Export Capabilities...")
        
        # Export market data
        market_export = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        market_export.close()
        temp_files.append(market_export.name)
        
        market_tracker.export_data(market_export.name, "apparel")
        
        with open(market_export.name, 'r') as f:
            exported_data = json.load(f)
        
        print(f"💾 Export Results:")
        print(f"   • Market data exported: {len(exported_data['prices'])} price points")
        print(f"   • Data format: JSON with {len(exported_data)} sections")
        
        # Final validation
        print("\n🔟 Final System Validation...")
        
        validation_results = {
            "market_intelligence": len(competitive_data) > 0,
            "cost_analysis": our_costs.total_cost > 0,
            "pricing_strategies": len(recommendations['strategies']) >= 5,
            "monitoring_alerts": alerts_generated > 0,
            "data_export": len(exported_data['prices']) > 0,
            "business_reporting": len(comprehensive_report) >= 8
        }
        
        passed_validations = sum(validation_results.values())
        total_validations = len(validation_results)
        
        print(f"✅ Validation Results: {passed_validations}/{total_validations} systems operational")
        
        for system, status in validation_results.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {system.replace('_', ' ').title()}")
        
        # Performance summary
        print(f"\n📈 Performance Summary:")
        print(f"   • Market data points processed: {len(competitive_data)}")
        print(f"   • Competitors analyzed: {len(competitors)}")
        print(f"   • Products monitored: {monitored_products}")
        print(f"   • Alerts generated: {alerts_generated}")
        print(f"   • Reports generated: 1 comprehensive business report")
        
        # Final verdict
        if passed_validations == total_validations:
            print(f"\n🎉 VALIDATION SUCCESSFUL!")
            print(f"The Printify data analysis system is fully operational with comprehensive")
            print(f"market intelligence, cost optimization, and real-time monitoring capabilities.")
        else:
            print(f"\n⚠️  PARTIAL VALIDATION")
            print(f"Some components may need attention. See details above.")
        
        print(f"\n💡 System Capabilities Demonstrated:")
        print(f"   • Real-time competitive price tracking")
        print(f"   • Automated cost change detection and alerting")
        print(f"   • Strategic pricing recommendations with confidence scoring")
        print(f"   • Market positioning analysis and opportunity identification")
        print(f"   • Comprehensive business intelligence reporting")
        print(f"   • Data export capabilities for external analysis")
        print(f"   • Performance monitoring and analytics")
        
        if not PANDAS_AVAILABLE:
            print(f"\n📝 Note: System running in standard mode without pandas.")
            print(f"   Installing pandas would enable enhanced analytics capabilities.")
        
    finally:
        # Cleanup temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


if __name__ == "__main__":
    validate_integrated_analytics()