# Design Document

## System Architecture

### High-Level Architecture

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

### Component Breakdown

#### 1. Data Access Layer
- **API Client Module**: Handles all HTTP requests to Ergast F1 API
- **Caching Strategy**: Streamlit's `@st.cache_data` decorator with TTL
- **Error Handling**: Retry logic, timeout handling, graceful degradation

#### 2. Business Logic Layer
- **Data Transformation**: Convert API responses to pandas DataFrames
- **Data Validation**: Ensure data integrity and handle missing values
- **Sorting & Filtering**: Apply F1 championship rules for standings

#### 3. UI Components Layer
- **Metrics Display**: `st.metric()` for key statistics
- **Data Tables**: Interactive sortable tables with pandas
- **Charts**: Plotly bar charts and line charts
- **Loading States**: Spinners and progress indicators

#### 4. Page Layer
- **Multi-page Navigation**: Tab-based or sidebar navigation
- **Auto-refresh**: 60-second refresh cycle
- **State Management**: Maintain user selections across refreshes

## Data Models

### Race Result
```python
{
    "season": str,
    "round": int,
    "raceName": str,
    "circuit": str,
    "date": str,
    "winner": {
        "driverId": str,
        "givenName": str,
        "familyName": str,
        "constructor": str
    },
    "podium": [
        {
            "position": int,
            "driver": str,
            "constructor": str,
            "points": float
        }
    ]
}
```

### Driver Standing
```python
{
    "position": int,
    "driverId": str,
    "givenName": str,
    "familyName": str,
    "constructor": str,
    "points": float,
    "wins": int
}
```

### Constructor Standing
```python
{
    "position": int,
    "constructorId": str,
    "name": str,
    "points": float,
    "wins": int
}
```

### Next Race
```python
{
    "season": str,
    "round": int,
    "raceName": str,
    "circuit": str,
    "locality": str,
    "country": str,
    "date": str,
    "time": str
}
```

## API Integration

### Ergast F1 API Endpoints

| Endpoint | Purpose | Cache TTL |
|----------|---------|-----------|
| `/current/last/results.json` | Latest race results | 300s (5 min) |
| `/current/driverStandings.json` | Current driver standings | 300s (5 min) |
| `/current/constructorStandings.json` | Constructor standings | 300s (5 min) |
| `/current/next.json` | Next scheduled race | 3600s (1 hour) |

### Error Handling Strategy

```python
def fetch_with_retry(url, max_retries=3, timeout=10):
    """
    Fetch data with retry logic and error handling
    
    Error scenarios:
    - Network timeout: Retry with exponential backoff
    - HTTP 4xx: Return None, show user-friendly message
    - HTTP 5xx: Retry, then fallback
    - JSON decode error: Log and return None
    """
```

## UI Design

### Page Structure

#### Page 1: Overview
```
┌─────────────────────────────────────────────────────────┐
│  🏎️ Formula 1 Dashboard - 2024 Season                   │
├─────────────────────────────────────────────────────────┤
│  Next Race                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Race Name    │  │ Circuit      │  │ Date & Time  │ │
│  │ [Metric]     │  │ [Metric]     │  │ [Metric]     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Latest Race Winner                                     │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Driver       │  │ Team         │                    │
│  │ [Metric]     │  │ [Metric]     │                    │
│  └──────────────┘  └──────────────┘                    │
├─────────────────────────────────────────────────────────┤
│  Podium Finishers                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Pos │ Driver │ Constructor │ Points │           │   │
│  │  1  │  ...   │    ...      │  ...   │           │   │
│  │  2  │  ...   │    ...      │  ...   │           │   │
│  │  3  │  ...   │    ...      │  ...   │           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### Page 2: Driver Standings
```
┌─────────────────────────────────────────────────────────┐
│  Driver Championship Standings                          │
├─────────────────────────────────────────────────────────┤
│  Top 10 Drivers - Points Comparison                     │
│  ┌─────────────────────────────────────────────────┐   │
│  │         [Plotly Bar Chart]                      │   │
│  │  Driver names on Y-axis, Points on X-axis      │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  Full Standings Table (Sortable)                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Pos │ Driver │ Team │ Points │ Wins │           │   │
│  │  1  │  ...   │ ...  │  ...   │ ...  │           │   │
│  │  2  │  ...   │ ...  │  ...   │ ...  │           │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  Driver Comparison                                      │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Select       │  │ Select       │                    │
│  │ Driver 1     │  │ Driver 2     │                    │
│  └──────────────┘  └──────────────┘                    │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Points: XXX  │  │ Points: XXX  │                    │
│  │ Wins: X      │  │ Wins: X      │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

