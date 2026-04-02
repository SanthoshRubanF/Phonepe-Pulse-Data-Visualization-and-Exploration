# PhonePe Pulse Data Visualization and Exploration

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive, production-ready web-based dashboard for visualizing and exploring PhonePe Pulse transaction data across India. Built with Streamlit and Plotly for interactive, real-time data visualization.

## 🎯 Project Overview

This project provides a complete solution for extracting, processing, and visualizing PhonePe Pulse data through an intuitive interactive dashboard. It leverages modern Python libraries to deliver insights into transaction patterns, insurance data, and user behavior across India.

## ✨ Key Features

- **📊 Interactive Dashboard**: Multi-page Streamlit application with responsive design
- **💳 Transaction Analysis**: Deep dive into transaction data with state-wise breakdowns
- **🛡️ Insurance Insights**: Complete insurance transaction analysis and trends
- **👥 User Demographics**: Device preferences and user behavior analysis
- **🗺️ Geographic Visualizations**: Choropleth maps showing state-wise distribution
- **📈 Time Series Analysis**: Year and quarter-wise trend analysis
- **⚡ Real-time Updates**: Dynamic data loading and filtering
- **🎨 Professional UI**: Modern, responsive design matching PhonePe Pulse aesthetics
- **10+ Analysis Options**: Multiple filtering and visualization options
- **📱 Responsive Design**: Works seamlessly across all devices

## 🏗️ Project Architecture

```
phonepe-pulse/
├── app/                           # Streamlit application
│   ├── __init__.py
│   ├── main.py                    # Main dashboard entry point
│   └── pages/                     # Multi-page components
│       ├── 01_Transaction_Analysis.py
│       ├── 02_Insurance_Analysis.py
│       └── 03_User_Analysis.py
│
├── config/                        # Configuration management
│   ├── __init__.py
│   └── settings.py               # Centralized settings
│
├── src/                          # Source modules
│   ├── __init__.py
│   ├── data_loader.py           # Data extraction and loading
│   ├── visualizations.py        # Chart and visualization creation
│   └── utils.py                 # Utility functions
│
├── pulse/                        # Data directory (downloaded)
│   └── data/                     # JSON data files
│
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── SETUP.md                      # Detailed setup guide
└── QUICKSTART.md                # Quick start guide
```

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- 2GB RAM minimum
- PostgreSQL 12+ (optional, for database backend)

### Technology Stack
- **Frontend**: Streamlit, Plotly
- **Data Processing**: Pandas, NumPy
- **Database**: PostgreSQL with psycopg2
- **API**: Requests library for data fetching
- **Configuration**: python-dotenv for environment management

### Python Packages
```
pandas>=1.5.0
streamlit>=1.28.0
psycopg2-binary>=2.9.0
plotly>=5.17.0
streamlit-option-menu>=0.3.10
requests>=2.31.0
python-dotenv>=1.0.0
```

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/SanthoshRubanF/Phonepe-Pulse-Data-Visualization-and-Exploration.git
cd Phonepe-Pulse-Data-Visualization-and-Exploration
```

### Step 2: Create Python Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

1. Copy environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```env
# Database Configuration (Optional - for PostgreSQL backend)
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_NAME=phonepe
DB_PORT=5432

# Data Configuration
DATA_BASE_PATH=./pulse/data

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
THEME=light
```

### Step 5: Download Data (Optional)

The project includes sample data. To download complete PhonePe Pulse data:

1. Clone the official PhonePe Pulse repository:
```bash
git clone https://github.com/PhonePe/pulse.git
```

2. Update `DATA_BASE_PATH` in `.env` to point to the data directory:
```env
DATA_BASE_PATH=../pulse/data
```

### Step 6: Run the Application

```bash
streamlit run app/main.py
```

The dashboard will be available at `http://localhost:8501`

## 📚 Usage Guide

### Dashboard Navigation

1. **Home Page** (`app/main.py`)
   - Overview statistics
   - Quick access to all features
   - Data source information

2. **Transaction Analysis**
   - Analyze by year, quarter, state
   - View transaction types
   - Compare transaction metrics

3. **Insurance Analysis**
   - Insurance type analysis
   - Premium distribution
   - State-wise insurance data

