# 🇨🇦 Real-Time Canadian Electricity Price Collector

## 🚀 **What This System Does**

This system collects **REAL-TIME electricity prices** from actual Canadian province websites instead of using estimated data. It:

- **Visits real websites** like AESO, BC Hydro, IESO, Hydro-Québec
- **Extracts current rates** using web scraping and API calls
- **Updates hourly** for real-time provinces (Alberta, Ontario)
- **Updates daily** for other provinces
- **Provides live dashboard** with current rates

## 📊 **Real-Time Data Sources**

### **⚡ Hourly Updates (Most Real-Time)**
- **Alberta (AESO)**: Pool price, RRO rates, historical data
- **Ontario (IESO)**: HOEP, Global Adjustment, Class A/B rates

### **📅 Daily Updates**
- **British Columbia (BC Hydro)**: Residential, business, time-of-use rates
- **Quebec (Hydro-Québec)**: Residential, business rates, calculator

### **📊 Regular Updates**
- **Manitoba Hydro**: Current rates
- **SaskPower**: Current rates
- **Other provinces**: Framework ready for implementation

## 🛠️ **Installation & Setup**

### **1. Install Dependencies**
```bash
pip install -r requirements_real_time.txt
```

### **2. Run Real-Time Collection**
```bash
python real_time_canadian_price_collector.py
```

### **3. View Real-Time Dashboard**
Open `real_time_canadian_dashboard.html` in your browser

## 🔄 **How Real-Time Collection Works**

### **Step 1: Website Access**
```python
# Example: Collecting from Alberta AESO
response = session.get("https://www.aeso.ca/reports/price/pool-price/")
soup = BeautifulSoup(response.content, 'html.parser')
```

### **Step 2: Data Extraction**
```python
# Extract current pool price using regex
price_elements = soup.find_all(text=re.compile(r'\$\d+\.?\d*'))
current_price = price_elements[0].strip()  # e.g., "$45.23"
```

### **Step 3: Data Validation**
```python
# Validate extracted data
if current_price and current_price.startswith('$'):
    results['real_time_rates']['current_pool_price'] = current_price
    logger.info(f"Alberta current pool price: {current_price}")
```

### **Step 4: Storage & Dashboard**
- Data saved to JSON files with timestamps
- Dashboard reads files and displays live data
- Real-time indicators show data freshness

## 📈 **Real-Time Dashboard Features**

### **Live Data Indicators**
- **🟢 LIVE DATA**: Pulsing indicator showing real-time status
- **Data Collection Status**: Shows success/failure for each province
- **Last Updated**: Timestamp of most recent data collection

### **Real-Time Charts**
- **Residential Rates**: Current residential electricity prices
- **Business Rates**: Current business electricity prices
- **Pool Prices**: Real-time market prices (Alberta)
- **HOEP**: Hourly Ontario Energy Price

### **Live Data Table**
- **Province**: Which province the data is from
- **Provider**: Electricity company (AESO, BC Hydro, etc.)
- **Status**: Collection success/failure
- **Data Points**: Number of rates collected
- **Latest Rates**: Actual current rates (not estimates)
- **Last Updated**: When data was collected

## 🔧 **Customization & Extension**

### **Add New Provinces**
```python
def collect_new_province_real_time(self) -> Dict:
    """Collect REAL-TIME electricity prices from new province."""
    try:
        results = {
            'province': 'New Province',
            'provider': 'Provider Name',
            'collection_time': datetime.now().isoformat(),
            'data_sources': [],
            'real_time_rates': {},
            'status': 'success'
        }
        
        # Add your collection logic here
        url = "https://province-website.com/rates"
        response = self.session.get(url, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract rates using your logic
            
        return results
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
```

### **Modify Data Sources**
```python
# In the main collection function
major_provinces = [
    ('alberta', self.collect_alberta_real_time),
    ('british_columbia', self.collect_bc_hydro_real_time),
    ('quebec', self.collect_quebec_real_time),
    ('ontario', self.collect_ontario_real_time),
    ('manitoba', self.collect_manitoba_real_time),
    ('saskatchewan', self.collect_saskatchewan_real_time),
    ('new_province', self.collect_new_province_real_time)  # Add here
]
```

## ⚠️ **Important Notes**

### **Rate Limiting**
- **3-second delays** between province requests
- **Respectful scraping** to avoid overwhelming servers
- **User-Agent headers** to identify your requests

### **Data Accuracy**
- **Real-time data** may change frequently
- **Website structure** changes can break scrapers
- **Validate data** before using for business decisions

### **Legal Considerations**
- **Check terms of service** for each website
- **Respect robots.txt** files
- **Don't overload** servers with requests

## 🚀 **Next Steps for Production**

### **1. Automated Collection**
```python
# Set up cron job or scheduler
# Run every hour for real-time provinces
# Run daily for other provinces
```

### **2. Database Integration**
```python
# Store data in PostgreSQL/MySQL
# Track historical rate changes
# Enable trend analysis
```

### **3. API Development**
```python
# Create REST API for data access
# Enable real-time notifications
# Support multiple clients
```

### **4. Monitoring & Alerts**
```python
# Monitor collection success rates
# Alert on data collection failures
# Track website structure changes
```

## 📊 **Sample Real-Time Data Output**

```json
{
  "collection_start": "2024-09-01T16:00:00",
  "provinces": {
    "alberta": {
      "province": "Alberta",
      "provider": "AESO",
      "status": "success",
      "real_time_rates": {
        "current_pool_price": "$45.23",
        "current_rro_rate": "$0.089",
        "recent_prices": ["$45.23", "$42.15", "$48.76"]
      },
      "collection_time": "2024-09-01T16:00:00"
    }
  },
  "summary": {
    "total_provinces": 6,
    "successful_collections": 6,
    "real_time_data_collected": 18,
    "collection_rate": "100.0%"
  }
}
```

## 🎯 **Business Applications**

### **Energy Trading**
- **Real-time pricing** for market decisions
- **Hourly updates** for Alberta pool prices
- **Live HOEP** for Ontario market analysis

### **Cost Optimization**
- **Current rates** across provinces
- **Rate comparison** for business planning
- **Trend analysis** for forecasting

### **Regulatory Compliance**
- **Live rate monitoring** for compliance
- **Historical tracking** for audits
- **Real-time alerts** for rate changes

## 🔍 **Troubleshooting**

### **Common Issues**

#### **SSL Errors**
```python
# Disable SSL verification for some websites
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
response = session.get(url, verify=False)
```

#### **Website Structure Changes**
```python
# Add multiple extraction methods
try:
    # Method 1: Direct text search
    price = soup.find(text=re.compile(r'\$\d+\.?\d*'))
except:
    try:
        # Method 2: CSS selector
        price = soup.select_one('.price-value').text
    except:
        # Method 3: Fallback
        price = "Data not available"
```

#### **Rate Limiting**
```python
# Add delays between requests
import time
time.sleep(3)  # 3-second delay
```

## 📞 **Support & Updates**

### **Keep Updated**
- **Monitor website changes** regularly
- **Update extraction patterns** as needed
- **Test collection** weekly

### **Community**
- **Share improvements** with other users
- **Report issues** for fixes
- **Contribute** new province collectors

---

**Ready to collect REAL-TIME Canadian electricity prices?** 🇨🇦⚡

This system gives you **actual current rates** instead of estimates, enabling real-time decision making and accurate cost analysis!
