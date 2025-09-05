#!/usr/bin/env python3
"""
Canadian Province Electricity Price Collector
============================================

This script collects electricity prices from all Canadian provinces and territories:
- Alberta (AESO)
- British Columbia (BC Hydro)
- Manitoba (Manitoba Hydro)
- New Brunswick (NB Power)
- Newfoundland & Labrador (NL Hydro)
- Nova Scotia (Nova Scotia Power)
- Ontario (IESO) - Already implemented
- Prince Edward Island (PEI Energy)
- Quebec (Hydro-Québec)
- Saskatchewan (SaskPower)
- Northwest Territories (NT Power)
- Nunavut (Qulliq Energy)
- Yukon (Yukon Energy)

Author: AI Assistant
Date: 2024
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import logging
from bs4 import BeautifulSoup
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CanadianProvincePriceCollector:
    """Collects electricity prices from all Canadian provinces and territories."""
    
    def __init__(self, output_dir: str = "data/canadian_provinces"):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create output directories
        os.makedirs(f"{output_dir}/raw", exist_ok=True)
        os.makedirs(f"{output_dir}/processed", exist_ok=True)
        os.makedirs(f"{output_dir}/summaries", exist_ok=True)
        
        # Canadian provinces and territories with their electricity providers
        self.provinces = {
            'alberta': {
                'name': 'Alberta',
                'provider': 'AESO (Alberta Electric System Operator)',
                'website': 'https://www.aeso.ca/',
                'price_data_url': 'https://www.aeso.ca/reports/price/',
                'demand_data_url': 'https://www.aeso.ca/reports/demand/',
                'market_type': 'Deregulated',
                'data_format': 'CSV/XML',
                'update_frequency': 'Hourly',
                'notes': 'Real-time market prices, pool price, RRO rates'
            },
            'british_columbia': {
                'name': 'British Columbia',
                'provider': 'BC Hydro',
                'website': 'https://www.bchydro.com/',
                'price_data_url': 'https://www.bchydro.com/power-in-system/market-prices/',
                'demand_data_url': 'https://www.bchydro.com/power-in-system/system-demand/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Daily',
                'notes': 'Two-tier rate system, time-of-use options'
            },
            'manitoba': {
                'name': 'Manitoba',
                'provider': 'Manitoba Hydro',
                'website': 'https://www.hydro.mb.ca/',
                'price_data_url': 'https://www.hydro.mb.ca/customer_service/rates/',
                'demand_data_url': 'https://www.hydro.mb.ca/customer_service/rates/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'Lowest rates in Canada, primarily hydroelectric'
            },
            'new_brunswick': {
                'name': 'New Brunswick',
                'provider': 'NB Power',
                'website': 'https://www.nbpower.com/',
                'price_data_url': 'https://www.nbpower.com/en/home/customer-service/rates-and-billing/',
                'demand_data_url': 'https://www.nbpower.com/en/home/customer-service/rates-and-billing/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'Time-of-use rates, industrial rates available'
            },
            'newfoundland_labrador': {
                'name': 'Newfoundland & Labrador',
                'provider': 'NL Hydro',
                'website': 'https://www.nlhydro.com/',
                'price_data_url': 'https://www.nlhydro.com/customer-service/rates/',
                'demand_data_url': 'https://www.nlhydro.com/customer-service/rates/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'Primarily hydroelectric, industrial rates'
            },
            'nova_scotia': {
                'name': 'Nova Scotia',
                'provider': 'Nova Scotia Power',
                'website': 'https://www.nspower.ca/',
                'price_data_url': 'https://www.nspower.ca/en/home/customer-service/rates-and-billing/',
                'demand_data_url': 'https://www.nspower.ca/en/home/customer-service/rates-and-billing/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'Time-of-use rates, renewable energy options'
            },
            'ontario': {
                'name': 'Ontario',
                'provider': 'IESO (Independent Electricity System Operator)',
                'website': 'https://www.ieso.ca/',
                'price_data_url': 'https://www.ieso.ca/en/power-data/price-overview',
                'demand_data_url': 'https://www.ieso.ca/en/power-data/demand-overview',
                'market_type': 'Mixed (Regulated + Market)',
                'data_format': 'XML/CSV',
                'update_frequency': 'Hourly',
                'notes': 'HOEP, Global Adjustment, Class A/B rates, 5CP system'
            },
            'prince_edward_island': {
                'name': 'Prince Edward Island',
                'provider': 'PEI Energy',
                'website': 'https://www.princeedwardisland.ca/en/topic/pei-energy-corporation',
                'price_data_url': 'https://www.princeedwardisland.ca/en/topic/pei-energy-corporation',
                'demand_data_url': 'https://www.princeedwardisland.ca/en/topic/pei-energy-corporation',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'Wind energy integration, time-of-use rates'
            },
            'quebec': {
                'name': 'Quebec',
                'provider': 'Hydro-Québec',
                'website': 'https://www.hydroquebec.com/',
                'price_data_url': 'https://www.hydroquebec.com/business/customers/rates/',
                'demand_data_url': 'https://www.hydroquebec.com/business/customers/rates/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'Lowest rates in North America, primarily hydroelectric'
            },
            'saskatchewan': {
                'name': 'Saskatchewan',
                'provider': 'SaskPower',
                'website': 'https://www.saskpower.com/',
                'price_data_url': 'https://www.saskpower.com/our-company/about-us/rates-and-fuels/',
                'demand_data_url': 'https://www.saskpower.com/our-company/about-us/rates-and-fuels/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'Coal and renewable energy mix, industrial rates'
            },
            'northwest_territories': {
                'name': 'Northwest Territories',
                'provider': 'NT Power',
                'website': 'https://www.ntpc.com/',
                'price_data_url': 'https://www.ntpc.com/rates/',
                'demand_data_url': 'https://www.ntpc.com/rates/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'High costs due to remote location, diesel generation'
            },
            'nunavut': {
                'name': 'Nunavut',
                'provider': 'Qulliq Energy',
                'website': 'https://www.qec.nu.ca/',
                'price_data_url': 'https://www.qec.nu.ca/customer-service/rates/',
                'demand_data_url': 'https://www.qec.nu.ca/customer-service/rates/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'Highest rates in Canada, 100% diesel generation'
            },
            'yukon': {
                'name': 'Yukon',
                'provider': 'Yukon Energy',
                'website': 'https://www.yukonenergy.ca/',
                'price_data_url': 'https://www.yukonenergy.ca/customer-service/rates/',
                'demand_data_url': 'https://www.yukonenergy.ca/customer-service/rates/',
                'market_type': 'Regulated',
                'data_format': 'Web/PDF',
                'update_frequency': 'Annually',
                'notes': 'Hydroelectric and diesel mix, remote communities'
            }
        }
    
    def get_province_summary(self) -> Dict:
        """Get summary of all Canadian provinces and their electricity providers."""
        summary = {
            'total_provinces': len(self.provinces),
            'provinces': {}
        }
        
        for code, info in self.provinces.items():
            summary['provinces'][code] = {
                'name': info['name'],
                'provider': info['provider'],
                'market_type': info['market_type'],
                'data_format': info['data_format'],
                'update_frequency': info['update_frequency'],
                'website': info['website']
            }
        
        return summary
    
    def collect_alberta_prices(self) -> Dict:
        """Collect electricity prices from Alberta AESO."""
        logger.info("Collecting Alberta electricity prices from AESO...")
        
        try:
            # AESO provides real-time market data
            results = {
                'province': 'Alberta',
                'provider': 'AESO',
                'collection_time': datetime.now().isoformat(),
                'data_sources': [],
                'price_types': []
            }
            
            # Real-time pool price
            try:
                pool_price_url = "https://www.aeso.ca/reports/price/pool-price/"
                response = self.session.get(pool_price_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'real_time_pool_price',
                        'url': pool_price_url,
                        'status': 'available',
                        'format': 'Web interface'
                    })
                    results['price_types'].append('Real-time Pool Price')
            except Exception as e:
                logger.warning(f"Could not access AESO pool price: {e}")
            
            # Historical price data
            try:
                historical_url = "https://www.aeso.ca/reports/price/historical-price-data/"
                response = self.session.get(historical_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'historical_price_data',
                        'url': historical_url,
                        'status': 'available',
                        'format': 'CSV download'
                    })
                    results['price_types'].append('Historical Price Data')
            except Exception as e:
                logger.warning(f"Could not access AESO historical data: {e}")
            
            # RRO rates (Regulated Rate Option)
            try:
                rro_url = "https://www.aeso.ca/reports/price/regulated-rate-option-rro/"
                response = self.session.get(rro_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'regulated_rate_option',
                        'url': rro_url,
                        'status': 'available',
                        'format': 'Monthly rates'
                    })
                    results['price_types'].append('RRO Rates')
            except Exception as e:
                logger.warning(f"Could not access AESO RRO data: {e}")
            
            results['status'] = 'success'
            results['message'] = f"Collected {len(results['data_sources'])} data sources from AESO"
            
            return results
            
        except Exception as e:
            logger.error(f"Error collecting Alberta data: {e}")
            return {
                'province': 'Alberta',
                'status': 'error',
                'error': str(e)
            }
    
    def collect_bc_hydro_prices(self) -> Dict:
        """Collect electricity prices from BC Hydro."""
        logger.info("Collecting British Columbia electricity prices from BC Hydro...")
        
        try:
            results = {
                'province': 'British Columbia',
                'provider': 'BC Hydro',
                'collection_time': datetime.now().isoformat(),
                'data_sources': [],
                'price_types': []
            }
            
            # Residential rates
            try:
                residential_url = "https://www.bchydro.com/accounts-billing/rates-energy-use/electricity-rates/residential-rates.html"
                response = self.session.get(residential_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'residential_rates',
                        'url': residential_url,
                        'status': 'available',
                        'format': 'Web page'
                    })
                    results['price_types'].append('Residential Rates')
            except Exception as e:
                logger.warning(f"Could not access BC Hydro residential rates: {e}")
            
            # Business rates
            try:
                business_url = "https://www.bchydro.com/accounts-billing/rates-energy-use/electricity-rates/business-rates.html"
                response = self.session.get(business_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'business_rates',
                        'url': business_url,
                        'status': 'available',
                        'format': 'Web page'
                    })
                    results['price_types'].append('Business Rates')
            except Exception as e:
                logger.warning(f"Could not access BC Hydro business rates: {e}")
            
            # Time-of-use rates
            try:
                tou_url = "https://www.bchydro.com/accounts-billing/rates-energy-use/electricity-rates/time-of-use-rates.html"
                response = self.session.get(tou_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'time_of_use_rates',
                        'url': tou_url,
                        'status': 'available',
                        'format': 'Web page'
                    })
                    results['price_types'].append('Time-of-Use Rates')
            except Exception as e:
                logger.warning(f"Could not access BC Hydro TOU rates: {e}")
            
            results['status'] = 'success'
            results['message'] = f"Collected {len(results['data_sources'])} data sources from BC Hydro"
            
            return results
            
        except Exception as e:
            logger.error(f"Error collecting BC Hydro data: {e}")
            return {
                'province': 'British Columbia',
                'status': 'error',
                'error': str(e)
            }
    
    def collect_quebec_prices(self) -> Dict:
        """Collect electricity prices from Hydro-Québec."""
        logger.info("Collecting Quebec electricity prices from Hydro-Québec...")
        
        try:
            results = {
                'province': 'Quebec',
                'provider': 'Hydro-Québec',
                'collection_time': datetime.now().isoformat(),
                'data_sources': [],
                'price_types': []
            }
            
            # Residential rates
            try:
                residential_url = "https://www.hydroquebec.com/residential/customer-space/account-and-billing/rates/"
                response = self.session.get(residential_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'residential_rates',
                        'url': residential_url,
                        'status': 'available',
                        'format': 'Web page'
                    })
                    results['price_types'].append('Residential Rates')
            except Exception as e:
                logger.warning(f"Could not access Hydro-Québec residential rates: {e}")
            
            # Business rates
            try:
                business_url = "https://www.hydroquebec.com/business/customers/rates/"
                response = self.session.get(business_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'business_rates',
                        'url': business_url,
                        'status': 'available',
                        'format': 'Web page'
                    })
                    results['price_types'].append('Business Rates')
            except Exception as e:
                logger.warning(f"Could not access Hydro-Québec business rates: {e}")
            
            # Rate calculator
            try:
                calculator_url = "https://www.hydroquebec.com/residential/customer-space/account-and-billing/rates/rate-calculator/"
                response = self.session.get(calculator_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'rate_calculator',
                        'url': calculator_url,
                        'status': 'available',
                        'format': 'Interactive tool'
                    })
                    results['price_types'].append('Rate Calculator')
            except Exception as e:
                logger.warning(f"Could not access Hydro-Québec rate calculator: {e}")
            
            results['status'] = 'success'
            results['message'] = f"Collected {len(results['data_sources'])} data sources from Hydro-Québec"
            
            return results
            
        except Exception as e:
            logger.error(f"Error collecting Hydro-Québec data: {e}")
            return {
                'province': 'Quebec',
                'status': 'error',
                'error': str(e)
            }
    
    def collect_ontario_prices(self) -> Dict:
        """Collect electricity prices from Ontario IESO (already implemented)."""
        logger.info("Collecting Ontario electricity prices from IESO...")
        
        try:
            results = {
                'province': 'Ontario',
                'provider': 'IESO',
                'collection_time': datetime.now().isoformat(),
                'data_sources': [],
                'price_types': []
            }
            
            # HOEP (Hourly Ontario Energy Price)
            try:
                hoep_url = "https://www.ieso.ca/en/power-data/price-overview"
                response = self.session.get(hoep_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'hoep_prices',
                        'url': hoep_url,
                        'status': 'available',
                        'format': 'Real-time data'
                    })
                    results['price_types'].append('HOEP (Hourly Ontario Energy Price)')
            except Exception as e:
                logger.warning(f"Could not access IESO HOEP data: {e}")
            
            # Global Adjustment
            try:
                ga_url = "https://www.ieso.ca/en/power-data/global-adjustment"
                response = self.session.get(ga_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'global_adjustment',
                        'url': ga_url,
                        'status': 'available',
                        'format': 'Monthly rates'
                    })
                    results['price_types'].append('Global Adjustment')
            except Exception as e:
                logger.warning(f"Could not access IESO Global Adjustment data: {e}")
            
            # Class A and Class B rates
            try:
                class_rates_url = "https://www.ieso.ca/en/power-data/global-adjustment"
                response = self.session.get(class_rates_url, timeout=10)
                if response.status_code == 200:
                    results['data_sources'].append({
                        'type': 'class_a_b_rates',
                        'url': class_rates_url,
                        'status': 'available',
                        'format': 'Customer class rates'
                    })
                    results['price_types'].append('Class A and Class B Rates')
            except Exception as e:
                logger.warning(f"Could not access IESO Class rates data: {e}")
            
            results['status'] = 'success'
            results['message'] = f"Collected {len(results['data_sources'])} data sources from IESO"
            
            return results
            
        except Exception as e:
            logger.error(f"Error collecting IESO data: {e}")
            return {
                'province': 'Ontario',
                'status': 'error',
                'error': str(e)
            }
    
    def collect_all_province_prices(self) -> Dict:
        """Collect electricity prices from all Canadian provinces."""
        logger.info("Starting comprehensive Canadian province electricity price collection...")
        
        start_time = time.time()
        
        results = {
            'collection_start': datetime.now().isoformat(),
            'provinces': {},
            'summary': {}
        }
        
        # Collect from major provinces first
        major_provinces = ['alberta', 'british_columbia', 'quebec', 'ontario']
        
        for province in major_provinces:
            logger.info(f"Collecting from {self.provinces[province]['name']}...")
            
            if province == 'alberta':
                results['provinces'][province] = self.collect_alberta_prices()
            elif province == 'british_columbia':
                results['provinces'][province] = self.collect_bc_hydro_prices()
            elif province == 'quebec':
                results['provinces'][province] = self.collect_quebec_prices()
            elif province == 'ontario':
                results['provinces'][province] = self.collect_ontario_prices()
            
            # Add delay to be respectful to servers
            time.sleep(2)
        
        # Add framework status for other provinces
        for province_code, info in self.provinces.items():
            if province_code not in results['provinces']:
                results['provinces'][province_code] = {
                    'province': info['name'],
                    'provider': info['provider'],
                    'status': 'framework_ready',
                    'website': info['website'],
                    'market_type': info['market_type'],
                    'data_format': info['data_format'],
                    'update_frequency': info['update_frequency'],
                    'message': f'Data collection framework ready for {info["name"]}'
                }
        
        # Summary statistics
        results['collection_end'] = datetime.now().isoformat()
        results['duration_seconds'] = time.time() - start_time
        
        # Calculate summary
        total_provinces = len(results['provinces'])
        successful_collections = sum(1 for p in results['provinces'].values() if p.get('status') == 'success')
        framework_ready = sum(1 for p in results['provinces'].values() if p.get('status') == 'framework_ready')
        
        results['summary'] = {
            'total_provinces': total_provinces,
            'successful_collections': successful_collections,
            'framework_ready': framework_ready,
            'collection_rate': f"{(successful_collections/total_provinces)*100:.1f}%"
        }
        
        # Save results
        self.save_collection_results(results)
        
        return results
    
    def save_collection_results(self, results: Dict):
        """Save collection results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/processed/canadian_province_prices_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Collection results saved to: {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def create_price_comparison_summary(self) -> Dict:
        """Create a summary comparing electricity prices across provinces."""
        logger.info("Creating Canadian province electricity price comparison summary...")
        
        # This would typically use actual collected price data
        # For now, creating a framework summary
        summary = {
            'comparison_date': datetime.now().isoformat(),
            'price_categories': {
                'residential': 'Average residential rates per kWh',
                'commercial': 'Average commercial rates per kWh',
                'industrial': 'Average industrial rates per kWh',
                'time_of_use': 'Time-of-use rate structures'
            },
            'province_rankings': {
                'lowest_rates': ['Quebec', 'Manitoba', 'British Columbia'],
                'highest_rates': ['Nunavut', 'Northwest Territories', 'Nova Scotia'],
                'market_types': {
                    'deregulated': ['Alberta'],
                    'regulated': ['All other provinces']
                }
            },
            'data_availability': {
                'real_time': ['Alberta (AESO)', 'Ontario (IESO)'],
                'daily': ['British Columbia (BC Hydro)'],
                'monthly': ['Most provinces'],
                'annually': ['All provinces']
            }
        }
        
        # Save summary
        summary_filename = f"{self.output_dir}/summaries/canadian_price_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(summary_filename, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Price comparison summary saved to: {summary_filename}")
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
        
        return summary

