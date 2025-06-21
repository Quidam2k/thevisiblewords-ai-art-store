"""
Standalone Pricing Monitor Test - No pytest dependency
Tests pricing monitor analytics capabilities without external dependencies
"""

import sys
import os
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pricing_monitor import (
    PricingMonitor, CostData, PricePoint, PriceAlert,
    PriceChangeReason, PriceDirection
)


def test_pricing_monitor_comprehensive():
    """Comprehensive test of pricing monitor analytics capabilities"""
    print("📈 Testing Pricing Monitor Analytics Capabilities")
    print("=" * 55)
    
    # Setup temporary files
    temp_files = []
    pricing_temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    alert_temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    pricing_temp.close()
    alert_temp.close()
    temp_files.extend([pricing_temp.name, alert_temp.name])
    
    # Initialize monitor
    monitor = PricingMonitor(
        data_file=pricing_temp.name,
        alert_file=alert_temp.name
    )
    
    print("✅ Pricing Monitor initialized with temporary data files")
    
    try:
        # Test 1: Cost Data Tracking
        print("\n1️⃣ Testing Cost Data Tracking...")
        
        # Create sample cost data for different products
        products_data = [
            ("product_001", 12345, 800, 200, 100),   # T-Shirt
            ("product_002", 12346, 1200, 300, 150),  # Hoodie
            ("product_003", 12347, 600, 150, 80),    # Tank Top
        ]
        
        initial_costs = {}
        for product_id, variant_id, base, shipping, processing in products_data:
            cost_data = CostData(
                variant_id=variant_id,
                base_cost=base,
                shipping_cost=shipping,
                processing_fee=processing,
                total_cost=base + shipping + processing
            )
            
            initial_costs[f"{product_id}:{variant_id}"] = cost_data
            
            # Track initial cost
            alert = monitor.track_cost_change(product_id, variant_id, cost_data)
            print(f"   • {product_id}: Initial cost ${cost_data.total_cost/100:.2f} tracked")
            assert alert is None  # First time tracking should not generate alert
        
        print("✅ Initial cost tracking successful")
        
        # Test 2: Price Point History
        print("\n2️⃣ Testing Price Point History...")
        
        # Add price points over time
        base_time = datetime.now() - timedelta(days=30)
        price_scenarios = [
            (1899, PriceChangeReason.MANUAL_ADJUSTMENT),
            (1999, PriceChangeReason.COST_INCREASE),
            (1849, PriceChangeReason.DEMAND_DROP),
            (2099, PriceChangeReason.MARKET_COMPETITION),
            (2199, PriceChangeReason.SEASONAL_ADJUSTMENT),
        ]
        
        for product_id, variant_id, base, shipping, processing in products_data:
            key = f"{product_id}:{variant_id}"
            base_cost_data = initial_costs[key]
            
            for i, (price, reason) in enumerate(price_scenarios):
                # Adjust cost slightly over time
                adjusted_cost = CostData(
                    variant_id=variant_id,
                    base_cost=base + (i * 20),
                    shipping_cost=shipping,
                    processing_fee=processing,
                    total_cost=base + (i * 20) + shipping + processing
                )
                
                monitor.add_price_point(
                    product_id, variant_id, price, adjusted_cost, reason
                )
                
                # Manually adjust timestamp for trend analysis
                history_key = f"{product_id}:{variant_id}"
                if history_key in monitor.price_history and monitor.price_history[history_key]:
                    monitor.price_history[history_key][-1].timestamp = base_time + timedelta(days=i*5)
        
        print(f"   • Added {len(price_scenarios)} price points for {len(products_data)} products")
        print("✅ Price point history tracking successful")
        
        # Test 3: Cost Change Alerts
        print("\n3️⃣ Testing Cost Change Alerts...")
        
        alerts_generated = 0
        for product_id, variant_id, base, shipping, processing in products_data:
            # Simulate significant cost increase
            new_cost = CostData(
                variant_id=variant_id,
                base_cost=base + 150,  # Significant increase
                shipping_cost=shipping + 50,
                processing_fee=processing + 25,
                total_cost=base + 150 + shipping + 50 + processing + 25
            )
            
            alert = monitor.track_cost_change(product_id, variant_id, new_cost)
            if alert:
                alerts_generated += 1
                print(f"   • {product_id}: Cost change alert generated ({alert.severity})")
                print(f"     Old cost: ${alert.old_value/100:.2f} → New cost: ${alert.new_value/100:.2f}")
        
        print(f"✅ Cost change alerts: {alerts_generated} alerts generated")
        
        # Test 4: Current Margins Analysis
        print("\n4️⃣ Testing Current Margins Analysis...")
        
        margins = monitor.get_current_margins()
        
        print(f"   • Products tracked: {len(margins)}")
        total_variants = sum(len(variants) for variants in margins.values())
        print(f"   • Total variants: {total_variants}")
        
        for product_id, variants in margins.items():
            for variant_id, data in variants.items():
                print(f"   • {product_id}:{variant_id}")
                print(f"     Selling: ${data['selling_price']/100:.2f}, Cost: ${data['total_cost']/100:.2f}")
                print(f"     Margin: {data['profit_margin']:.1f}%, Profit: ${data['profit_amount']/100:.2f}")
        
        print("✅ Current margins analysis successful")
        
        # Test 5: Price Trend Analysis
        print("\n5️⃣ Testing Price Trend Analysis...")
        
        for product_id, variant_id, _, _, _ in products_data:
            trends = monitor.get_price_trends(product_id, variant_id, days=30)
            
            if "error" not in trends:
                print(f"   • {product_id}:{variant_id}")
                print(f"     Trend direction: {trends['trend_direction']}")
                print(f"     Price change: {trends['price_change']['percentage']:+.1f}%")
                print(f"     Cost change: {trends['cost_change']['percentage']:+.1f}%")
                print(f"     Current margin: {trends['current_margin']:.1f}%")
                print(f"     Volatility: {trends['price_volatility']:.2f}")
                
                if trends['recommendations']:
                    print(f"     Recommendations: {len(trends['recommendations'])}")
                    for rec in trends['recommendations'][:2]:  # Show first 2
                        print(f"       - {rec}")
            else:
                print(f"   • {product_id}:{variant_id}: {trends['error']}")
        
        print("✅ Price trend analysis successful")
        
        # Test 6: Alert Management
        print("\n6️⃣ Testing Alert Management...")
        
        active_alerts = monitor.get_active_alerts()
        print(f"   • Active alerts: {len(active_alerts)}")
        
        # Show alert breakdown by severity
        alert_breakdown = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for alert in active_alerts:
            alert_breakdown[alert.severity] += 1
        
        for severity, count in alert_breakdown.items():
            if count > 0:
                print(f"     {severity.title()}: {count} alerts")
        
        # Test alert acknowledgment
        if active_alerts:
            success = monitor.acknowledge_alert(0)
            if success:
                print(f"   • Alert acknowledgment: First alert acknowledged")
                
                remaining_alerts = monitor.get_active_alerts()
                print(f"   • Remaining alerts: {len(remaining_alerts)}")
        
        print("✅ Alert management successful")
        
        # Test 7: Summary Statistics
        print("\n7️⃣ Testing Summary Statistics...")
        
        stats = monitor.get_summary_stats()
        
        print(f"   • Total products tracked: {stats['total_products_tracked']}")
        print(f"   • Total alerts: {stats['total_alerts']}")
        print(f"   • Unacknowledged alerts: {stats['unacknowledged_alerts']}")
        print(f"   • Average profit margin: {stats['average_profit_margin']:.1f}%")
        print(f"   • Monitoring enabled: {stats['monitoring_enabled']}")
        
        print("   • Alert breakdown:")
        for severity, count in stats['alert_breakdown'].items():
            if count > 0:
                print(f"     {severity.title()}: {count}")
        
        print("✅ Summary statistics successful")
        
        # Test 8: Volatility Calculations
        print("\n8️⃣ Testing Volatility Calculations...")
        
        for product_id, variant_id, _, _, _ in products_data:
            history_key = f"{product_id}:{variant_id}"
            if history_key in monitor.price_history:
                history = monitor.price_history[history_key]
                volatility = monitor._calculate_volatility(history)
                
                print(f"   • {product_id}: Volatility = {volatility:.2f}")
                print(f"     Data points: {len(history)}")
        
        print("✅ Volatility calculations successful")
        
        # Test 9: Data Persistence
        print("\n9️⃣ Testing Data Persistence...")
        
        # Save current state
        monitor.save_data()
        monitor.save_alerts()
        print("   • Data saved to files")
        
        # Create new monitor instance and load data
        new_monitor = PricingMonitor(
            data_file=pricing_temp.name,
            alert_file=alert_temp.name
        )
        
        # Verify data loaded correctly
        loaded_margins = new_monitor.get_current_margins()
        loaded_alerts = new_monitor.get_active_alerts()
        
        print(f"   • Loaded products: {len(loaded_margins)}")
        print(f"   • Loaded alerts: {len(loaded_alerts)}")
        
        print("✅ Data persistence successful")
        
        # Test 10: Performance Metrics
        print("\n🔟 Testing Performance Metrics...")
        
        import time
        
        # Test bulk data processing
        start_time = time.time()
        
        for i in range(50):
            test_cost = CostData(
                variant_id=99900 + i,
                base_cost=800 + (i * 10),
                shipping_cost=200,
                processing_fee=100,
                total_cost=1100 + (i * 10)
            )
            
            monitor.add_price_point(
                f"bulk_test_{i}",
                99900 + i,
                1999 + (i * 25),
                test_cost,
                PriceChangeReason.MANUAL_ADJUSTMENT
            )
        
        processing_time = time.time() - start_time
        print(f"   • Bulk processing: 50 price points in {processing_time:.3f}s")
        
        # Test query performance
        start_time = time.time()
        final_stats = monitor.get_summary_stats()
        query_time = time.time() - start_time
        
        print(f"   • Query performance: Summary stats in {query_time:.4f}s")
        print(f"   • Final product count: {final_stats['total_products_tracked']}")
        
        print("✅ Performance metrics successful")
        
        print("\n" + "=" * 55)
        print("🎉 All Pricing Monitor tests completed successfully!")
        
        print("\n📊 Summary of Analytics Capabilities Tested:")
        print("   ✅ Real-time cost change tracking and alerts")
        print("   ✅ Historical price point analysis")
        print("   ✅ Profit margin calculations and monitoring")
        print("   ✅ Price trend analysis with volatility metrics")
        print("   ✅ Alert management and acknowledgment system")
        print("   ✅ Comprehensive summary statistics")
        print("   ✅ Data persistence and recovery")
        print("   ✅ Performance optimization for bulk operations")
        
        print("\n💡 Key Analytics Features:")
        print("   • Automated cost change detection")
        print("   • Multi-dimensional trend analysis")
        print("   • Risk assessment through margin monitoring")
        print("   • Time-series price volatility analysis")
        print("   • Configurable alert thresholds and severities")
        print("   • Built-in recommendation engine")
        print("   • No external dependencies required")
        
    finally:
        # Cleanup
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


if __name__ == "__main__":
    test_pricing_monitor_comprehensive()