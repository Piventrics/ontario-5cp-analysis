# Ontario 5CP Analysis - Project Structure

## 🗂️ Organized Folder Structure

Your project has been reorganized into a clean, professional structure:

### 📊 **dashboards/** (5 files)
- `5cp_forecasting_dashboard.html` - Main 5CP forecasting dashboard
- `battery_savings_dashboard.html` - Class A vs Class B comparison
- `ga_calculator_standalone.html` - Standalone GA calculator
- `index.html` - Project index page
- `test_dashboard.html` - Testing dashboard

### 🔧 **data_scripts/** (24 files)
- **Download scripts**: `download_*.py` - IESO data collection
- **Parse scripts**: `parse_*.py` - Data processing and extraction
- **Analysis scripts**: `analyze_*.py` - Data analysis and insights
- **Creation scripts**: `create_*.py` - Map and visualization generation
- **Jupyter notebooks**: `*.ipynb` - Interactive data exploration

### 📈 **analysis_scripts/** (4 files)
- `5cp_forecasting_model.py` - ML forecasting pipeline
- `run_forecasting.py` - Forecasting execution script
- `simple_5cp_statistics.py` - Basic 5CP statistics
- `visualize_5cp.py` - 5CP visualization tools

### 🐍 **python_scripts/** (13 files)
- Utility scripts, test files, and helper functions
- PowerShell scripts for Windows automation
- Configuration and setup scripts

### 📋 **config_files/** (6 files)
- `README.md` - Main project documentation
- `README_FORECASTING.md` - Forecasting system guide
- `README_ZONAL_DEMAND.md` - Zonal demand analysis guide
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `requirements.txt` - Python dependencies
- `requirements_forecasting.txt` - Forecasting-specific dependencies

### 🖼️ **images/** (4 files)
- `ontario_enhanced_geographic_map.png` - Ontario zone map
- `ontario_geographic_map.png` - Basic geographic map
- `ontario_zonal_demand_analysis.png` - Zonal demand analysis
- `ontario_zonal_demand_map.png` - Zonal demand visualization

### 📁 **data/** (0 files)
- Raw and processed data storage (currently empty)

### 📊 **results/** (1 file)
- Analysis results and outputs

## 🎯 **Key Benefits of This Organization**

1. **Easy Navigation**: Related files are grouped logically
2. **Professional Appearance**: Clean, industry-standard structure
3. **Maintainability**: Easy to find and update specific components
4. **Scalability**: New files can be added to appropriate folders
5. **Collaboration**: Team members can quickly understand the project

## 🚀 **Quick Start Guide**

- **View Dashboards**: Open files in `dashboards/` folder
- **Run Analysis**: Execute scripts in `analysis_scripts/` folder
- **Download Data**: Use scripts in `data_scripts/` folder
- **Configure**: Check `config_files/` for setup instructions

## 📝 **Next Steps**

1. **Test Dashboards**: Open HTML files to ensure they work correctly
2. **Run Forecasting**: Execute `analysis_scripts/run_forecasting.py`
3. **Download Data**: Use data scripts to collect fresh IESO data
4. **Customize**: Modify scripts and dashboards as needed

Your project is now organized and ready for professional development! 🎉
