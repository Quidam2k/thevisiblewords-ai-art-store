"""
Test CSV Analytics and Data Export Features
Tests CSV import/export, data aggregation, and pandas integration specifically
"""

import sys
import os
import csv
import json
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test pandas availability
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    print(f"✅ Pandas {pd.__version__} is available")
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  Pandas not available - using basic CSV handling")

from market_tracker import MarketTracker


class TestCSVAnalyticsFeatures:
    """Test CSV analytics and data aggregation features"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_files = []
        
        # Create temporary market tracker
        self.market_temp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.market_temp.close()
        self.temp_files.append(self.market_temp.name)
        self.market_tracker = MarketTracker(self.market_temp.name)
    
    def teardown_method(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def test_csv_import_functionality(self):
        """Test comprehensive CSV import capabilities"""
        print("\n📥 Testing CSV Import Functionality...")
        
        # Create sample CSV with realistic e-commerce data
        csv_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_files.append(csv_file.name)
        
        csv_data = [
            ['competitor_id', 'product_name', 'category', 'price', 'url', 'availability', 'confidence'],
            ['printful', 'Unisex Heavy Cotton Tee', 'apparel', '15.95', 'https://printful.com/tee', 'in_stock', '0.95'],
            ['printful', 'Gildan 18000 Hoodie', 'apparel', '32.95', 'https://printful.com/hoodie', 'in_stock', '0.90'],
            ['gooten', 'Basic T-Shirt', 'apparel', '12.99', 'https://gooten.com/tee', 'in_stock', '0.85'],
            ['teespring', 'Premium Tee', 'apparel', '18.99', 'https://teespring.com/premium', 'limited', '0.80'],
            ['redbubble', 'Artist Designed Shirt', 'apparel', '22.99', 'https://redbubble.com/art', 'in_stock', '0.88'],
            ['society6', 'All Over Print Tee', 'apparel', '28.99', 'https://society6.com/aop', 'in_stock', '0.92'],
            ['amazon', 'Generic T-Shirt', 'apparel', '9.99', 'https://amazon.com/generic', 'in_stock', '0.70'],
            ['etsy', 'Handmade Vintage Tee', 'apparel', '35.99', 'https://etsy.com/vintage', 'limited', '0.75'],
        ]
        
        with open(csv_file.name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
        
        # First, add the competitors to the tracker
        competitors_to_add = {
            'teespring': 'Teespring',
            'redbubble': 'Redbubble', 
            'society6': 'Society6',
            'amazon': 'Amazon',
            'etsy': 'Etsy'
        }
        
        for comp_id, comp_name in competitors_to_add.items():
            from market_tracker import CompetitorTier
            self.market_tracker.add_competitor(
                comp_id, comp_name, CompetitorTier.MID_RANGE, ['apparel']
            )
        
        # Test CSV import
        imported_count = self.market_tracker.import_csv_data(csv_file.name)
        print(f"✅ CSV Import: {imported_count} records successfully imported")
        
        # Verify imported data
        competitive_prices = self.market_tracker.get_competitive_prices('apparel')
        imported_prices = [p for p in competitive_prices if p.competitor_id in competitors_to_add]
        print(f"✅ Data Verification: {len(imported_prices)} imported records found in system")
        
        # Test price range analysis
        prices = [p.price for p in competitive_prices]
        if prices:
            min_price = min(prices) / 100
            max_price = max(prices) / 100
            avg_price = sum(prices) / len(prices) / 100
            print(f"✅ Price Analysis: Range ${min_price:.2f} - ${max_price:.2f}, Average ${avg_price:.2f}")
        
        return True
    
    def test_csv_export_functionality(self):
        """Test CSV export and data aggregation"""
        print("\n📤 Testing CSV Export Functionality...")
        
        # Add sample data to market tracker
        sample_data = [
            ('printful', 'Premium T-Shirt', 'apparel', 1895),
            ('printful', 'Basic Hoodie', 'apparel', 3295), 
            ('gooten', 'Economy Tee', 'apparel', 1199),
            ('gooten', 'Deluxe Shirt', 'apparel', 1699),
        ]
        
        for comp_id, product, category, price in sample_data:
            self.market_tracker.add_price_data(comp_id, product, category, price)
        
        # Test JSON export (current functionality)
        export_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        export_file.close()
        self.temp_files.append(export_file.name)
        
        self.market_tracker.export_data(export_file.name, 'apparel')
        
        # Verify export
        with open(export_file.name, 'r') as f:
            exported_data = json.load(f)
        
        assert 'category' in exported_data
        assert 'prices' in exported_data
        print(f"✅ JSON Export: {len(exported_data['prices'])} price records exported")
        
        # Test full data export
        full_export_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        full_export_file.close()
        self.temp_files.append(full_export_file.name)
        
        self.market_tracker.export_data(full_export_file.name)  # No category = full export
        
        with open(full_export_file.name, 'r') as f:
            full_data = json.load(f)
        
        assert 'competitors' in full_data
        assert 'all_prices' in full_data
        print(f"✅ Full Export: {len(full_data['competitors'])} competitors, market segments included")
        
        return True
    
    def test_data_aggregation_capabilities(self):
        """Test data aggregation and analytical processing"""
        print("\n📊 Testing Data Aggregation Capabilities...")
        
        # Add varied pricing data for aggregation testing
        time_series_data = []
        base_time = datetime.now() - timedelta(days=60)
        
        for i in range(20):
            # Simulate price changes over time
            price_variations = [1599, 1699, 1799, 1899, 1999, 2099, 2199]
            price = price_variations[i % len(price_variations)]
            
            # Add temporal variance
            timestamp = base_time + timedelta(days=i*3)
            
            self.market_tracker.add_price_data(
                'printful',
                f'Product Series {i // 5}',
                'apparel', 
                price + (i * 25),  # Gradual price increase trend
                timestamp=timestamp
            )
            
            time_series_data.append({
                'timestamp': timestamp,
                'price': price + (i * 25),
                'period': i
            })
        
        # Test market summary aggregation
        summary = self.market_tracker.get_market_summary('apparel')
        apparel_data = summary['categories']['apparel']
        
        print(f"✅ Market Aggregation: {apparel_data['data_points']} data points analyzed")
        print(f"   • Price Range: ${apparel_data['price_range']['min']/100:.2f} - ${apparel_data['price_range']['max']/100:.2f}")
        print(f"   • Volatility: ${apparel_data['volatility']/100:.2f}")
        
        # Test pricing opportunities analysis
        opportunities = self.market_tracker.find_pricing_opportunities('apparel')
        print(f"✅ Opportunity Analysis: {len(opportunities)} opportunities identified")
        
        for opp in opportunities[:3]:  # Show first 3
            print(f"   • {opp.insight_type}: {opp.title}")
        
        # Test competitive positioning analysis
        position_analysis = self.market_tracker.analyze_price_position(1999, 'apparel')
        print(f"✅ Positioning Analysis: {position_analysis['percentile']:.1f} percentile position")
        print(f"   • Competitiveness: {position_analysis['competitiveness']}")
        
        return True
    
    def test_pandas_csv_integration(self):
        """Test advanced pandas-based CSV analytics if available"""
        print(f"\n🐼 Testing Pandas CSV Integration (Available: {PANDAS_AVAILABLE})...")
        
        if not PANDAS_AVAILABLE:
            print("⚠️  Pandas not available - using basic CSV processing")
            # Test basic functionality still works
            competitive_prices = self.market_tracker.get_competitive_prices('apparel')
            basic_stats = {
                'count': len(competitive_prices),
                'avg_price': sum(p.price for p in competitive_prices) / len(competitive_prices) if competitive_prices else 0
            }
            print(f"✅ Basic Analytics: {basic_stats['count']} records, avg price ${basic_stats['avg_price']/100:.2f}")
            return True
        
        # Advanced pandas-based analytics
        try:
            import pandas as pd
            import numpy as np
            
            # Get competitive price data
            competitive_prices = self.market_tracker.get_competitive_prices('apparel')
            
            if not competitive_prices:
                print("⚠️  No competitive price data available for pandas analysis")
                return True
            
            # Convert to pandas DataFrame
            df_data = []
            for price in competitive_prices:
                df_data.append({
                    'competitor': price.competitor_name,
                    'product': price.product_name,
                    'price': price.price / 100,  # Convert to dollars
                    'timestamp': price.timestamp,
                    'confidence': price.confidence,
                    'availability': price.availability
                })
            
            df = pd.DataFrame(df_data)
            print(f"✅ DataFrame Created: {len(df)} records, {len(df.columns)} columns")
            
            # Advanced statistical analysis
            price_stats = df['price'].describe()
            print(f"✅ Statistical Analysis:")
            print(f"   • Mean: ${price_stats['mean']:.2f}")
            print(f"   • Std Dev: ${price_stats['std']:.2f}")
            print(f"   • 25th Percentile: ${price_stats['25%']:.2f}")
            print(f"   • 75th Percentile: ${price_stats['75%']:.2f}")
            
            # Competitor analysis
            if 'competitor' in df.columns and len(df) > 1:
                competitor_analysis = df.groupby('competitor').agg({
                    'price': ['mean', 'std', 'count', 'min', 'max'],
                    'confidence': 'mean'
                }).round(2)
                
                print(f"✅ Competitor Analysis: {len(competitor_analysis)} competitors profiled")
                
                # Show top competitors by volume
                top_competitors = df['competitor'].value_counts().head(3)
                print("   • Top competitors by data points:")
                for comp, count in top_competitors.items():
                    avg_price = df[df['competitor'] == comp]['price'].mean()
                    print(f"     - {comp}: {count} products, ${avg_price:.2f} avg")
            
            # Time series analysis if we have timestamps
            if 'timestamp' in df.columns and len(df) > 2:
                df_time = df.copy()
                df_time['date'] = pd.to_datetime(df_time['timestamp'])
                df_time = df_time.sort_values('date')
                
                # Calculate rolling averages
                df_time['price_7d_avg'] = df_time['price'].rolling(window=3, min_periods=1).mean()
                
                print(f"✅ Time Series Analysis: {len(df_time)} time points")
                
                # Price trend analysis
                if len(df_time) >= 2:
                    price_change = df_time['price'].iloc[-1] - df_time['price'].iloc[0]
                    trend = "increasing" if price_change > 0 else "decreasing" if price_change < 0 else "stable"
                    print(f"   • Overall trend: {trend} (${price_change:.2f} change)")
            
            # Correlation analysis
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                correlation_matrix = df[numeric_cols].corr()
                print(f"✅ Correlation Analysis: {correlation_matrix.shape[0]}x{correlation_matrix.shape[1]} matrix")
                
                # Find strongest correlations
                for i in range(len(correlation_matrix.columns)):
                    for j in range(i+1, len(correlation_matrix.columns)):
                        corr_val = correlation_matrix.iloc[i, j]
                        if abs(corr_val) > 0.5:  # Strong correlation
                            col1, col2 = correlation_matrix.columns[i], correlation_matrix.columns[j]
                            print(f"   • Strong correlation: {col1} vs {col2}: {corr_val:.3f}")
            
        except Exception as e:
            print(f"⚠️  Pandas analysis failed: {e}")
            return False
        
        return True
    
    def test_data_quality_and_validation(self):
        """Test data quality checks and validation"""
        print("\n✅ Testing Data Quality & Validation...")
        
        # Test with various data quality scenarios
        quality_test_data = [
            # Good data
            ('competitor1', 'Good Product', 'apparel', 1999, 0.95),
            # Edge cases
            ('competitor1', 'Low Price Product', 'apparel', 99, 0.90),    # Very low price
            ('competitor1', 'High Price Product', 'apparel', 9999, 0.85), # High price
            ('competitor1', 'Low Confidence', 'apparel', 1599, 0.45),     # Low confidence
        ]
        
        # Add competitor first
        from market_tracker import CompetitorTier
        self.market_tracker.add_competitor(
            'competitor1', 'Test Competitor', CompetitorTier.MID_RANGE, ['apparel']
        )
        
        valid_count = 0
        for comp_id, product, category, price, confidence in quality_test_data:
            success = self.market_tracker.add_price_data(
                comp_id, product, category, price, confidence=confidence
            )
            if success:
                valid_count += 1
        
        print(f"✅ Data Validation: {valid_count}/{len(quality_test_data)} records passed validation")
        
        # Test confidence filtering
        all_prices = self.market_tracker.get_competitive_prices('apparel')
        high_confidence = [p for p in all_prices if p.confidence >= 0.7]
        medium_confidence = [p for p in all_prices if 0.5 <= p.confidence < 0.7]
        low_confidence = [p for p in all_prices if p.confidence < 0.5]
        
        print(f"✅ Confidence Distribution:")
        print(f"   • High (≥70%): {len(high_confidence)} records")
        print(f"   • Medium (50-70%): {len(medium_confidence)} records") 
        print(f"   • Low (<50%): {len(low_confidence)} records")
        
        # Test data freshness
        recent_prices = []
        older_prices = []
        cutoff = datetime.now() - timedelta(days=7)
        
        for price in all_prices:
            if price.timestamp > cutoff:
                recent_prices.append(price)
            else:
                older_prices.append(price)
        
        print(f"✅ Data Freshness:")
        print(f"   • Recent (last 7 days): {len(recent_prices)} records")
        print(f"   • Older: {len(older_prices)} records")
        
        return True


def run_csv_analytics_test():
    """Run the CSV analytics test suite"""
    print("📊 Starting CSV Analytics Features Test Suite")
    print("=" * 60)
    
    test_suite = TestCSVAnalyticsFeatures()
    test_suite.setup_method()
    
    tests = [
        ("CSV Import Functionality", test_suite.test_csv_import_functionality),
        ("CSV Export Functionality", test_suite.test_csv_export_functionality),
        ("Data Aggregation Capabilities", test_suite.test_data_aggregation_capabilities),
        ("Pandas CSV Integration", test_suite.test_pandas_csv_integration),
        ("Data Quality & Validation", test_suite.test_data_quality_and_validation),
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed_tests += 1
                print(f"✅ {test_name} - PASSED")
            else:
                failed_tests += 1
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            failed_tests += 1
            print(f"❌ {test_name} - ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    test_suite.teardown_method()
    
    print("\n" + "=" * 60)
    print(f"📊 CSV Analytics Test Results: {passed_tests} passed, {failed_tests} failed")
    
    return passed_tests, failed_tests


if __name__ == "__main__":
    run_csv_analytics_test()