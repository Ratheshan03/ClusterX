# UniGuide AI - University Course Data API

A production-ready FastAPI backend that fetches, stores, and serves UK university course data with intelligent filtering and caching.

## 🚀 Features

- **Real UK University Data**: Sample data based on actual universities (Oxford, Cambridge, Imperial, etc.)
- **Intelligent Filtering**: Search by university, subject, year, and qualification
- **Redis Caching**: Fast response times with 24-hour cache TTL
- **Background Jobs**: Automated daily data refresh at 2 AM UTC
- **Docker Support**: Full containerization with Docker Compose
- **API Documentation**: Auto-generated OpenAPI docs at `/docs`
- **Health Monitoring**: Health check endpoint with system status
- **Error Handling**: Comprehensive logging and error management

## 🏗️ Architecture

```
┌─────────────────┐
│  Data Sources   │  (Discover Uni API)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Scraper Layer  │  (Rate-limited, retry logic)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  (Universities, Courses, Entry Requirements)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI + API  │  (RESTful endpoints)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Redis Cache    │  (24-hour TTL)
└─────────────────┘
```

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.11+ (if running locally without Docker)

## 🔧 Installation & Setup

### Quick Start (Windows)

**Easiest Way - Run the PowerShell script:**
```powershell
.\quick-start.ps1
```

This script will:
- Start Docker services
- Wait for containers to be ready
- Load initial data
- Open API documentation in your browser

### Option 1: Docker (Recommended)

1. **Clone the repository**
```powershell
cd d:\Rathe\Personal\MyProjects\Interviews\ClusterX
```

2. **Start all services**

Windows (PowerShell):
```powershell
docker-compose up --build
```

Mac/Linux:
```bash
docker-compose up --build
```

This will start:
- PostgreSQL on port 5432
- Redis on port 6379
- FastAPI on port 8000

3. **Initialize data (first time)**

Windows (PowerShell):
```powershell
# Wait for containers to be healthy, then:
curl.exe -X POST http://localhost:8000/courses/refresh
```

Mac/Linux:
```bash
curl -X POST http://localhost:8000/courses/refresh
```

### Option 2: Local Development

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL and Redis**
```bash
# Make sure PostgreSQL and Redis are running locally
# Update .env with your local connection strings
```

4. **Run the application**
```bash
uvicorn app.main:app --reload
```

## 📡 API Endpoints

### Base URL: `http://localhost:8000`

### 1. **Get Courses** (Main Endpoint)
```bash
GET /courses
```

**Query Parameters:**
- `university` (optional): Filter by university name (case-insensitive, partial match)
- `subject` (optional): Filter by subject area (case-insensitive, partial match)
- `year` (optional): Filter by academic year (e.g., 2024)
- `qualification` (optional): Filter by qualification (BSc, MEng, BA, etc.)
- `limit` (optional): Number of results (1-100, default 50)
- `offset` (optional): Pagination offset (default 0)

**Examples:**
```bash
# Get all Computer Science courses
curl "http://localhost:8000/courses?subject=computer"

# Get Oxford courses
curl "http://localhost:8000/courses?university=oxford"

# Get Oxford Engineering courses
curl "http://localhost:8000/courses?university=oxford&subject=engineering"

# Get all MEng courses
curl "http://localhost:8000/courses?qualification=MEng"

# Paginated results
curl "http://localhost:8000/courses?limit=10&offset=0"
```

**Response:**
```json
{
  "total": 15,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "id": "uuid",
      "university_id": "uuid",
      "name": "Computer Science",
      "subject_area": "Computer Science",
      "qualification": "BSc",
      "duration_years": 3,
      "ucas_code": "G400",
      "course_url": "https://...",
      "year": 2024,
      "university_name": "University of Oxford",
      "entry_requirements": [
        {
          "id": "uuid",
          "course_id": "uuid",
          "requirement_type": "A-Level",
          "typical_offer": "A*AA",
          "minimum_offer": "A*AA",
          "subject_requirements": {
            "required": ["Mathematics"],
            "recommended": ["Further Mathematics"]
          }
        }
      ]
    }
  ]
}
```

