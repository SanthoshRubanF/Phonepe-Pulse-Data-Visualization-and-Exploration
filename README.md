# PhonePe Pulse Data Visualization and Exploration

![Status](https://img.shields.io/badge/status-production%20ready-success.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A comprehensive, production-ready web-based dashboard for visualizing and exploring PhonePe Pulse transaction data across all 36 Indian states and union territories. Built with Streamlit and Plotly for interactive, real-time data visualization with complete data coverage from 2018-2024.

## 🎯 Project Overview

This project provides a complete solution for extracting, processing, and visualizing PhonePe Pulse data through an intuitive, modular dashboard. It delivers insights into transaction patterns, insurance data, and user behavior across India with full geographic coverage.

**Data Coverage:**
- **37 Geographic Entities**: All 36 Indian states/UTs + India-wide aggregate
- **Time Period**: 2018-2024 (7 years of quarterly data)
- **Data Types**: Transactions, Insurance, and User demographics
- **Total Records**: 23,600+ rows of processed data

## ✨ Key Features

- **📊 Interactive Multi-Page Dashboard**: Streamlit application with responsive, theme-aware design
- **💳 Transaction Analysis**: Complete transaction data with state-wise and quarterly breakdowns
- **🛡️ Insurance Insights**: Insurance transaction analysis across all states and insurance types
- **👥 User Demographics**: Device preferences and user behavior analysis
- **🗺️ Geographic Visualization**: Choropleth maps showing state-wise data distribution
- **📈 Time Series Analysis**: Year and quarter-wise trend analysis with filtering
- **⚡ Dynamic Data Loading**: Efficient JSON parsing with session-based caching
- **🎨 Professional UI**: Modern design matching PhonePe Pulse aesthetics with light/dark theme support
- **10+ Analysis Options**: Multiple filtering and visualization combinations
- **📱 Responsive Design**: Optimized for desktop, tablet, and mobile devices

## 🏗️ Project Architecture

```
Phonepe-Pulse-Data-Visualization-and-Exploration/
├── app/                              # Streamlit application (multi-page)
│   ├── __init__.py
│   ├── main.py                       # Homepage with metrics and feature overview
│   └── pages/                        # Analysis pages
│       ├── 01_Transaction_Analysis.py
│       ├── 02_Insurance_Analysis.py
│       └── 03_User_Analysis.py
│
├── config/                           # Configuration module
│   ├── __init__.py
│   └── settings.py                   # Centralized settings with environment variables
│
├── bundled_pulse_data/               # Bundled PhonePe Pulse JSON data for deployment
│   ├── aggregated/
│   ├── map/
│   └── top/
│
├── src/                              # Core business logic
│   ├── __init__.py
│   ├── data_loader.py               # JSON data loading (country + state level)
│   ├── visualizations.py            # Chart creation (8 visualization types)
│   └── utils.py                     # Helper functions and utilities
│
├── pulse/                            # PhonePe Pulse data (downloaded)
│   └── data/                         # JSON data files (organized by type, geography, time)
│
├── .env                              # Environment variables configuration
├── requirements.txt                  # Python package dependencies
└── README.md                         # This documentation file
```

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- 1GB RAM minimum
- Internet connection (for initial data download and GeoJSON files)
- PostgreSQL 12+ (optional, for database backend)

### Technology Stack
- **Frontend Framework**: Streamlit 1.52.2
- **Visualization**: Plotly 5.17.0
- **Data Processing**: Pandas, NumPy
- **HTTP Requests**: Requests 2.31.0
- **Environment Management**: python-dotenv 1.0.0

### Python Packages
```
streamlit==1.52.2
plotly==5.17.0
pandas
numpy
requests==2.31.0
python-dotenv==1.0.0
```

All packages are listed in `requirements.txt` and installed via `pip install -r requirements.txt`

## 🚀 Installation & Setup

### Quick Start (5 minutes)

**Step 1: Clone Repository**
```bash
git clone https://github.com/SanthoshRubanF/Phonepe-Pulse-Data-Visualization-and-Exploration.git
cd Phonepe-Pulse-Data-Visualization-and-Exploration
```

**Step 2: Create Virtual Environment**
- Windows:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

**Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Step 4: Configure Data Path (if needed)**

The `.env` file is pre-configured with default values:
```env
DATA_BASE_PATH=./pulse/data
```

If you're using a different path or operating system, edit `.env`:
- **Windows**: Use absolute paths with backslashes or forward slashes
- **macOS/Linux**: `DATA_BASE_PATH=./pulse/data` (relative path from project root)

If `DATA_BASE_PATH` is missing or points to a location that does not exist, the app automatically falls back to the bundled dataset in `bundled_pulse_data/`. If that folder is unavailable, it then checks `pulse/data`.

**Step 5: Run Dashboard**
```bash
streamlit run app/main.py
```

Access the dashboard at: **http://localhost:8501**

### PostgreSQL Database Setup (Optional)

For production deployments, you can use PostgreSQL database instead of JSON files:

**Step 1: Configure Database**
```env
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=phonepe
DB_PORT=5432
```

**Step 2: Setup Database**
```bash
python src/database.py --full-setup
```

This will:
- ✅ Test database connection
- ✅ Create necessary tables
- ✅ Sync data from JSON to PostgreSQL

**Step 3: Run Dashboard**
```bash
streamlit run app/main.py
```

The dashboard will automatically use PostgreSQL if available, with automatic fallback to JSON files.

See [DATABASE_SETUP.md](DATABASE_SETUP.md) for comprehensive database documentation.

### Initial Data Setup

The repository includes PhonePe Pulse data (2018-2024) in the `pulse/data/` directory.

**If you need to update the data:**
```bash
# Clone the official PhonePe Pulse repository
git clone https://github.com/PhonePe/pulse.git

# Update DATA_BASE_PATH in .env to point to the cloned data
# Example: DATA_BASE_PATH=../pulse/data
```

### Troubleshooting Setup

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Verify virtual environment is activated and dependencies installed |
| `FileNotFoundError` for data | Check `DATA_BASE_PATH` in `.env` - ensure path exists |
| Port 8501 in use | Run: `streamlit run app/main.py --server.port 8502` |
| Slow data loading | First run caches data in session. Subsequent runs are faster |

## 📚 Usage Guide

### Dashboard Navigation

The application is a multi-page Streamlit dashboard with the following structure:

1. **🏠 Home Page** (`app/main.py`)
   - **Key Metrics**: Total transactions, transaction amount, states covered, years available
   - **Feature Overview**: Quick access to all analysis types
   - **Data Source**: Information about PhonePe Pulse data
   - **Theme Toggle**: Switch between light and dark modes

2. **💳 Transaction Analysis** (`01_Transaction_Analysis.py`)
   - Transaction data from 2018-2024
   - Filter by year, quarter, state, and transaction type
   - Visualizations: Bar charts, choropleth maps, trend lines, metric cards
   - Analysis types: Year-wise, quarter-wise, state-wise comparisons

3. **🛡️ Insurance Analysis** (`02_Insurance_Analysis.py`)
   - Insurance transaction data from 2020-2024
   - Filter by year, state, and insurance type
   - Visualizations: Bar charts, pie charts, geographic maps
   - Insights: Premium distribution, insurance type popularity

4. **👥 User Analysis** (`03_User_Analysis.py`)
   - User demographics and device preferences
   - Data from 2018-2024
   - Filter by year and state
   - Visualizations: Device brand analysis, user growth trends

### Data Selection & Filtering

Use the sidebar on each page to:
- **Select Time Period**: Choose specific year(s) or quarter(s)
- **Geographic Filter**: Select individual states or view all-India aggregate
- **Category Filter**: Choose specific transaction types, insurance types, or device brands
- **View Toggle**: Switch between different visualization types

### Interpreting Visualizations

- **Bar Charts**: Compare metrics across categories (states, quarters, types)
- **Choropleth Maps**: Geographic distribution of data across states with color intensity
- **Pie Charts**: Show proportional relationships (e.g., insurance type distribution)
- **Line Charts**: Analyze trends over time (growth, seasonal patterns)
- **Metric Cards**: Display key statistics with large, prominent numbers
- **Scatter Plots**: Analyze relationships between two variables

### Data Coverage & Scope

**Geographic Coverage:**
- All 36 Indian states and union territories
- India-wide aggregates (country-level data)

**Time Coverage:**
- Transactions: 2018 Q2 - 2024 Q1 (7 years)
- Insurance: 2020 Q1 - 2024 Q1 (4+ years)
- Users: 2018 Q2 - 2024 Q1 (7 years)

## 🔧 Project Modules

### `config/settings.py`
Central configuration management using Python dataclasses.

**Features:**
- Environment variable loading via python-dotenv
- Type-safe configuration with dataclass
- Support for database and data path configuration
- All settings in one place for easy maintenance

**Usage:**
```python
from config.settings import config

data_path = config.AGG_TRANSACTION_PATH
db_host = config.DB_HOST
```

---

### `src/data_loader.py`
Handles data loading from PhonePe Pulse JSON files.

**Key Features:**
- Loads data from both country-level (India-wide) and state-level JSON files
- Supports three data types: Transaction, Insurance, User
- Automatic path construction for different geographic levels
- Data validation and cleaning
- Efficient DataFrame concatenation

**Main Class:**
```python
class DataLoader:
    def load_from_json(self, data_type: str) -> pd.DataFrame
    def load_from_database(self, data_type: str) -> pd.DataFrame  # Future
```

**Supported Data Types:**
- `'transaction'` or `'aggregated'` - Transaction data
- `'insurance'` - Insurance data
- `'user'` - User data

**Example:**
```python
from src.data_loader import DataLoader

loader = DataLoader()
transaction_df = loader.load_from_json('aggregated')
insurance_df = loader.load_from_json('insurance')
user_df = loader.load_from_json('user')
```

---

### `src/visualizations.py`
Creates all dashboard visualizations using Plotly.

**Visualization Types:**
1. **Bar Charts** - Categorical comparisons
2. **Pie Charts** - Proportional data
3. **Choropleth Maps** - Geographic distribution
4. **Line Charts** - Time series trends
5. **Scatter Plots** - Relationship analysis
6. **Metric Cards** - Key statistics
7. **Combination Charts** - Multi-metric views
8. **Hover Maps** - Interactive geographic data

**Main Class:**
```python
class DashboardVisualizations:
    def create_bar_chart(...) -> go.Figure
    def create_pie_chart(...) -> go.Figure
    def create_choropleth_map(...) -> go.Figure
    def create_line_chart(...) -> go.Figure
    def create_metric_card(...) -> go.Figure
    # ... and more
```

**Example:**
```python
from src.visualizations import DashboardVisualizations

viz = DashboardVisualizations()
fig = viz.create_bar_chart(
    df, 
    x_col='State',
    y_col='Transaction_Amount',
    title='Transaction Amount by State'
)
fig.show()
```

---

### `src/utils.py`
Utility functions for data processing and validation.

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `clean_state_names()` | Standardize state name formatting |
| `validate_dataframe()` | Check data integrity |
| `get_available_years()` | Extract available years from data |
| `get_available_states()` | Get list of all states with data |
| `format_currency()` | Format numbers as Indian currency (₹) |
| `get_summary_stats()` | Calculate statistics (sum, mean, count) |
| `fetch_geojson()` | Fetch and cache GeoJSON for maps |

---

### `src/database.py`
PostgreSQL database management and utilities.

**Features:**
- Connection management and pooling
- Automatic table creation with proper indexing
- Data synchronization from JSON to database
- Batch insert operations for performance
- Database statistics and diagnostics
- Automatic fallback to JSON if database unavailable

**Main Class:**
```python
class DatabaseManager:
    def test_connection() -> bool
    def setup_database() -> bool
    def sync_data() -> bool
    def get_database_stats() -> dict
    def clear_database(confirm: bool) -> bool
```

**Command-Line Usage:**
```bash
# Test database connection
python src/database.py --test

# Create database tables
python src/database.py --setup

# Sync JSON data to database
python src/database.py --sync

# Show database statistics
python src/database.py --stats

# Complete setup (test + setup + sync)
python src/database.py --full-setup

# Clear all database data
python src/database.py --clear
```

**Database Integration in DataLoader:**
The `DataLoader` class automatically supports both JSON and database sources:
```python
from src.data_loader import DataLoader

loader = DataLoader()

# Loads from database, falls back to JSON if unavailable
transactions = loader.load_from_database('transaction')
insurance = loader.load_from_database('insurance')
users = loader.load_from_database('user')
```

## 📊 Analysis Options

The dashboard provides **10+ different analysis combinations** through flexible filtering:

### Transaction Analysis (6+ options)
1. **Transaction Volume by Year** - Trend analysis across years
2. **Transaction Volume by Quarter** - Seasonal patterns and quarterly trends
3. **Transaction Amount by State** - Geographic comparison with choropleth map
4. **Top Transactions by Type** - Category-wise breakdown
5. **Quarterly Trend Analysis** - Line chart showing growth over time
6. **State Comparison Matrix** - Multi-state comparison dashboard

### Insurance Analysis (4+ options)
1. **Insurance Premiums by Year** - Trend over time
2. **Insurance Type Distribution** - Pie chart of insurance categories
3. **State-wise Insurance Coverage** - Choropleth map visualization
4. **Insurance Growth Metrics** - Year-over-year comparison

### User Analysis (4+ options)
1. **User Growth by Year** - Historical growth trends
2. **Device Brand Preferences** - Brand distribution pie chart
3. **State-wise User Distribution** - Geographic user analysis
4. **Brand Comparison Over Time** - Trend analysis by brand

**Total Combinations:** 14+ unique analysis views available through UI filtering

## 🐛 Troubleshooting

### Common Issues & Solutions

**1. ModuleNotFoundError (e.g., `No module named 'streamlit'`)**
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**2. Data Loading Errors**
- **Issue**: `FileNotFoundError: pulse/data directory not found`
- **Solution**: 
  - Verify data exists: Check `pulse/data/` folder has subdirectories (aggregated, map, top)
  - Check `.env` file: Ensure `DATA_BASE_PATH` points to correct location
  - Verify path permissions: Ensure read access to data files

**3. Port Already in Use (Streamlit at 8501)**
```bash
# Use alternative port
streamlit run app/main.py --server.port 8502

# Or kill existing process
# Windows: netstat -ano | findstr :8501
# macOS/Linux: lsof -i :8501
```

**4. Slow Data Loading on First Run**
- First run: Parses all JSON files and loads into memory (~30-60 seconds)
- Subsequent runs: Uses session cache, much faster
- Normal behavior - allows interactive dashboard without database

**5. Visualization Not Rendering**
- Clear Streamlit cache: `streamlit cache clear`
- Restart dashboard: Press `C` in terminal, then rerun
- Check browser console for errors: F12 → Console tab

**6. States Showing as File Names (e.g., "1.json")**
- This means data extraction encountered issues with file paths
- Check that all JSON files are properly formatted in `pulse/data/`
- Verify no path separator issues (shouldn't happen with current code, but check .env path format)

### Getting Help

1. **Check Logs**: Run app and watch terminal output for errors
2. **Verify Configuration**: Check `.env` file values
3. **Test Data Path**:
   ```bash
   python -c "from config.settings import config; print(config.DATA_BASE_PATH)"
   ```
4. **Clear Cache & Restart**:
   ```bash
   streamlit cache clear
   streamlit run app/main.py
   ```

## 📝 Code Standards

This project follows professional Python development practices:

- **Style Guide**: PEP 8 compliance with 88-character line length (Black formatter compatible)
- **Type Hints**: Full type annotations on function arguments and return values
- **Documentation**: Comprehensive docstrings for all classes and functions
- **Error Handling**: Proper exception handling with informative error messages
- **Code Organization**: Modular design with single responsibility principle
- **Variable Naming**: Clear, descriptive names (no single letters except loop counters)
- **Import Structure**: Organized imports (stdlib → third-party → local)

### Code Quality

- ✅ No hardcoded values (all configuration in `config/settings.py`)
- ✅ DRY principle (no repeated code blocks)
- ✅ Proper separation of concerns (data vs. visualization vs. UI)
- ✅ Extensible architecture for adding new analysis types
- ✅ Session caching for performance optimization

## 🚀 Deployment

### Local Development
```bash
streamlit run app/main.py --logger.level=info
```
- Accessible at: http://localhost:8501
- Auto-reloads on file changes
- Full debug information in terminal

### Production Deployment

#### Option 1: Streamlit Cloud (Recommended)
1. Push code to GitHub repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select repository, branch, and `app/main.py` as main file
5. Add secrets (`.env` values) in Cloud settings
6. Deploy

#### Option 2: Docker Container
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Run with:
```bash
docker build -t phonepe-dash .
docker run -p 8501:8501 -e DATA_BASE_PATH=/app/pulse/data phonepe-dash
```

#### Option 3: Self-Hosted Server
```bash
# SSH into server and setup
ssh user@server.com
git clone <repo-url>
cd project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/phonepe-dash.service
```

Systemd service file example:
```ini
[Unit]
Description=PhonePe Pulse Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/user/Phonepe-Pulse-Dashboard
Environment="PATH=/home/user/Phonepe-Pulse-Dashboard/venv/bin"
ExecStart=/home/user/Phonepe-Pulse-Dashboard/venv/bin/streamlit run app/main.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable phonepe-dash
sudo systemctl start phonepe-dash
```

### Environment Variables for Production
```env
# Required
DATA_BASE_PATH=/path/to/pulse/data

# Optional
DEBUG=False
LOG_LEVEL=WARNING
THEME=light
```

## 📊 Data Processing Pipeline

```
Raw PhonePe Pulse JSON Files (Country & State Level)
           ↓
    DataLoader Module (Automatic Path Construction)
           ↓
    Clean & Validate Data
           ↓
  Cache in Streamlit Session
           ↓
  Visualization Module (Plotly)
           ↓
  Interactive Dashboard UI (Streamlit Pages)
           ↓
  Browser Display (http://localhost:8501)
```

**Performance Characteristics:**
- First load: ~30-60 seconds (parses all JSON files)
- Subsequent loads: <1 second (uses session cache)
- Memory usage: ~150-200MB (in-memory DataFrame cache)
- Data freshness: Static (update by restarting app)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/yourusername/Phonepe-Pulse.git
   cd Phonepe-Pulse
   ```
3. **Create** a feature branch:
   ```bash
   git checkout -b feature/YourFeatureName
   ```
4. **Make** your changes with clear commit messages
5. **Push** to your fork:
   ```bash
   git push origin feature/YourFeatureName
   ```
6. **Open** a Pull Request with description of changes

### Development Setup
```bash
# Additional dev dependencies (optional)
pip install black flake8 mypy  # For code quality checks

# Run linter
flake8 src/ app/ config/

# Format code
black src/ app/ config/

# Type checking
mypy src/ app/ config/
```

## 📄 License

This project is licensed under the **MIT License** - see LICENSE file for details.

## 👏 Acknowledgments

- **PhonePe Pulse Team** ([github.com/PhonePe/pulse](https://github.com/PhonePe/pulse)) - for the comprehensive data repository
- **Streamlit Community** - for creating an amazing web framework
- **Plotly Team** - for powerful interactive visualization library
- **Contributors** - for improvements and bug fixes

## 📞 Support & Contact

For questions, issues, or suggestions:

| Type | Method |
|------|--------|
| 🐛 Bug Report | [Create an Issue](https://github.com/SanthoshRubanF/Phonepe-Pulse-Data-Visualization-and-Exploration/issues) |
| 💡 Feature Request | [Discussions](https://github.com/SanthoshRubanF/Phonepe-Pulse-Data-Visualization-and-Exploration/discussions) |
| 📚 Documentation | Check [README.md](README.md) and inline code comments |
| 💬 General Help | Create a GitHub Issue with `[HELP]` prefix |

## 🔄 Version History

### v2.0.0 (Released)
**Major Refactoring - Production Ready**
- ✅ Complete rewrite with modular architecture (monolithic → 8 modules)
- ✅ Enhanced UI design matching PhonePe Pulse aesthetic
- ✅ Full geographic coverage: All 36 states + India aggregate
- ✅ Complete data loading: Country + state level (23,600+ rows)
- ✅ Fixed state name extraction (Windows path separator issues)
- ✅ Theme-aware responsive design (light/dark mode)
- ✅ Comprehensive error handling and validation
- ✅ Type hints throughout codebase
- ✅ Professional documentation
- ✅ Session-based data caching for performance
- ✅ Modular visualization system (8+ chart types)

### v1.0.0 (Initial Release)
- Basic dashboard implementation
- Transaction and insurance analysis
- Simple state filtering

---

## 📈 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Lines of Code** | 5,500+ |
| **Python Files** | 8 |
| **Visualization Types** | 8+ |
| **Analysis Options** | 14+ |
| **States/UTs Covered** | 37 (36 + India) |
| **Years of Data** | 7 (2018-2024) |
| **Total Data Rows** | 23,600+ |
| **Code Coverage** | Full type hints |

---

**Built with ❤️ using Python, Streamlit, and Plotly**

**Last Updated:** January 2025 | **Status:** Production Ready ✅



