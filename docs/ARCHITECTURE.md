# UniGuide AI - System Architecture

## Overview

UniGuide AI is designed as a modular, scalable system for collecting, storing, and serving UK university course data. The architecture follows clean code principles with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Data Sources                     │
│  • Discover Uni (Official UK Gov Data)                          │
│  • UCAS Course Search (Future)                                  │
│  • HESA Open Data (Future)                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/API Calls
                             │ Rate Limited (2s delay)
                             │ Retry Logic (3 attempts)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Scraper Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ BaseScraper  │  │ DiscoverUni  │  │  Future      │         │
│  │  (Abstract)  │◄─┤   Scraper    │  │  Scrapers    │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  • Data validation                                              │
│  • Transformation to common format                              │
│  • Error handling                                               │
└────────────────────────────┬────────────────────────────────────┘
                             │ Parsed Data
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Scraper    │  │    Course    │  │    Cache     │         │
│  │   Service    │  │   Service    │  │   Service    │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                 │
│         │ Store Data       │ Query Data       │ Cache/Retrieve  │
│         ▼                  ▼                  ▼                 │
└─────────────────────────────────────────────────────────────────┘
                             │
            ┌────────────────┴────────────────┐
            ▼                                  ▼
┌───────────────────────┐           ┌───────────────────────┐
│     PostgreSQL        │           │        Redis          │
│  ┌─────────────────┐  │           │  ┌─────────────────┐  │
│  │  universities   │  │           │  │  Query Cache    │  │
│  │  courses        │  │           │  │  TTL: 24h       │  │
│  │  entry_reqs     │  │           │  └─────────────────┘  │
│  │  scraping_logs  │  │           └───────────────────────┘
│  └─────────────────┘  │
└───────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   /courses   │  │/universities │  │   /health    │         │
│  │   • GET      │  │   • GET      │  │   • GET      │         │
│  │   • Filters  │  │              │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐                                              │
│  │/courses/     │                                              │
│  │  refresh     │                                              │
│  │   • POST     │                                              │
│  └──────────────┘                                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │ JSON Responses
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Background Jobs (APScheduler)                 │
│  • Daily refresh at 2 AM UTC                                    │
│  • Retry failed scrapes                                         │
│  • Log execution status                                         │
└─────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Clients                                  │
│  • Frontend Applications                                        │
│  • Mobile Apps                                                  │
│  • Third-party Integrations                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Layer (PostgreSQL)

**Purpose**: Persistent storage for all university and course data

**Tables**:
- `universities`: University information (name, location, website)
- `courses`: Course details (name, subject, UCAS code, year)
- `entry_requirements`: Admission requirements per course
- `scraping_logs`: Audit trail of data fetching operations

**Key Features**:
- UUID primary keys for distributed system compatibility
- Indexed columns for fast queries (university_id, subject_area, year)
- JSONB for flexible requirement data structure
- Timestamps for tracking data freshness

### 2. Cache Layer (Redis)

**Purpose**: Reduce database load and improve response times

**Strategy**:
- Cache key format: `courses:<md5_hash_of_params>`
- TTL: 24 hours (aligned with daily refresh cycle)
- Invalidation: Cleared on data refresh
- Graceful degradation: API works without cache

**Cache Keys**:
```
courses:a1b2c3d4...  → GET /courses?university=oxford
courses:e5f6g7h8...  → GET /courses?subject=engineering
universities:all     → GET /universities
```

### 3. Scraper Layer

**Purpose**: Fetch and normalize data from external sources

**Abstract Base Class** (`BaseScraper`):
```python
class BaseScraper(ABC):
    - _rate_limit_wait()       # Ensures delays between requests
    - fetch_data()             # Abstract: Fetch raw data
    - parse_data()             # Abstract: Transform to common format
```

**Concrete Implementation** (`DiscoverUniScraper`):
- Fetches data from Discover Uni API
- Currently uses sample data (15 courses from top UK universities)
- Normalizes to common schema
- In production: Would connect to actual API

**Design Benefits**:
- Easy to add new sources (UCAS, HESA)
- Consistent data format across sources
- Built-in rate limiting and error handling

### 4. Service Layer

**Purpose**: Business logic and orchestration

**ScraperService**:
- Orchestrates data fetching and storage
- Handles database transactions
- Upserts (insert/update) universities and courses
- Logs scraping operations
- Clears cache after refresh

**CourseService**:
- Builds complex queries with filters
- Handles pagination
- Generates cache keys
- Returns enriched course data with university names

**CacheService**:
- Abstracts Redis operations
- Handles connection failures gracefully
- JSON serialization/deserialization
- Pattern-based cache clearing

### 5. API Layer (FastAPI)

**Purpose**: RESTful HTTP interface

**Endpoints**:

1. `GET /courses` - Main query endpoint
   - Query params: university, subject, year, qualification, limit, offset
   - Returns paginated results with total count
   - Cached responses

2. `GET /universities` - List all universities
   - Returns all universities ordered by name

3. `POST /courses/refresh` - Manual data refresh
   - Triggers scraping job
   - Returns job status

4. `GET /health` - System health
   - Checks database, cache, last scrape
   - Used for monitoring/alerting

**Features**:
- Auto-generated OpenAPI docs (`/docs`)
- CORS enabled for frontend integration
- Pydantic validation
- Error handling middleware

### 6. Background Jobs (APScheduler)

**Purpose**: Automated data refresh

**Schedule**:
- Daily at 2 AM UTC (low traffic time)
- Configurable via environment variable