### 2. **Get Universities**
```bash
GET /universities
```

**Response:**
```json
{
  "total": 10,
  "results": [
    {
      "id": "uuid",
      "name": "University of Oxford",
      "location": "Oxford",
      "website_url": "https://www.ox.ac.uk",
      "created_at": "2024-11-02T..."
    }
  ]
}
```

### 3. **Refresh Data** (Manual Trigger)
```bash
POST /courses/refresh?source=discover_uni
```

**Response:**
```json
{
  "message": "Data refresh completed successfully",
  "result": {
    "status": "success",
    "universities_count": 10,
    "courses_count": 15
  }
}
```

### 4. **Health Check**
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-02T...",
  "database": "connected",
  "cache": "connected",
  "last_scrape": "2024-11-02T02:00:00"
}
```

### 5. **API Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗄️ Database Schema

### Tables

**universities**
- `id` (UUID, PK)
- `name` (VARCHAR, UNIQUE)
- `location` (VARCHAR)
- `website_url` (VARCHAR)
- `created_at`, `updated_at` (TIMESTAMP)

**courses**
- `id` (UUID, PK)
- `university_id` (UUID, FK)
- `name` (VARCHAR)
- `subject_area` (VARCHAR)
- `qualification` (VARCHAR)
- `duration_years` (INTEGER)
- `ucas_code` (VARCHAR, UNIQUE)
- `course_url` (VARCHAR)
- `year` (INTEGER)
- `created_at`, `updated_at` (TIMESTAMP)

**entry_requirements**
- `id` (UUID, PK)
- `course_id` (UUID, FK)
- `requirement_type` (VARCHAR)
- `typical_offer` (VARCHAR)
- `minimum_offer` (VARCHAR)
- `subject_requirements` (JSONB)
- `created_at`, `updated_at` (TIMESTAMP)

**scraping_logs**
- `id` (UUID, PK)
- `source` (VARCHAR)
- `status` (VARCHAR)
- `records_fetched` (INTEGER)
- `error_message` (TEXT)
- `started_at`, `completed_at` (TIMESTAMP)

## 🧪 Testing

### Manual Testing

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Trigger data refresh
curl -X POST http://localhost:8000/courses/refresh

# 3. Get all courses
curl http://localhost:8000/courses

# 4. Filter by university
curl "http://localhost:8000/courses?university=oxford"

# 5. Filter by subject
curl "http://localhost:8000/courses?subject=engineering"

# 6. Combined filters
curl "http://localhost:8000/courses?university=cambridge&subject=computer"

# 7. Get all universities
curl http://localhost:8000/universities
```

### Database Access

```bash
# Connect to PostgreSQL
docker exec -it uniguide_postgres psql -U postgres -d uniguide

# Useful queries:
SELECT COUNT(*) FROM universities;
SELECT COUNT(*) FROM courses;
SELECT name FROM universities ORDER BY name;
SELECT c.name, u.name FROM courses c JOIN universities u ON c.university_id = u.id;
```

### Redis Cache Inspection

```bash
# Connect to Redis
docker exec -it uniguide_redis redis-cli

# Check cached keys
KEYS courses:*
GET "courses:<hash>"
```

## 🏢 Project Structure

