# 🌾 Agri-Adapt AI: AI-Powered Agricultural Resilience Platform

> **Empowering Kenyan farmers with AI insights for drought-resilient farming**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Polars](https://img.shields.io/badge/Polars-0.20+-green.svg)](https://pola.rs)
[![Flask](https://img.shields.io/badge/Flask-2.3+-red.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Project Overview

Agri-Adapt AI addresses Kenya's critical food security challenge by providing smallholder farmers with AI-powered maize drought resilience scores. Using historical climate and soil data, our Random Forest model predicts crop resilience, helping farmers make informed planting decisions and reduce crop failures by 20-30%.

### 🌍 Problem Statement
- **Drought Impact**: 30% increase in drought frequency affecting rain-fed agriculture
- **Crop Failures**: 20-30% annual losses in vulnerable counties like Nakuru and Machakos
- **Data Gap**: Siloed climate, soil, and yield data leaves farmers without actionable insights
- **Food Security**: Maize is Kenya's staple crop, critical for national food security

### 🚀 Solution
- **AI-Powered Scoring**: Machine learning model predicts maize resilience (0-100%)
- **Actionable Insights**: Visual gauge with planting recommendations
- **Farmer-Focused**: Simple, mobile-friendly interface for low-literacy users
- **Data-Driven**: Integrates CHIRPS rainfall, AfSIS soil, and FAOSTAT yield data

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   ML Model      │
│   (HTML/CSS/JS) │◄──►│   (Python)      │◄──►│   (Random Forest)│
│                 │    │                 │    │                 │
│ • County Select │    │ • /api/predict  │    │ • Rainfall      │
│ • Input Forms   │    │ • /api/counties │    │ • Soil pH       │
│ • Gauge Chart   │    │ • Validation    │    │ • Organic Carbon│
│ • Results       │    │ • Error Handling│    │ • Yield Output  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/agri-adapt-ai.git
   cd agri-adapt-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Run AI Model Development**
   ```bash
   # Quick data analysis
   python scripts/analysis/quick_data_analysis.py
   
   # Full AI model pipeline
   python scripts/modeling/ai_model_development.py
   ```

5. **Run the application**
   ```bash
   python src/api/app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🏗️ Project Structure

```
scripts/                    # Organized script packages
├── analysis/              # Data analysis and visualization
├── data_processing/       # Data collection and integration
├── modeling/              # AI model development
└── utilities/             # Helper and maintenance tools

data/                      # Data storage and organization
├── analysis/              # Generated charts and plots
├── processed/             # Clean, integrated datasets
├── raw/                   # Original data sources
└── reports/               # Analysis summaries

src/                       # Source code
├── api/                   # Flask API implementation
├── models/                # Model definitions
├── utils/                 # Utility modules
└── frontend/              # Frontend components
```

*For detailed structure, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)*

## 📊 Usage Example

### Demo Scenario: Nakuru County
1. **Select County**: Choose "Nakuru" from dropdown
2. **Input Parameters**:
   - Rainfall: 800 mm/year
   - Soil pH: 6.5
   - Organic Carbon: 2.1%
3. **Get Results**: 
   - Resilience Score: 86% (Green Gauge)
   - Predicted Yield: 4.32 t/ha
   - Recommendation: "High Resilience - Plant maize with drought-tolerant varieties"

### API Endpoints

```bash
# Health check
GET /api/health

# Get Kenya counties
GET /api/counties

# Predict resilience score
POST /api/predict
{
  "county": "Nakuru",
  "rainfall": 800.0,
  "soil_ph": 6.5,
  "organic_carbon": 2.1
}

# Model status
GET /api/model/status
```

## 🔬 Technical Details

### Machine Learning Model
- **Algorithm**: Random Forest Regressor (100 trees)
- **Features**: Annual rainfall, soil pH, organic carbon
- **Target**: Maize yield (tonnes/ha)
- **Performance**: R² ≥ 0.85, 5-fold cross-validation
- **Interpretability**: Feature importance analysis

### Data Sources
- **CHIRPS**: High-resolution rainfall data (0.05°, 1981-2024)
- **AfSIS**: Soil properties (pH, organic carbon, 250m resolution)
- **FAOSTAT**: Global crop production statistics
- **Processing**: Polars for efficient data manipulation

### Technology Stack
- **Backend**: Flask (Python) with CORS support
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Charts**: Chart.js for interactive visualizations
- **Styling**: Bootstrap 5 with custom CSS
- **Data**: Polars for high-performance data processing

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_maize_model.py -v
```

## 📁 Project Structure

```
agri-adapt-ai/
├── src/                    # Source code
│   ├── api/               # Flask API endpoints
│   ├── models/            # Machine learning models
│   ├── data_processing/   # Data pipeline
│   ├── frontend/          # Web interface
│   └── utils/             # Helper functions
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── config/                # Configuration files
├── data/                  # Data files
├── notebooks/             # Jupyter notebooks
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── deployment/            # Deployment configs
```

## 🎯 Hackathon Deliverables

### ✅ Completed (Sprints 1-3)
- [x] Project structure and setup
- [x] Machine learning model (Random Forest)
- [x] Flask API with endpoints
- [x] Frontend HTML/CSS design
- [x] Unit tests for core functionality

### 🔄 In Progress (Sprint 4)
- [x] JavaScript dashboard functionality
- [x] API integration
- [x] Chart.js visualizations
- [x] Form validation and error handling

### 📋 Remaining (Sprints 5-6)
- [ ] End-to-end testing
- [ ] Bug fixes and polish
- [ ] Accessibility improvements
- [ ] Pitch deck preparation
- [ ] Demo rehearsal

## 🌟 Key Features

### Must-Have (MVP)
- ✅ County selection (47 Kenyan counties)
- ✅ Maize drought resilience scoring (0-100%)
- ✅ Interactive gauge visualization
- ✅ Mobile-responsive design

### Should-Have
- ✅ Input validation and error handling
- ✅ Feature importance visualization
- ✅ Planting recommendations
- ✅ Loading states and user feedback

### Could-Have
- ✅ Tooltips and explanations
- ✅ Basic error logging
- ✅ Accessibility features (WCAG 2.1)

## 🎭 Demo Script

**5-Minute Pitch Structure:**
1. **Problem** (1 min): Drought impact on Kenyan agriculture
2. **Solution** (1 min): AI-powered resilience scoring
3. **Live Demo** (2 min): Nakuru county scenario
4. **Impact & Vision** (1 min): Food security and scaling

**Demo Flow:**
1. Open dashboard → Select "Nakuru"
2. Input: 800mm rainfall, pH 6.5, 2.1% organic carbon
3. Show: 86% resilience score, green gauge
4. Explain: Feature importance and recommendations

## 🤝 Contributing

This is a hackathon project. For contributions:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **KALRO**: Kenya Agricultural and Livestock Research Organization
- **CHIRPS**: Climate Hazards Group InfraRed Precipitation with Station data
- **AfSIS**: Africa Soil Information Service
- **FAOSTAT**: Food and Agriculture Organization Statistics
- **Inflection AI**: Hackathon organizers and mentors

## 📞 Contact

- **Team**: Agri-Adapt AI Hackathon Team
- **Project**: [GitHub Repository](https://github.com/your-username/agri-adapt-ai)
- **Demo**: [Live Application](http://localhost:5000)

---

**Built with ❤️ for sustainable agriculture in Kenya**

*Last updated: August 29, 2025*