**Job Workflow**:
1. Create scraping log (status: in_progress)
2. Fetch data from source
3. Parse and validate
4. Upsert to database
5. Update log (status: success/failed)
6. Clear cache

**Error Handling**:
- Failed jobs logged with error message
- Doesn't crash the main API
- Can be manually triggered via API

## Data Flow

### Scenario 1: Initial Data Load

```
1. Admin calls POST /courses/refresh
2. ScraperService.refresh_data()
3. DiscoverUniScraper.fetch_data()
4. Parse raw data into structured format
5. For each university:
   - Upsert into universities table
6. For each course:
   - Upsert into courses table
   - Insert entry_requirements
7. Log success in scraping_logs
8. Clear Redis cache
9. Return success response
```

### Scenario 2: Query with Filters

```
1. Client: GET /courses?university=oxford&subject=engineering
2. CourseService.get_courses()
3. Generate cache key from params
4. Check Redis cache
   - If HIT: Return cached data
   - If MISS: Continue to step 5
5. Build SQL query with filters:
   - JOIN universities ON courses.university_id
   - WHERE university.name ILIKE '%oxford%'
   - AND courses.subject_area ILIKE '%engineering%'
6. Load with entry_requirements (joinedload)
7. Execute query, get total count
8. Transform to Pydantic schemas
9. Cache results in Redis (24h TTL)
10. Return JSON response
```

### Scenario 3: Background Refresh

```
1. Scheduler triggers at 2 AM UTC
2. refresh_data_job()
3. Create new event loop (async in sync context)
4. ScraperService.refresh_data()
5. [Same as Scenario 1, steps 3-8]
6. Close event loop
7. Log completion
```

## Technology Choices

### FastAPI
- **Why**: High performance, auto-generated docs, native async support
- **Alternatives**: Flask, Django REST Framework

### PostgreSQL
- **Why**: ACID compliance, JSONB support, mature ecosystem
- **Alternatives**: MySQL, MongoDB

### Redis
- **Why**: Fast in-memory cache, simple key-value store
- **Alternatives**: Memcached, in-memory Python dict

### SQLAlchemy
- **Why**: ORM abstraction, migration support, type safety
- **Alternatives**: Raw SQL, Tortoise ORM

### APScheduler
- **Why**: Simple, in-process scheduler, cron syntax
- **Alternatives**: Celery, RQ

### Docker Compose
- **Why**: Easy local development, reproducible environment
- **Alternatives**: Kubernetes (overkill for this scale)

## Security Considerations

### Current Implementation
- ✅ Environment variables for secrets
- ✅ SQL injection prevention (ORM parameterization)
- ✅ CORS configuration
- ✅ Input validation (Pydantic)

### Production Enhancements Needed
- ❌ API authentication (JWT tokens)
- ❌ Rate limiting per client
- ❌ HTTPS/TLS encryption
- ❌ Input sanitization for XSS
- ❌ Database connection pooling limits

## Scalability Considerations

### Current Architecture (Single Instance)
- Suitable for: 1,000-10,000 requests/day
- Bottleneck: Database queries
- Mitigation: Redis cache (99% hit rate expected)

### Horizontal Scaling Strategy
1. **API Layer**: Deploy multiple FastAPI instances behind load balancer
2. **Database**: Read replicas for queries, primary for writes
3. **Cache**: Redis Cluster for distributed cache
4. **Background Jobs**: Separate worker instances

### Vertical Scaling Strategy
1. **Database**: Increase PostgreSQL instance size
2. **Cache**: Increase Redis memory
3. **API**: More CPU cores for uvicorn workers

## Monitoring & Observability

### Current Implementation
- ✅ Health check endpoint
- ✅ Scraping logs table
- ✅ Python logging (stdout)

### Production Enhancements
- Metrics: Prometheus + Grafana
- Logging: ELK Stack or CloudWatch
- Tracing: Jaeger or New Relic
- Alerting: PagerDuty for critical failures

## Deployment Architecture

### Local Development
```
Docker Compose
├── PostgreSQL (port 5432)
├── Redis (port 6379)
└── FastAPI (port 8000)
```

### Production Recommendation
```
Load Balancer (Nginx/AWS ALB)
├── FastAPI Instance 1
├── FastAPI Instance 2
└── FastAPI Instance 3
    │
    ├──> PostgreSQL (AWS RDS)
    ├──> Redis (AWS ElastiCache)
    └──> S3 (for logs/backups)
```

## Extension Points

### Adding New Data Source
1. Create new scraper class inheriting `BaseScraper`
2. Implement `fetch_data()` and `parse_data()`
3. Register in `ScraperService`
4. No changes needed to API or database

### Adding New Filters
1. Add query parameter to `get_courses()` route
2. Add filter clause in `CourseService.get_courses()`
3. Update cache key generation
4. No changes to database schema

### Adding New Endpoints
1. Create new router in `app/routes/`
2. Register in `app/main.py`
3. Define Pydantic schemas
4. Implement service logic

## Testing Strategy

### Unit Tests
- Test scrapers: `tests/test_scrapers.py`
- Test services: `tests/test_services.py`
- Test models: `tests/test_models.py`

### Integration Tests
- Test API endpoints: `tests/test_api.py`
- Test database operations
- Test cache functionality

### Load Tests
- Use Locust or Apache JMeter
- Target: 100 req/sec sustained
- Monitor response times and error rates

## Conclusion

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Easy to extend with new sources
- ✅ Production-ready patterns (caching, logging, health checks)
- ✅ Scalable design
- ✅ Well-documented

The modular design allows each component to be developed, tested, and scaled independently while maintaining a cohesive system.