4. **User Analysis**
   - Device preferences
   - User growth trends
   - Brand distribution

### Filtering & Selection

Use the sidebar to:
- Select analysis type
- Choose time period (year, quarter)
- Pick specific states
- Filter by transaction or insurance type

### Interpreting Visualizations

- **Bar Charts**: Compare values across categories
- **Choropleth Maps**: Geographic distribution visualization
- **Pie Charts**: Show proportional relationships
- **Line Charts**: Analyze trends over time
- **Metric Cards**: Display key statistics

## 🔧 Project Modules

### `config/settings.py`
Central configuration management with support for:
- Database connections
- Data path configuration
- Application settings
- Environment variable loading

**Usage:**
```python
from config.settings import config

db_host = config.DB_HOST
data_path = config.AGG_TRANSACTION_PATH
```

### `src/data_loader.py`
Handles data loading from JSON files and databases.

**Key Classes:**
- `DataLoader`: Main class for loading all data types

**Usage:**
```python
from src.data_loader import DataLoader

loader = DataLoader()
df = loader.load_from_json('aggregated', 'transaction')
```

### `src/visualizations.py`
Creates all charts and visualizations.

**Key Class:**
- `DashboardVisualizations`: Creates all dashboard charts

**Methods:**
- `create_bar_chart()`: Create bar charts
- `create_choropleth_map()`: Create geo maps
- `create_pie_chart()`: Create pie charts
- `create_line_chart()`: Create trend lines
- `create_metric_card()`: Display metric cards

**Usage:**
```python
from src.visualizations import DashboardVisualizations

viz = DashboardVisualizations(geojson_url)
fig = viz.create_bar_chart(df, 'States', 'value', 'Title')
```

### `src/utils.py`
Utility functions for data processing and validation.

**Key Functions:**
- `clean_state_names()`: Standardize state names
- `validate_dataframe()`: Check data validity
- `get_available_years()`: Extract available years
- `get_available_states()`: Get state list
- `format_currency()`: Format numbers as currency
- `get_summary_stats()`: Calculate statistics
- `fetch_geojson()`: Fetch and cache GeoJSON

## 📊 Analysis Options

The dashboard provides **10+ different analysis options**:

1. **Transaction Analysis by Year**
2. **Transaction Analysis by Quarter**
3. **Transaction Analysis by State**
4. **Transaction Analysis by Type**
5. **Insurance Analysis by Year**
6. **Insurance Analysis by State**
7. **Insurance Analysis by Type**
8. **User Analysis by Year**
9. **User Analysis by State**
10. **Device Brand Analysis**

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure you're in virtual environment
pip install -r requirements.txt
```

### Data Loading Problems
```bash
# Check DATA_BASE_PATH in .env
# Verify JSON files exist
# Check file permissions
```

### Port Already in Use
```bash
# Use different port
streamlit run app/main.py --server.port 8502
```

## 📝 Code Standards

This project follows PEP 8 style guide with:
- Type hints for function arguments
- Comprehensive docstrings
- Modular function design
- Error handling and logging
- Clean variable naming

## 🚀 Deployment

### Local Development
```bash
streamlit run app/main.py
```

### Production Deployment Using Streamlit Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Configure environment variables
4. Deploy

## 📊 Data Processing Pipeline

```
Raw JSON Data (PhonePe Pulse)
           ↓
    DataLoader Module
           ↓
  Data Cache (Session)
           ↓
  Visualization Module
           ↓
   Dashboard UI
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👏 Acknowledgments

- **PhonePe Pulse Team** for the data repository
- **Streamlit** for the amazing framework
- **Plotly** for interactive visualizations

## 📞 Support & Contact

For questions or issues:
- 📧 Create an issue on GitHub
- 💬 Check existing discussions
- 📚 Review documentation

## 🔄 Version History

### v2.0.0 (2026-04-02)
- ✅ Complete refactoring with modular architecture
- ✅ Enhanced UI matching PhonePe Pulse design
- ✅ Improved data loading and validation
- ✅ Added comprehensive documentation
- ✅ Type hints throughout codebase
- ✅ Better error handling and logging

### v1.0.0 (Initial Release)
- Initial dashboard implementation

---

**Built with ❤️  using Python, Streamlit, and Plotly**

*Last Updated: April 2, 2026*

