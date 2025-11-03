# UniGuide AI - University Course Data API

A FastAPI backend that fetches, stores, and serves UK university course data with filtering, caching, and background jobs.

## Features

- **UK University Data**: Course information from top UK universities (Oxford, Cambridge, Imperial, UCL, Edinburgh)
- **Smart Filtering**: Search by university, subject, year, and qualification type
- **Fast Performance**: Redis caching for quick responses
- **Auto Refresh**: Daily background job to keep data fresh
- **Docker Ready**: Complete Docker Compose setup
- **API Docs**: Auto-generated interactive documentation at `/docs`

## Tech Stack

- **Backend**: FastAPI + Python
- **Database**: PostgreSQL
- **Cache**: Redis
- **Jobs**: APScheduler
- **Container**: Docker Compose

## Quick Start

### 1. Start the Application

```bash
docker-compose up --build
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI (port 8000)

### 2. Load Sample Data

```bash
curl -X POST http://localhost:8000/courses/refresh
```

This loads 5 universities with 5 courses into the database.

### 3. Test the API

```bash
# Get all courses
curl http://localhost:8000/courses

# Filter by university
curl "http://localhost:8000/courses?university=oxford"

# Filter by subject
curl "http://localhost:8000/courses?subject=computer"
```

### 4. View API Documentation

Open your browser: http://localhost:8000/docs

You can test all endpoints interactively from Swagger UI.

## API Endpoints

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | System health check |
| GET | `/universities` | List all universities |
| GET | `/courses` | Query courses with filters |
| POST | `/courses/refresh` | Manually refresh data |
| GET | `/docs` | Interactive API documentation |

### Query Parameters for `/courses`

- `university` - Filter by university name (partial match)
- `subject` - Filter by subject area (partial match)
- `year` - Filter by academic year (e.g., 2024)
- `qualification` - Filter by degree type (BSc, MEng, BA, etc.)
- `limit` - Results per page (1-100, default: 50)
- `offset` - Pagination offset (default: 0)

### Examples

```bash
# All courses
curl http://localhost:8000/courses

# Oxford courses
curl "http://localhost:8000/courses?university=oxford"

# Computer Science courses
curl "http://localhost:8000/courses?subject=computer"

# Cambridge Engineering
curl "http://localhost:8000/courses?university=cambridge&subject=engineering"

# MEng degrees
curl "http://localhost:8000/courses?qualification=MEng"

# Paginated results
curl "http://localhost:8000/courses?limit=10&offset=0"
```

## Response Format

```json
{
  "total": 5,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "id": "uuid",
      "university_name": "University of Oxford",
      "name": "Computer Science",
      "subject_area": "Computer Science",
      "qualification": "BA",
      "duration_years": 3,
      "ucas_code": "G400",
      "year": 2024,
      "entry_requirements": [
        {
          "requirement_type": "A-Level",
          "typical_offer": "A*AA",
          "subject_requirements": {
            "required": ["Mathematics"]
          }
        }
      ]
    }
  ]
}
```

## Project Structure

```
ClusterX/
├── app/
│   ├── models/              # Database models
│   ├── schemas/             # API schemas
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── scrapers/            # Data fetchers
│   ├── jobs/                # Background tasks
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   └── main.py              # FastAPI app
├── tests/
│   └── test_api.py          # API tests
├── docker-compose.yml       # Docker setup
├── Dockerfile               # Container config
├── requirements.txt         # Dependencies
└── README.md                # This file
```

## Database Schema

### Tables

**universities**
- id, name, location, website_url

**courses**
- id, university_id, name, subject_area, qualification, ucas_code, year

**entry_requirements**
- id, course_id, requirement_type, typical_offer, subject_requirements

**scraping_logs**
- id, source, status, records_fetched, started_at, completed_at

## Development

### Running Locally (Without Docker)

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up PostgreSQL and Redis**
```bash
# Update .env with local connection strings
DATABASE_URL=postgresql://user:pass@localhost:5432/uniguide
REDIS_URL=redis://localhost:6379/0
```

3. **Run the application**
```bash
uvicorn app.main:app --reload
```

### Running Tests

```bash
pytest tests/
```

## Configuration

Environment variables (see `.env.example`):

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/uniguide
REDIS_URL=redis://redis:6379/0
SCRAPER_RATE_LIMIT_SECONDS=2
CACHE_TTL_SECONDS=86400
REFRESH_DATA_CRON=0 2 * * *
```

## Features Implemented

### Core Requirements
- ✅ FastAPI backend
- ✅ UK university course data scraping
- ✅ PostgreSQL database storage
- ✅ API endpoints with filtering
- ✅ Background job for daily refresh

### Bonus Features
- ✅ **Docker Setup**: Complete Docker Compose configuration
- ✅ **Redis Caching**: Fast query responses with 24-hour TTL
- ✅ **Error Handling**: Comprehensive logging and graceful degradation

## How It Works

### Data Flow

1. **Data Collection**: Scraper fetches UK university course data
2. **Storage**: Data saved to PostgreSQL with proper relationships
3. **API Query**: Client requests courses with filters
4. **Caching**: Check Redis cache first, then database if needed
5. **Response**: Return filtered results as JSON

### Background Jobs

- Runs daily at 2 AM UTC
- Refreshes all course data
- Clears cache after refresh
- Logs all operations

### Caching Strategy

- Cache key: MD5 hash of query parameters
- TTL: 24 hours
- Automatic invalidation on data refresh
- Graceful degradation if Redis unavailable

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "last_scrape": "2024-11-03T02:00:00Z"
}
```

### Logs

```bash
# View API logs
docker-compose logs -f api

# View all logs
docker-compose logs
```

## Stopping the Application

```bash
# Stop containers
docker-compose down

# Stop and remove data
docker-compose down -v
```

## Architecture

For detailed architecture documentation, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Sample Data

The system includes sample data for 5 UK universities:
- University of Oxford
- University of Cambridge
- Imperial College London
- University College London
- University of Edinburgh

Each with Computer Science courses and realistic entry requirements (A-Level grades, IB points).

## Production Deployment

Recommended setup:
- **Database**: Managed PostgreSQL (AWS RDS, Supabase)
- **Cache**: Managed Redis (ElastiCache, Redis Cloud)
- **API**: Container platform (Railway, Render, AWS ECS)
- **Monitoring**: Health checks, error tracking (Sentry)

## Future Enhancements

- Add more data sources (UCAS, HESA)
- Implement API authentication
- Add rate limiting
- Create admin dashboard
- Add automated tests
- Set up CI/CD pipeline

## License

This is an assessment project for ClusterX.

---

**Questions?** Check the logs: `docker-compose logs -f api`