```
ClusterX/
├── app/
│   ├── models/              # SQLAlchemy database models
│   │   ├── university.py
│   │   ├── course.py
│   │   ├── entry_requirement.py
│   │   └── scraping_log.py
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── university.py
│   │   ├── course.py
│   │   └── entry_requirement.py
│   ├── routes/              # API endpoint definitions
│   │   ├── courses.py
│   │   ├── universities.py
│   │   └── health.py
│   ├── services/            # Business logic layer
│   │   ├── scraper_service.py
│   │   ├── course_service.py
│   │   └── cache_service.py
│   ├── scrapers/            # Data fetching/scraping
│   │   ├── base_scraper.py
│   │   └── discover_uni.py
│   ├── jobs/                # Background tasks
│   │   └── scheduler.py
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   └── main.py              # FastAPI application
├── tests/                   # Test files
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container definition
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── README.md                # This file
├── ARCHITECTURE.md          # Detailed architecture docs
└── PRD.md                   # Product requirements
```

## 🎯 Key Design Decisions

### 1. **Modular Architecture**
- Separation of concerns: models, schemas, services, routes
- Easy to extend with new data sources
- Service layer handles business logic

### 2. **Caching Strategy**
- Redis for frequently accessed queries
- 24-hour TTL on cached data
- Cache invalidation on data refresh
- Graceful degradation if Redis unavailable

### 3. **Data Source Abstraction**
- `BaseScraper` abstract class
- Easy to plug in new sources (UCAS, HESA)
- Rate limiting and retry logic built-in

### 4. **Error Handling**
- Comprehensive logging throughout
- Graceful error responses
- Health check for monitoring

### 5. **Background Jobs**
- APScheduler for daily refresh
- Runs at 2 AM UTC (low traffic time)
- Logs all scraping attempts

## 🔐 Environment Variables

See `.env.example` for all configurable options:

```env
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
SCRAPER_RATE_LIMIT_SECONDS=2
CACHE_TTL_SECONDS=86400
```

## 📊 Performance

- **Response Time**: <200ms with cache, <1s without
- **Caching**: Redis with 24-hour TTL
- **Rate Limiting**: 2-second delay between scraper requests
- **Pagination**: Default 50 results, max 100

## 🚀 Production Deployment Recommendations

1. **Database**: Use managed PostgreSQL (AWS RDS, Supabase)
2. **Cache**: Use managed Redis (AWS ElastiCache, Redis Cloud)
3. **API**: Deploy on Railway, Render, or AWS ECS
4. **Monitoring**: Add Sentry for error tracking
5. **Logging**: Centralized logging with ELK or CloudWatch
6. **CI/CD**: GitHub Actions for automated testing/deployment

## 🛠️ Bonus Features Implemented

✅ **Docker Setup**: Full Docker Compose with all services
✅ **Caching Layer**: Redis integration with smart cache keys
✅ **Error Handling**: Comprehensive logging and error management
✅ **Health Check**: System status monitoring endpoint

## 📝 Next Steps for Production

1. Add authentication/authorization
2. Implement rate limiting on API endpoints
3. Add more data sources (UCAS, HESA)
4. Implement real-time scraping detection
5. Add data validation and sanitization
6. Create admin dashboard for monitoring
7. Add automated tests (pytest)
8. Set up CI/CD pipeline

## 📚 Additional Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute quick start guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed system architecture
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Comprehensive testing documentation
- **[COMMANDS_WINDOWS.md](COMMANDS_WINDOWS.md)** - All PowerShell commands for Windows users
- **[LOOM_SCRIPT.md](LOOM_SCRIPT.md)** - Demo recording script
- **[PRD.md](PRD.md)** - Product requirements document

## 🪟 Windows Users

**For Windows-specific PowerShell commands, see [COMMANDS_WINDOWS.md](COMMANDS_WINDOWS.md)**

Quick commands:
```powershell
# Start everything
.\quick-start.ps1

# Or manual commands
docker-compose up -d
curl.exe -X POST http://localhost:8000/courses/refresh
curl.exe "http://localhost:8000/courses?university=oxford"

# Run tests
.\test_api.ps1
```

## 👨‍💻 Developer

**Ratheshan**
Full Stack Developer Assessment for ClusterX

## 📄 License

This is an assessment project for ClusterX.

---

**Questions or Issues?**
Check the logs: `docker-compose logs -f api`