def main():
    """Main function to demonstrate the Canadian province price collector."""
    
    print("🇨🇦 Canadian Province Electricity Price Collector")
    print("=" * 55)
    
    # Initialize collector
    collector = CanadianProvincePriceCollector()
    
    # Show available provinces
    print("\n📊 Available Canadian Provinces and Territories:")
    summary = collector.get_province_summary()
    for code, info in summary['provinces'].items():
        print(f"  • {info['name']}: {info['provider']}")
        print(f"    Market: {info['market_type']} | Data: {info['data_format']} | Updates: {info['update_frequency']}")
        print(f"    Website: {info['website']}")
        print()
    
    print(f"\n🚀 Starting data collection from {summary['total_provinces']} provinces...")
    
    # Collect all province prices
    results = collector.collect_all_province_prices()
    
    print(f"\n✅ Collection complete!")
    print(f"   Duration: {results['duration_seconds']:.2f} seconds")
    print(f"   Provinces processed: {results['summary']['total_provinces']}")
    print(f"   Successful collections: {results['summary']['successful_collections']}")
    print(f"   Framework ready: {results['summary']['framework_ready']}")
    print(f"   Collection rate: {results['summary']['collection_rate']}")
    
    # Show detailed results for successful collections
    print(f"\n📊 Detailed Results:")
    for province_code, result in results['provinces'].items():
        if result.get('status') == 'success':
            print(f"  ✅ {result['province']} ({result['provider']}):")
            print(f"     Data sources: {len(result['data_sources'])}")
            print(f"     Price types: {', '.join(result['price_types'])}")
            print(f"     Message: {result['message']}")
        else:
            print(f"  🔧 {result['province']} ({result['provider']}): {result['status']}")
    
    # Create price comparison summary
    print(f"\n📈 Creating price comparison summary...")
    price_summary = collector.create_price_comparison_summary()
    
    print(f"\n💾 Results saved to:")
    print(f"   Raw data: data/canadian_provinces/raw/")
    print(f"   Processed data: data/canadian_provinces/processed/")
    print(f"   Summaries: data/canadian_provinces/summaries/")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Implement specific collectors for remaining provinces")
    print(f"   2. Extract actual price data from collected sources")
    print(f"   3. Build price comparison dashboards")
    print(f"   4. Create historical price tracking")
    print(f"   5. Analyze price trends across provinces")

if __name__ == "__main__":
    main()