#### Page 3: Constructor Standings
```
┌─────────────────────────────────────────────────────────┐
│  Constructor Championship Standings                     │
├─────────────────────────────────────────────────────────┤
│  Constructor Points Comparison                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │         [Plotly Bar Chart]                      │   │
│  │  Team names on Y-axis, Points on X-axis        │   │
│  └─────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────┤
│  Full Constructor Standings (Sortable)                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Pos │ Constructor │ Points │ Wins │             │   │
│  │  1  │    ...      │  ...   │ ...  │             │   │
│  │  2  │    ...      │  ...   │ ...  │             │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Technical Implementation Details

### File Structure
```
f1-dashboard/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # Deployment instructions
└── .streamlit/
    └── config.toml       # Streamlit configuration (optional)
```

### Core Functions

#### Data Fetching Functions
```python
@st.cache_data(ttl=300)
def fetch_latest_race():
    """Fetch latest race results from Ergast API"""
    
@st.cache_data(ttl=300)
def fetch_driver_standings():
    """Fetch current driver championship standings"""
    
@st.cache_data(ttl=300)
def fetch_constructor_standings():
    """Fetch current constructor championship standings"""
    
@st.cache_data(ttl=3600)
def fetch_next_race():
    """Fetch next scheduled race details"""
```

#### UI Rendering Functions
```python
def render_overview_page():
    """Render the overview page with next race and latest results"""
    
def render_driver_standings_page():
    """Render driver standings with table and chart"""
    
def render_constructor_standings_page():
    """Render constructor standings with table and chart"""
    
def render_driver_comparison(driver1, driver2):
    """Render side-by-side driver comparison"""
```

#### Helper Functions
```python
def create_bar_chart(data, x_col, y_col, title):
    """Create Plotly horizontal bar chart"""
    
def format_driver_name(given_name, family_name):
    """Format driver name for display"""
    
def handle_api_error(error):
    """Display user-friendly error message"""
```

### Caching Strategy

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Race Results | 5 minutes | Updates after race completion |
| Driver Standings | 5 minutes | Updates after each race |
| Constructor Standings | 5 minutes | Updates after each race |
| Next Race | 1 hour | Changes infrequently |

### Auto-Refresh Implementation

```python
# Use Streamlit's experimental_rerun with time-based trigger
import time

# Store last refresh time in session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

# Check if 60 seconds have elapsed
if time.time() - st.session_state.last_refresh > 60:
    st.session_state.last_refresh = time.time()
    st.rerun()
```

## Performance Optimization

### Strategies
1. **Minimize API Calls**: Use caching with appropriate TTL
2. **Lazy Loading**: Load data only when page is accessed
3. **Efficient Data Structures**: Use pandas for fast data manipulation
4. **Chart Optimization**: Limit chart data points for faster rendering

### Expected Performance
- Initial page load: < 2 seconds
- Cached page load: < 0.5 seconds
- Auto-refresh: < 1 second (cached data)

## Deployment Configuration

### requirements.txt
```
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.17.0
requests>=2.31.0
```

### Streamlit Cloud Deployment
1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Configure Python version (3.8+)
4. Deploy with one click

### Environment Variables
- `ERGAST_API_BASE_URL`: Base URL for Ergast API (default: http://ergast.com/api/f1)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)

## Error Handling & Edge Cases

### Scenarios
1. **API Unavailable**: Display cached data with warning message
2. **No Upcoming Race**: Show "Season Complete" or "Off-season" message
3. **Incomplete Data**: Handle missing fields gracefully
4. **Network Timeout**: Retry with exponential backoff
5. **Invalid JSON**: Log error and show user-friendly message

## Testing Strategy

### Unit Tests
- Test each fetch function with mocked API responses
- Test data transformation functions
- Test error handling logic

### Integration Tests
- Test full data flow from API to UI
- Test caching behavior
- Test auto-refresh functionality

### Property-Based Tests
- Verify standings order correctness (CP2)
- Verify cache consistency (CP3)
- Verify error handling completeness (CP4)

## Security Considerations

- No authentication required (public API)
- No sensitive data storage
- Input validation for user selections
- Rate limiting awareness (Ergast API limits)

## Future Enhancements

### Bonus Features
1. **Dark Theme Support**: Use Streamlit theme configuration
2. **Team Filter**: Dropdown to filter drivers by team
3. **Championship Progression**: Line chart showing points over season
4. **Historical Data**: View past seasons
5. **Race Calendar**: Full season schedule with countdown timers

### Implementation Priority
1. Core features (US1-US7) - High priority
2. Driver comparison (US5) - High priority
3. Championship progression (US8) - Medium priority
4. Dark theme - Low priority
5. Team filter - Low priority

## Accessibility

- Use semantic HTML through Streamlit components
- Ensure sufficient color contrast
- Provide text alternatives for charts
- Keyboard navigation support (built into Streamlit)

## Monitoring & Logging

- Log API request failures
- Track cache hit/miss rates
- Monitor page load times
- Log user interactions (page views, comparisons)

## Conclusion

This design provides a robust, scalable, and maintainable architecture for the Formula 1 dashboard. The modular structure allows for easy testing, future enhancements, and deployment to production environments.