#!/usr/bin/env python3
"""
Example Usage of Multi-Region Electricity Data Collector
=======================================================

This script demonstrates how to use the multi-region data collector
to gather electricity data from different sources.
"""

from multi_region_electricity_data_collector import MultiRegionElectricityDataCollector
import json

def main():
    print("🔌 Multi-Region Electricity Data Collection Example")
    print("=" * 55)
    
    # Initialize the collector
    print("\n1️⃣ Initializing collector...")
    collector = MultiRegionElectricityDataCollector()
    
    # Show available data sources
    print("\n2️⃣ Available data sources:")
    summary = collector.get_data_availability_summary()
    for region, info in summary['regions'].items():
        print(f"   • {info['name']}: {info['status']}")
    
    # Example 1: Collect Ontario data (framework ready)
    print("\n3️⃣ Collecting Ontario data...")
    ontario_results = collector.collect_ontario_data("2024-01-01", "2024-12-31")
    print(f"   Status: {ontario_results['status']}")
    print(f"   Message: {ontario_results['message']}")
    
    # Example 2: Collect Canadian provinces data (framework ready)
    print("\n4️⃣ Collecting Canadian provinces data...")
    canada_results = collector.collect_canada_other_data()
    for province, result in canada_results.items():
        print(f"   • {result['name']}: {result['status']}")
    
    # Example 3: Collect US data (needs API key)
    print("\n5️⃣ Collecting US data...")
    us_results = collector.collect_us_data()  # No API key
    print(f"   Status: {us_results['status']}")
    print(f"   Message: {us_results['message']}")
    
    # Example 4: Collect European data (framework ready)
    print("\n6️⃣ Collecting European data...")
    europe_results = collector.collect_europe_data()
    for data_type, result in europe_results.items():
        print(f"   • {data_type}: {result['status']}")
    
    # Example 5: Collect all data at once
    print("\n7️⃣ Collecting all available data...")
    all_results = collector.collect_all_data()
    
    print(f"\n✅ Collection complete!")
    print(f"   Duration: {all_results['duration_seconds']:.2f} seconds")
    print(f"   Regions processed: {len(all_results['regions'])}")
    
    # Show detailed results for one region
    print(f"\n📊 Detailed results for Ontario:")
    ontario_detail = all_results['regions']['ontario']
    print(f"   Status: {ontario_detail['status']}")
    print(f"   Data types: {', '.join(ontario_detail['data_types'])}")
    
    print(f"\n💾 Results saved to: data/multi_region/processed/")
    
    # Example of how to use with real API keys
    print(f"\n🚀 To collect real US data, you would use:")
    print(f"   collector.collect_all_data(us_api_key='your_eia_api_key_here')")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Get EIA API key from: https://www.eia.gov/opendata/register.php")
    print(f"   2. Integrate with your existing Ontario IESO scripts")
    print(f"   3. Implement specific data collectors for each source")
    print(f"   4. Build comparison dashboards across regions")

if __name__ == "__main__":
    main()
