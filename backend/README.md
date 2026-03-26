# F1 Dashboard Backend API

FastAPI backend for the F1 Dashboard application, providing REST endpoints for historical F1 data, analytics, and WebSocket support for real-time race tracking.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Settings and environment variables
│   ├── routers/                # API route handlers
│   │   ├── __init__.py
│   │   ├── standings.py        # Driver/constructor standings
│   │   ├── races.py            # Race calendar, results, qualifying
│   │   ├── analytics.py        # Analytics endpoints
│   │   ├── live.py             # Live data endpoints
│   │   └── ws.py               # WebSocket endpoints
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── jolpica.py          # Jolpica API client
│   │   ├── openf1.py           # OpenF1 API client
│   │   ├── analytics.py        # Analytics calculations
│   │   └── live.py             # Session mode logic
│   ├── models/                 # Pydantic data models
│   │   ├── __init__.py
│   │   ├── common.py           # Shared models
│   │   ├── standings.py        # Standings models
│   │   ├── races.py            # Race models
│   │   ├── analytics.py        # Analytics models
│   │   └── live.py             # Live data models
│   ├── cache/                  # Redis caching layer
│   │   ├── __init__.py
│   │   └── redis.py            # Redis client and cache decorator
│   ├── middleware/             # Custom middleware
│   │   ├── __init__.py
│   │   └── request_id.py       # Request ID tracking
│   └── utils/                  # Helper functions
│       ├── __init__.py
│       ├── helpers.py          # Data helpers
│       └── formatters.py       # Formatting utilities
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_services/          # Service layer tests
│   ├── test_routers/           # API endpoint tests
│   └── test_analytics_properties.py  # Property-based tests
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md                   # This file
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

4. Start Redis (required for caching):
```bash
docker run -d -p 6379:6379 redis:alpine
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Testing

Run tests with pytest:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run property-based tests:
```bash
pytest tests/test_analytics_properties.py -v
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `REDIS_HOST`: Redis server hostname
- `CORS_ORIGINS`: Allowed frontend origins
- `CACHE_TTL_HISTORICAL`: Cache TTL for historical data (seconds)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Architecture

The backend follows a 4-tier architecture:
1. **Presentation**: FastAPI routers handling HTTP/WebSocket requests
2. **Business Logic**: Service layer with data fetching and analytics
3. **Caching**: Redis layer reducing external API calls by 80%+
4. **External APIs**: Jolpica (historical) and OpenF1 (live) data sources
