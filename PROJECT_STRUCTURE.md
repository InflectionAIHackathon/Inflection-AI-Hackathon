# 🏗️ **Project Structure Documentation**

## 📁 **Directory Organization**

```
Inflection-AI-Hackathon/
├── 📁 config/                          # Configuration files
│   └── settings.py                     # Global project settings
├── 📁 data/                            # Data storage and organization
│   ├── 📁 analysis/                    # Analysis outputs and visualizations
│   │   ├── maize_relationships_analysis.png
│   │   ├── rainfall_yield_analysis.png
│   │   └── random_forest_performance.png
│   ├── 📁 models/                      # Trained model storage
│   ├── 📁 processed/                   # Processed datasets
│   │   ├── master_water_scarcity_dataset_realistic.csv
│   │   ├── kenya_counties_weather_2019-2023.csv
│   │   └── county_maize_yields_2019-2023.csv
│   ├── 📁 raw/                         # Raw data sources
│   │   ├── kenya_maize_production.csv
│   │   └── kenya_soil_properties_isric.csv
│   ├── 📁 reports/                     # Analysis reports and summaries
│   │   ├── QUICK_ANALYSIS_SUMMARY.md
│   │   ├── AI_MODEL_DEVELOPMENT_SUMMARY.md
│   │   ├── comprehensive_data_quality_analysis.json
│   │   └── dataset_analysis_report.json
│   ├── 📁 water_scarcity_dashboard/    # Dashboard-specific data
│   ├── 📁 weather_data/                # Weather data storage
│   ├── 📁 chirps_data/                 # CHIRPS rainfall data
│   └── 📁 AfSP012Qry_ISRIC/           # ISRIC soil data
├── 📁 deployment/                      # Deployment configurations
├── 📁 docs/                            # Documentation
│   ├── 📁 technical/                   # Technical documentation
│   │   ├── AI_MODEL_DEVELOPMENT.md
│   │   └── QUICK_DATA_ANALYSIS_SUMMARY.md
│   ├── 📁 user_guide/                  # User documentation
│   └── 📁 api/                         # API documentation
├── 📁 logs/                            # Application logs
├── 📁 models/                          # Model artifacts (legacy)
├── 📁 notebooks/                       # Jupyter notebooks
├── 📁 reports/                         # Generated reports (legacy)
├── 📁 scripts/                         # Organized script packages
│   ├── 📁 analysis/                    # Data analysis scripts
│   │   ├── __init__.py
│   │   ├── quick_data_analysis.py
│   │   └── exploratory_data_analysis.py
│   ├── 📁 data_processing/             # Data processing scripts
│   │   ├── __init__.py
│   │   ├── create_water_scarcity_data.py
│   │   ├── integrate_all_datasets.py
│   │   └── collect_openmeteo_data.py
│   ├── 📁 modeling/                    # AI model development
│   │   ├── __init__.py
│   │   ├── ai_model_development.py
│   │   └── quick_data_analysis_and_modeling.py
│   ├── 📁 utilities/                   # Utility and maintenance
│   │   ├── __init__.py
│   │   ├── cleanup_project.py
│   │   └── fix_dashboard_data_with_real_weather.py
│   └── __init__.py
├── 📁 src/                             # Source code
│   ├── 📁 api/                         # API implementation
│   ├── 📁 data_processing/             # Data processing modules
│   ├── 📁 frontend/                    # Frontend components
│   ├── 📁 models/                      # Model definitions
│   ├── 📁 utils/                       # Utility modules
│   └── __init__.py
├── 📁 tests/                           # Test suite
│   └── 📁 unit/                        # Unit tests
│       └── test_ai_model.py
├── 📁 wandb/                           # Weights & Biases logs
├── .gitignore                          # Git ignore rules
├── PROJECT_STRUCTURE.md                 # This file
├── README.md                           # Main project README
├── requirements.txt                     # Production dependencies
└── requirements-dev.txt                 # Development dependencies
```

## 🔧 **Script Organization**

### **Analysis Scripts** (`scripts/analysis/`)
- **Purpose**: Data exploration, visualization, and correlation analysis
- **Key Files**: Rainfall vs yield analysis, exploratory data analysis
- **Outputs**: Charts, plots, correlation reports

### **Data Processing Scripts** (`scripts/data_processing/`)
- **Purpose**: Data collection, integration, and preprocessing
- **Key Files**: Dataset creation, weather data collection, integration
- **Outputs**: Clean, processed datasets ready for modeling

### **Modeling Scripts** (`scripts/modeling/`)
- **Purpose**: AI model development, training, and evaluation
- **Key Files**: Random Forest implementation, hyperparameter tuning
- **Outputs**: Trained models, performance metrics, feature importance

### **Utility Scripts** (`scripts/utilities/`)
- **Purpose**: Project maintenance, cleanup, and fixes
- **Key Files**: Project organization, dashboard data fixes
- **Outputs**: Clean project structure, fixed data issues

## 📊 **Data Organization**

### **Analysis** (`data/analysis/`)
- **Content**: Generated charts, plots, and visualizations
- **Purpose**: Store analysis outputs for documentation and review
- **Formats**: PNG, JPG, SVG files

### **Processed** (`data/processed/`)
- **Content**: Clean, integrated datasets ready for modeling
- **Purpose**: Store final datasets used in analysis and modeling
- **Formats**: CSV, Parquet, HDF5 files

### **Raw** (`data/raw/`)
- **Content**: Original data sources before processing
- **Purpose**: Preserve original data for reproducibility
- **Formats**: CSV, JSON, shapefiles

### **Reports** (`data/reports/`)
- **Content**: Analysis summaries, quality reports, JSON metadata
- **Purpose**: Document data quality and analysis findings
- **Formats**: Markdown, JSON, HTML

## 🚀 **Key Benefits of This Organization**

1. **Clear Separation of Concerns**: Each directory has a specific purpose
2. **Easy Navigation**: Logical grouping makes finding files simple
3. **Scalability**: Easy to add new scripts and data types
4. **Maintainability**: Clear structure reduces confusion
5. **Documentation**: Self-documenting through organization
6. **Testing**: Organized structure supports comprehensive testing
7. **Deployment**: Clear separation of source, data, and outputs

## 📝 **File Naming Conventions**

- **Scripts**: `snake_case.py` (e.g., `quick_data_analysis.py`)
- **Data Files**: `descriptive_name.csv` (e.g., `master_water_scarcity_dataset_realistic.csv`)
- **Reports**: `UPPER_CASE.md` (e.g., `AI_MODEL_DEVELOPMENT_SUMMARY.md`)
- **Configs**: `snake_case.py` (e.g., `settings.py`)
- **Tests**: `test_module_name.py` (e.g., `test_ai_model.py`)

## 🔄 **Maintenance Guidelines**

1. **Keep Scripts Organized**: Place new scripts in appropriate subdirectories
2. **Update __init__.py Files**: Document new scripts when added
3. **Clean Temporary Files**: Remove temporary outputs and logs regularly
4. **Version Control**: Commit organized structure changes
5. **Documentation**: Update this file when structure changes

---

*Last Updated: August 30, 2025*  
*Version: 1.0.0*  
*Maintainer: Agri-Adapt AI Team* 🚀
