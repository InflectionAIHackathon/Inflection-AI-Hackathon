# 🌾 Agri-Adapt AI: AI-Powered Agricultural Resilience Platform

![Agri-Adapt AI Logo](https://img.shields.io/badge/Agri--Adapt-AI-brightgreen?style=for-the-badge&logo=leaf&logoColor=white)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Polars](https://img.shields.io/badge/Polars-0.20+-green.svg)](https://pola.rs)
[![Next.js](https://img.shields.io/badge/Next.js-15+-black.svg)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Empowering Kenyan farmers with AI-driven drought resilience insights to make informed crop decisions and reduce agricultural losses by up to 30%.**

---

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
│   Frontend      │    │   FastAPI       │    │   ML Model      │
│   (Next.js/React)│◄──►│   (Python)      │◄──►│   (Random Forest)│
│                 │    │                 │    │                 │
│ • County Select │    │ • /api/predict  │    │ • Rainfall      │
│ • Input Forms   │    │ • /api/counties │    │ • Soil pH       │
│ • Gauge Chart   │    │ • Validation    │    │ • Organic Carbon│
│ • Results       │    │ • Error Handling│    │ • Yield Output  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features

- 🎯 **Drought Resilience Scoring**: AI-powered county-level resilience scores (0-100%)
- 🗺️ **Interactive County Selection**: Easy-to-use dropdown and map interface
- 📊 **Data Visualization**: Interactive charts showing weather patterns and yield predictions
- 📱 **Mobile-First Design**: Optimized for smartphones with offline capability
- ♿ **Accessibility**: WCAG 2.1 compliant with multi-language support
- ⚡ **Real-Time Processing**: Sub-second response times for score calculations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/agri-adapt-ai.git
   cd agri-adapt-ai
   ```

2. **Backend Setup (Python/FastAPI)**

   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install Python dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup (Next.js/React)**

   ```bash
   # Install Node.js dependencies
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

4. **Start the Backend**

   ```bash
   python scripts/start_backend.py
   # Backend will run on http://localhost:8000
   ```

5. **Start the Frontend**
   ```bash
   npm run dev
   # Frontend will run on http://localhost:3000
   ```

---

## 🏗️ Project Structure

```
agri-adapt-ai/
├── 📁 app/                    # Next.js app directory
│   ├── page.tsx              # Main dashboard page
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── 📁 components/             # React components
│   ├── ui/                   # Reusable UI components
│   ├── resilience-gauge.tsx  # Resilience score display
│   ├── recommendations-panel.tsx # Farming recommendations
│   ├── data-visualization.tsx    # Charts and graphs
│   └── weather-integration.tsx   # Weather data integration
├── 📁 src/                    # Python backend source
│   ├── api/                  # FastAPI application
│   ├── models/               # ML model classes
│   └── utils/                # Utility functions
├── 📁 config/                 # Configuration files
├── 📁 models/                 # Trained ML models
├── 📁 data/                   # Dataset files
├── 📁 scripts/                # Training and utility scripts
└── 📁 tests/                  # Test suites
```

---

## 🔧 Backend API Endpoints

### Core Endpoints

- `GET /health` - System health check
- `GET /api/counties` - List of Kenya counties
- `POST /api/predict` - Single prediction
- `POST /api/predict/batch` - Batch predictions
- `GET /api/model/status` - Model performance info
- `GET /api/metrics` - Usage statistics

### Example API Usage

```bash
# Make a prediction
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "rainfall": 800,
    "soil_ph": 6.5,
    "organic_carbon": 2.1,
    "county": "Nakuru"
  }'
```

---

## 🎨 Frontend Features

### Dashboard Components

- **Resilience Gauge**: Visual representation of drought resilience score
- **County Selector**: Interactive dropdown with search functionality
- **Recommendations Panel**: Actionable farming advice based on scores
- **Data Visualization**: Interactive charts for weather and yield data
- **Weather Integration**: Real-time weather data for selected counties
- **Cost Calculator**: Input cost analysis for different farming strategies

### Technology Stack

- **Framework**: Next.js 15 with App Router
- **UI Library**: React 18 with TypeScript
- **Styling**: Tailwind CSS 4 with custom components
- **Components**: Radix UI for accessibility
- **Charts**: Recharts for data visualization
- **Forms**: React Hook Form with Zod validation

---

## 🧪 Testing

### Backend Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_backend_api.py

# Run with coverage
python -m pytest --cov=src
```

### Frontend Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

---

## 🚀 Deployment

### Backend Deployment

```bash
# Using Docker
docker build -t agri-adapt-ai-backend .
docker run -p 8000:8000 agri-adapt-ai-backend

# Using Docker Compose
docker-compose up -d
```

### Frontend Deployment

```bash
# Build for production
npm run build

# Start production server
npm start

# Deploy to Vercel
vercel --prod
```

---

## 📊 Model Performance

- **R² Score**: 0.7 (70% accuracy)
- **Algorithm**: Random Forest Regressor
- **Features**: Rainfall, Soil pH, Organic Carbon
- **Training Data**: Historical climate and soil data
- **Cross-validation**: 5-fold CV with consistent performance

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Kenyan farmers for their valuable insights
- Climate data providers (CHIRPS, AfSIS, FAOSTAT)
- Open-source community for tools and libraries
- Agricultural experts for domain knowledge

---

## 📞 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: [GitHub Issues](https://github.com/your-username/agri-adapt-ai/issues)
- **Email**: support@agri-adapt-ai.com

---

**Built with ❤️ for sustainable agriculture in Kenya**
