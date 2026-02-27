# 🏎️ Formula 1 Dashboard

A production-ready real-time Formula 1 dashboard application that provides live F1 race data, driver standings, constructor standings, and race schedules. Built with Python and Streamlit, this interactive web application fetches data from the Ergast F1 API and presents it in a modern, user-friendly interface.

![F1 Dashboard](https://img.shields.io/badge/F1-Dashboard-E10600?style=for-the-badge&logo=formula1)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)

## ✨ Features

- **📊 Race Overview**: View next scheduled race details and latest race results
- **🏎️ Driver Standings**: Complete driver championship standings with interactive charts
- **👤 Driver Profiles**: Detailed driver statistics, race results, and performance analysis (click driver names in standings)
- **🏁 Constructor Standings**: Team championship standings with visual comparisons
- **🏢 Team Profiles**: Comprehensive team statistics, driver lineups, and race performance (click team names in standings)
- **🏁 All Races**: View complete race calendar and results for any season
- **� Historical Data**: Access F1 data from 1950 to present (select season in sidebar)
- **🔄 Auto-Refresh**: Automatic data refresh every 60 seconds (current season only)
- **📈 Interactive Charts**: Plotly-powered visualizations with hover details
- **🎨 F1-Themed Design**: Professional styling with Formula 1 colors
- **⚡ Performance Optimized**: Smart caching for fast load times
- **🛡️ Error Handling**: Graceful handling of API failures and edge cases
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for API access)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd f1-dashboard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

4. Open your browser and navigate to:
```
http://localhost:8501
```

## 📦 Dependencies

- **streamlit** (>=1.28.0): Web application framework
- **pandas** (>=2.0.0): Data manipulation and analysis
- **plotly** (>=5.17.0): Interactive charts and visualizations
- **requests** (>=2.31.0): HTTP library for API calls

All dependencies are listed in `requirements.txt`.

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Web Application                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Overview   │  │   Drivers    │  │ Constructors │      │
│  │     Page     │  │   Standings  │  │  Standings   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    UI Components Layer                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Metrics  │ │  Tables  │ │  Charts  │ │ Spinners │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
├─────────────────────────────────────────────────────────────┤
│                   Business Logic Layer                       │
│  ┌──────────────────────────────────────────────────┐      │
│  │  Data Processing & Transformation Functions      │      │
│  └──────────────────────────────────────────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                   Data Access Layer                          │
│  ┌──────────────────────────────────────────────────┐      │
│  │  API Client with Caching (@st.cache_data)        │      │
│  └──────────────────────────────────────────────────┘      │
├─────────────────────────────────────────────────────────────┤
│                    External Services                         │
│  ┌──────────────────────────────────────────────────┐      │
│  │           Ergast F1 API (HTTP/JSON)              │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### Data Access Layer
- **API Client**: Handles all HTTP requests to Ergast F1 API
- **Caching**: Uses Streamlit's `@st.cache_data` decorator with TTL
- **Error Handling**: Retry logic, timeout handling, graceful degradation

#### Business Logic Layer
- **Data Transformation**: Converts API responses to pandas DataFrames
- **Data Validation**: Ensures data integrity and handles missing values
- **Sorting & Filtering**: Applies F1 championship rules

#### UI Components Layer
- **Metrics Display**: Key statistics using `st.metric()`
- **Data Tables**: Interactive sortable tables
- **Charts**: Plotly horizontal bar charts with F1 theming
- **Loading States**: Spinners and progress indicators

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. Push your code to a GitHub repository

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)

3. Sign in with your GitHub account

4. Click "New app" and select your repository

5. Configure the deployment:
   - **Main file path**: `app.py`
   - **Python version**: 3.8+
   - **Branch**: main (or your default branch)

6. Click "Deploy"

Your app will be live at: `https://your-app-name.streamlit.app`

### Local Development

For local development with auto-reload:

```bash
streamlit run app.py --server.runOnSave true
```

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t f1-dashboard .
docker run -p 8501:8501 f1-dashboard
```

## ⚙️ Configuration

### Environment Variables

The application uses the following default configuration:

- **ERGAST_API_BASE_URL**: `http://ergast.com/api/f1` (Ergast F1 API base URL)
- **REQUEST_TIMEOUT**: 10 seconds
- **MAX_RETRIES**: 3 attempts
- **CACHE_TTL_RACE_DATA**: 300 seconds (5 minutes)
- **CACHE_TTL_NEXT_RACE**: 3600 seconds (1 hour)
- **AUTO_REFRESH_INTERVAL**: 60 seconds

These can be modified in the `app.py` file if needed.

### Streamlit Configuration

Create a `.streamlit/config.toml` file for custom Streamlit settings:

```toml
[theme]
primaryColor = "#E10600"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
```

## 📊 Data Source

This application uses the [Ergast F1 API](http://ergast.com/mrd/), a free and open API providing Formula 1 data since 1950.

**API Endpoints Used:**
- `/current/last/results.json` - Latest race results
- `/current/driverStandings.json` - Current driver standings
- `/current/constructorStandings.json` - Current constructor standings
- `/current/next.json` - Next scheduled race

**Rate Limits**: The Ergast API has a rate limit of 4 requests per second and 200 requests per hour per IP address. This application's caching strategy ensures compliance with these limits.

## 🎯 Features in Detail

### Driver & Team Profile Pages
Click on any driver name in the Driver Standings or team name in the Constructor Standings to view detailed profile pages featuring:

**Driver Profiles:**
- Personal information (name, number, nationality, date of birth)
- Season statistics (races, wins, podiums, points, poles, fastest laps, DNFs, average finish)
- Current championship position
- Complete race-by-race results table
- Points scored per race visualization
- Finishing positions trend chart

**Team Profiles:**
- Team information (name, nationality)
- Current driver lineup
- Season statistics (races, wins, podiums, points, 1-2 finishes, DNFs)
- Current championship position
- Race-by-race results with driver performance
- Points scored per race visualization

### Auto-Refresh
The dashboard automatically refreshes every 60 seconds to ensure you always see the latest data. The current tab/page is preserved during refresh, and a countdown timer shows when the next refresh will occur.

### Caching Strategy
- **Race Results**: Cached for 5 minutes (updates after race completion)
- **Driver Standings**: Cached for 5 minutes (updates after each race)
- **Constructor Standings**: Cached for 5 minutes (updates after each race)
- **Next Race**: Cached for 1 hour (changes infrequently)
- **Profile Data**: Cached for 5 minutes (driver/team details and race results)

### Error Handling
The application gracefully handles:
- Network timeouts
- API server errors (5xx)
- Client errors (4xx)
- Invalid JSON responses
- Empty or null data
- Rate limiting

## 🧪 Testing

The application includes comprehensive error handling and has been tested for:
- API failure scenarios
- Empty/null responses
- Network timeouts
- Data validation
- Cache behavior
- Auto-refresh functionality
- Responsive design

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [Ergast F1 API](http://ergast.com/mrd/) for providing comprehensive Formula 1 data
- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Plotly](https://plotly.com/) for interactive visualizations
- Formula 1 fans worldwide 🏎️

## 📧 Contact

For questions, suggestions, or issues, please open an issue on GitHub.

---

**Enjoy the dashboard and happy racing! 🏁**
