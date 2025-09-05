#!/usr/bin/env python3
"""
Enhanced Real-Time Canadian Province Electricity Price Collector
==============================================================

This version has IMPROVED extraction patterns to actually get REAL rates
instead of just framework working.

Author: AI Assistant
Date: 2024
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Tuple
import logging
from bs4 import BeautifulSoup
import re
import urllib3

# Disable SSL warnings for some websites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedRealTimeCanadianPriceCollector:
    """Enhanced collector with BETTER extraction patterns for REAL rates."""
    
    def __init__(self, output_dir: str = "data/enhanced_real_time"):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create output directories
        os.makedirs(f"{output_dir}/raw", exist_ok=True)
        os.makedirs(f"{output_dir}/processed", exist_ok=True)
        os.makedirs(f"{output_dir}/summaries", exist_ok=True)
        
    def extract_rate_with_multiple_patterns(self, soup: BeautifulSoup, patterns: List[str]) -> Optional[str]:
        """Try multiple extraction patterns to get the actual rate."""
        for pattern in patterns:
            try:
                if pattern.startswith('.'):
                    # CSS selector
                    element = soup.select_one(pattern)
                    if element and element.text.strip():
                        rate_text = element.text.strip()
                        if self.is_valid_rate(rate_text):
                            return rate_text
                elif pattern.startswith('#'):
                    # ID selector
                    element = soup.find(id=pattern[1:])
                    if element and element.text.strip():
                        rate_text = element.text.strip()
                        if self.is_valid_rate(rate_text):
                            return rate_text
                else:
                    # Text pattern
                    elements = soup.find_all(string=re.compile(pattern, re.IGNORECASE))
                    for element in elements:
                        if self.is_valid_rate(element):
                            return element.strip()
            except Exception as e:
                logger.debug(f"Pattern {pattern} failed: {e}")
                continue
        return None
    
    def is_valid_rate(self, text: str) -> bool:
        """Check if extracted text looks like a valid rate."""
        if not text:
            return False
        
        # Look for common rate patterns
        rate_patterns = [
            r'\$\d+\.?\d*',  # $0.094, $45.23
            r'\d+\.?\d*\s*¢',  # 9.4¢
            r'\d+\.?\d*\s*cents',  # 9.4 cents
            r'\d+\.?\d*\s*per\s*kWh',  # 9.4 per kWh
            r'\d+\.?\d*\s*per\s*kW',  # 25 per kW
        ]
        
        for pattern in rate_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def collect_alberta_enhanced(self) -> Dict:
        """Enhanced Alberta collection with BETTER extraction patterns."""
        logger.info("Collecting ENHANCED Alberta electricity prices from AESO...")
        
        try:
            results = {
                'province': 'Alberta',
                'provider': 'AESO',
                'collection_time': datetime.now().isoformat(),
                'data_sources': [],
                'real_time_rates': {},
                'status': 'success'
            }
            
            # 1. Real-time pool price - try multiple extraction methods
            try:
                pool_price_url = "https://www.aeso.ca/reports/price/pool-price/"
                response = self.session.get(pool_price_url, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Multiple extraction patterns for pool price
                    pool_patterns = [
                        r'\$\d+\.?\d*',  # Basic dollar pattern
                        r'Pool Price.*?\$\d+\.?\d*',  # Pool Price: $45.23
                        r'Current.*?\$\d+\.?\d*',  # Current: $45.23
                        r'\$\d+\.?\d*\s*per\s*MWh',  # $45.23 per MWh
                    ]
                    
                    current_price = self.extract_rate_with_multiple_patterns(soup, pool_patterns)
                    if current_price:
                        results['real_time_rates']['current_pool_price'] = current_price
                        logger.info(f"✅ Alberta current pool price: {current_price}")
                    
                    results['data_sources'].append({
                        'type': 'real_time_pool_price',
                        'url': pool_price_url,
                        'status': 'success',
                        'data_extracted': bool(results['real_time_rates'].get('current_pool_price'))
                    })
                    
            except Exception as e:
                logger.warning(f"Could not extract AESO pool price: {e}")
            
            # 2. RRO rates with enhanced extraction
            try:
                rro_url = "https://www.aeso.ca/reports/price/regulated-rate-option-rro/"
                response = self.session.get(rro_url, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Enhanced RRO extraction patterns
                    rro_patterns = [
                        r'RRO.*?\$\d+\.?\d*',  # RRO Rate: $0.089
                        r'Regulated.*?\$\d+\.?\d*',  # Regulated: $0.089
                        r'\$\d+\.?\d*\s*per\s*kWh',  # $0.089 per kWh
                        r'\$\d+\.?\d*',  # Basic dollar pattern
                    ]
                    
                    current_rro = self.extract_rate_with_multiple_patterns(soup, rro_patterns)
                    if current_rro:
                        results['real_time_rates']['current_rro_rate'] = current_rro
                        logger.info(f"✅ Alberta RRO rate: {current_rro}")
                    
                    results['data_sources'].append({
                        'type': 'regulated_rate_option',
                        'url': rro_url,
                        'status': 'success',
                        'data_extracted': bool(results['real_time_rates'].get('current_rro_rate'))
                    })
                    
            except Exception as e:
                logger.warning(f"Could not extract AESO RRO data: {e}")
            
            results['message'] = f"Collected {len([s for s in results['data_sources'] if s['data_extracted']])} real-time data sources from AESO"
            return results
            
        except Exception as e:
            logger.error(f"Error collecting Alberta real-time data: {e}")
            return {
                'province': 'Alberta',
                'status': 'error',
                'error': str(e)
            }
    
    def collect_bc_hydro_enhanced(self) -> Dict:
        """Enhanced BC Hydro collection with BETTER extraction patterns."""
        logger.info("Collecting ENHANCED British Columbia electricity prices from BC Hydro...")
        
        try:
            results = {
                'province': 'British Columbia',
                'provider': 'BC Hydro',
                'collection_time': datetime.now().isoformat(),
                'data_sources': [],
                'real_time_rates': {},
                'status': 'success'
            }
            
            # 1. Residential rates with enhanced extraction
            try:
                residential_url = "https://www.bchydro.com/accounts-billing/rates-energy-use/electricity-rates/residential-rates.html"
                response = self.session.get(residential_url, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Enhanced residential rate extraction patterns
                    residential_patterns = [
                        r'\$\d+\.?\d*\s*per\s*kWh',  # $0.094 per kWh
                        r'Residential.*?\$\d+\.?\d*',  # Residential: $0.094
                        r'Rate.*?\$\d+\.?\d*',  # Rate: $0.094
                        r'\$\d+\.?\d*',  # Basic dollar pattern
                        r'\d+\.?\d*\s*¢',  # 9.4¢
                    ]
                    
                    residential_rate = self.extract_rate_with_multiple_patterns(soup, residential_patterns)
                    if residential_rate:
                        results['real_time_rates']['residential_rate'] = residential_rate
                        logger.info(f"✅ BC Hydro residential rate: {residential_rate}")
                    
                    results['data_sources'].append({
                        'type': 'residential_rates',
                        'url': residential_url,
                        'status': 'success',
                        'data_extracted': bool(results['real_time_rates'].get('residential_rate'))
                    })
                    
            except Exception as e:
                logger.warning(f"Could not extract BC Hydro residential rates: {e}")
            
            # 2. Business rates with enhanced extraction
            try:
                business_url = "https://www.bchydro.com/accounts-billing/rates-energy-use/electricity-rates/business-rates.html"
                response = self.session.get(business_url, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Enhanced business rate extraction patterns
                    business_patterns = [
                        r'\$\d+\.?\d*\s*per\s*kWh',  # $0.094 per kWh
                        r'Business.*?\$\d+\.?\d*',  # Business: $0.094
                        r'Rate.*?\$\d+\.?\d*',  # Rate: $0.094
                        r'\$\d+\.?\d*',  # Basic dollar pattern
                        r'\d+\.?\d*\s*¢',  # 9.4¢
                    ]
                    
                    business_rate = self.extract_rate_with_multiple_patterns(soup, business_patterns)
                    if business_rate:
                        results['real_time_rates']['business_rate'] = business_rate
                        logger.info(f"✅ BC Hydro business rate: {business_rate}")
                    
                    results['data_sources'].append({
                        'type': 'business_rates',
                        'url': business_url,
                        'status': 'success',
                        'data_extracted': bool(results['real_time_rates'].get('business_rate'))
                    })
                    
            except Exception as e:
                logger.warning(f"Could not extract BC Hydro business rates: {e}")
            
            results['message'] = f"Collected {len([s for s in results['data_sources'] if s['data_extracted']])} real-time data sources from BC Hydro"
            return results
            
        except Exception as e:
            logger.error(f"Error collecting BC Hydro real-time data: {e}")
            return {
                'province': 'British Columbia',
                'status': 'error',
                'error': str(e)
            }
    
    def collect_ontario_enhanced(self) -> Dict:
        """Enhanced Ontario collection with BETTER extraction patterns."""
        logger.info("Collecting ENHANCED Ontario electricity prices from IESO...")
        
        try:
            results = {
                'province': 'Ontario',
                'provider': 'IESO',
                'collection_time': datetime.now().isoformat(),
                'data_sources': [],
                'real_time_rates': {},
                'status': 'success'
            }
            
            # 1. HOEP with enhanced extraction
            try:
                hoep_url = "https://www.ieso.ca/en/power-data/price-overview"
                response = self.session.get(hoep_url, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Enhanced HOEP extraction patterns
                    hoep_patterns = [
                        r'HOEP.*?\$\d+\.?\d*',  # HOEP: $0.128
                        r'Price.*?\$\d+\.?\d*',  # Price: $0.128
                        r'Current.*?\$\d+\.?\d*',  # Current: $0.128
                        r'\$\d+\.?\d*\s*per\s*MWh',  # $0.128 per MWh
                        r'\$\d+\.?\d*',  # Basic dollar pattern
                    ]
                    
                    current_hoep = self.extract_rate_with_multiple_patterns(soup, hoep_patterns)
                    if current_hoep:
                        results['real_time_rates']['current_hoep'] = current_hoep
                        logger.info(f"✅ Ontario current HOEP: {current_hoep}")
                    
                    results['data_sources'].append({
                        'type': 'hoep_prices',
                        'url': hoep_url,
                        'status': 'success',
                        'data_extracted': bool(results['real_time_rates'].get('current_hoep'))
                    })
                    
            except Exception as e:
                logger.warning(f"Could not extract IESO HOEP data: {e}")
            
            # 2. Global Adjustment with enhanced extraction
            try:
                ga_url = "https://www.ieso.ca/en/power-data/global-adjustment"
                response = self.session.get(ga_url, timeout=15, verify=False)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Enhanced Global Adjustment extraction patterns
                    ga_patterns = [
                        r'Global.*?Adjustment.*?\$\d+\.?\d*',  # Global Adjustment: $0.089
                        r'GA.*?\$\d+\.?\d*',  # GA: $0.089
                        r'Rate.*?\$\d+\.?\d*',  # Rate: $0.089
                        r'\$\d+\.?\d*\s*per\s*kWh',  # $0.089 per kWh
                        r'\$\d+\.?\d*',  # Basic dollar pattern
                    ]
                    
                    current_ga = self.extract_rate_with_multiple_patterns(soup, ga_patterns)
                    if current_ga:
                        results['real_time_rates']['current_global_adjustment'] = current_ga
                        logger.info(f"✅ Ontario Global Adjustment: {current_ga}")
                    
                    results['data_sources'].append({
                        'type': 'global_adjustment',
                        'url': ga_url,
                        'status': 'success',
                        'data_extracted': bool(results['real_time_rates'].get('current_global_adjustment'))
                    })
                    
            except Exception as e:
                logger.warning(f"Could not extract IESO Global Adjustment data: {e}")
            
            results['message'] = f"Collected {len([s for s in results['data_sources'] if s['data_extracted']])} real-time data sources from IESO"
            return results
            
        except Exception as e:
            logger.error(f"Error collecting IESO real-time data: {e}")
            return {
                'province': 'Ontario',
                'status': 'error',
                'error': str(e)
            }
    
    def collect_all_provinces_enhanced(self) -> Dict:
        """Collect REAL-TIME electricity prices with ENHANCED extraction."""
        logger.info("Starting ENHANCED REAL-TIME Canadian province electricity price collection...")
        
        start_time = time.time()
        
        results = {
            'collection_start': datetime.now().isoformat(),
            'provinces': {},
            'summary': {},
            'real_time_data_available': []
        }
        
        # Collect from major provinces with ENHANCED extraction
        major_provinces = [
            ('alberta', self.collect_alberta_enhanced),
            ('british_columbia', self.collect_bc_hydro_enhanced),
            ('ontario', self.collect_ontario_enhanced),
        ]
        
        for province_code, collector_func in major_provinces:
            logger.info(f"Collecting ENHANCED data from {province_code}...")
            
            try:
                province_result = collector_func()
                results['provinces'][province_code] = province_result
                
                # Check if we got real-time data
                if province_result.get('status') == 'success' and province_result.get('real_time_rates'):
                    results['real_time_data_available'].append({
                        'province': province_result['province'],
                        'data_points': len(province_result['real_time_rates']),
                        'rates': province_result['real_time_rates']
                    })
                
                # Add delay to be respectful to servers
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"Error collecting from {province_code}: {e}")
                results['provinces'][province_code] = {
                    'province': province_code.title(),
                    'status': 'error',
                    'error': str(e)
                }
        
        # Summary statistics
        results['collection_end'] = datetime.now().isoformat()
        results['duration_seconds'] = time.time() - start_time
        
        # Calculate summary
        total_provinces = len(results['provinces'])
        successful_collections = sum(1 for p in results['provinces'].values() if p.get('status') == 'success')
        real_time_data_count = len(results['real_time_data_available'])
        
        results['summary'] = {
            'total_provinces': total_provinces,
            'successful_collections': successful_collections,
            'real_time_data_collected': real_time_data_count,
            'collection_rate': f"{(successful_collections/total_provinces)*100:.1f}%",
            'real_time_data_rate': f"{(real_time_data_count/total_provinces)*100:.1f}%"
        }
        
        # Save results
        self.save_enhanced_results(results)
        
        return results
    
    def save_enhanced_results(self, results: Dict):
        """Save enhanced collection results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/processed/enhanced_real_time_canadian_prices_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Enhanced collection results saved to: {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

def main():
    """Main function to demonstrate ENHANCED real-time Canadian province price collection."""
    
    print("🇨🇦 ENHANCED REAL-TIME Canadian Province Electricity Price Collector")
    print("=" * 70)
    print("This version has IMPROVED extraction patterns to get REAL rates!")
    print()
    
    # Initialize enhanced collector
    collector = EnhancedRealTimeCanadianPriceCollector()
    
    print("🚀 Starting ENHANCED REAL-TIME data collection from Canadian provinces...")
    print("   Using improved extraction patterns for better rate detection...")
    print()
    
    # Collect all province prices with ENHANCED extraction
    results = collector.collect_all_provinces_enhanced()
    
    print(f"\n✅ ENHANCED REAL-TIME Collection complete!")
    print(f"   Duration: {results['duration_seconds']:.2f} seconds")
    print(f"   Provinces processed: {results['summary']['total_provinces']}")
    print(f"   Successful collections: {results['summary']['successful_collections']}")
    print(f"   Real-time data collected: {results['summary']['real_time_data_collected']}")
    print(f"   Collection rate: {results['summary']['collection_rate']}")
    print(f"   Real-time data rate: {results['summary']['real_time_data_rate']}")
    
    # Show real-time data collected
    if results['real_time_data_available']:
        print(f"\n📊 ENHANCED REAL-TIME Data Collected:")
        for data in results['real_time_data_available']:
            print(f"  ✅ {data['province']}: {data['data_points']} data points")
            for rate_type, rate_value in data['rates'].items():
                print(f"     • {rate_type}: {rate_value}")
    else:
        print(f"\n⚠️  No real-time data was extracted. This may indicate:")
        print(f"   • Website structure changes")
        print(f"   • Anti-scraping measures")
        print(f"   • Need for Selenium (JavaScript-rendered content)")
    
    # Show detailed results
    print(f"\n📊 Detailed Results:")
    for province_code, result in results['provinces'].items():
        if result.get('status') == 'success':
            print(f"  ✅ {result['province']} ({result['provider']}):")
            print(f"     Data sources: {len(result['data_sources'])}")
            if result.get('real_time_rates'):
                print(f"     Real-time rates: {len(result['real_time_rates'])}")
                for rate_type, rate_value in result['real_time_rates'].items():
                    print(f"       • {rate_type}: {rate_value}")
            print(f"     Message: {result['message']}")
        else:
            print(f"  ❌ {result.get('province', province_code)}: {result.get('status', 'unknown')}")
    
    print(f"\n💾 Results saved to:")
    print(f"   Raw data: {collector.output_dir}/raw/")
    print(f"   Processed data: {collector.output_dir}/processed/")
    print(f"   Summaries: {collector.output_dir}/summaries/")
    
    print(f"\n🚀 Next steps for ENHANCED real-time data:")
    print(f"   1. Review extracted rates and validate accuracy")
    print(f"   2. If still limited, implement Selenium for JavaScript sites")
    print(f"   3. Set up automated collection (every hour for real-time provinces)")
    print(f"   4. Build real-time dashboard with live data feeds")
    print(f"   5. Implement rate change alerts and notifications")

if __name__ == "__main__":
    main()
