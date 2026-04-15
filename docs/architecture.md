# System Architecture

## Overview

Job Bot is a human-in-the-loop job application copilot built with FastAPI, following a modular, service-oriented architecture.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                        │
│                    (Web UI / API Clients)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                              │
│                    (FastAPI Endpoints)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Jobs    │ │Application│ │ Outreach │ │ Tracker  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Services Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Fetchers   │  │   Scoring    │  │ Applications │      │
│  │              │  │              │  │              │      │
│  │ • Greenhouse │  │ • Calculator │  │ • Packet     │      │
│  │ • Lever      │  │ • Filters    │  │ • Autofill   │      │
│  │ • Ashby      │  │ • Normalizer │  │ • Playwright │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Outreach   │  │    Sheets    │  │     LLM      │      │
│  │              │  │              │  │              │      │
│  │ • Generator  │  │ • Sync       │  │ • Client     │      │
│  │ • Contacts   │  │ • Formatter  │  │ • Prompts    │      │
│  │ • Followup   │  │              │  │ • Classifiers│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Models     │  │   Database   │  │   Cache      │      │
│  │              │  │              │  │              │      │
│  │ • Job        │  │ • SQLite     │  │ • In-memory  │      │
│  │ • Application│  │ • Postgres   │  │ • Redis      │      │
│  │ • Contact    │  │              │  │              │      │
│  │ • Outreach   │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   External Integrations                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │Greenhouse│ │  Lever   │ │  Ashby   │ │Google    │        │
│  │   API    │ │   API    │ │   API    │ │  Sheets  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘        │
│  ┌──────────┐ ┌──────────┐                                     │
│  │Anthropic │ │  OpenAI  │                                     │
│  │   API    │ │   API    │                                     │
│  └──────────┘ └──────────┘                                     │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### API Layer
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **CORS Middleware**: Cross-origin resource sharing support

### Services Layer

#### Job Fetching Services
- **Base Fetcher**: Abstract interface for all job fetchers
- **Greenhouse Fetcher**: Integration with Greenhouse ATS
- **Lever Fetcher**: Integration with Lever ATS
- **Ashby Fetcher**: Integration with Ashby ATS
- **Manual Fetcher**: Support for manual company watchlists

#### Scoring Services
- **Calculator**: Priority score calculation based on multiple factors
- **Filters**: Job filtering logic based on user preferences
- **Normalizer**: Job data normalization and deduplication

#### Application Services
- **Packet**: Application packet preparation
- **Autofill**: Browser autofill logic
- **Playwright**: Browser automation integration

#### Outreach Services
- **Generator**: Message draft generation
- **Contacts**: Contact management
- **Followup**: Follow-up task creation

#### Integration Services
- **Sheets Sync**: Google Sheets synchronization
- **Formatter**: Data formatting for external systems

#### LLM Services (Optional)
- **Client**: LLM client wrapper
- **Prompts**: Prompt templates
- **Classifiers**: AI-powered classification

### Data Layer
- **Models**: SQLAlchemy ORM models
- **Database**: SQLite (MVP) / PostgreSQL (Production)
- **Cache**: In-memory caching with Redis support

## Data Flow

### Job Ingestion Flow
1. User triggers job fetch (manual or scheduled)
2. Fetcher services retrieve jobs from ATS sources
3. Jobs are normalized and deduplicated
4. Jobs are filtered based on user preferences
5. Jobs are scored and ranked
6. Jobs are stored in database
7. User reviews and approves/rejects jobs

### Application Flow
1. User selects job from queue
2. Application packet is prepared
3. Browser automation launches application
4. Standard fields are auto-filled
5. User reviews and confirms submission
6. Application status is updated
7. Tracker is synchronized

### Outreach Flow
1. User identifies contact for company
2. Outreach draft is generated
3. User reviews and edits draft
4. User sends message manually
5. Outreach status is tracked
6. Follow-up tasks are created

## Security & Privacy

### Data Protection
- Personal data stored in encrypted database
- Credentials stored in environment variables
- No sensitive data in logs
- Secure credential management

### User Control
- All automated actions require approval
- No automatic submissions
- No automatic messaging
- Explicit consent for all actions

### API Security
- CORS configuration
- Rate limiting
- Input validation
- SQL injection prevention
- XSS protection

## Scalability Considerations

### Current Design (MVP)
- SQLite database
- In-memory caching
- Synchronous job processing
- Single server deployment

### Future Enhancements
- PostgreSQL for production
- Redis for distributed caching
- Async job processing with Celery
- Horizontal scaling with load balancer
- CDN for static assets

## Technology Stack

### Backend
- **Python 3.11+**: Primary programming language
- **FastAPI**: Web framework
- **SQLAlchemy**: ORM
- **Pydantic**: Data validation
- **Alembic**: Database migrations

### Browser Automation
- **Playwright**: Browser automation
- **BeautifulSoup**: HTML parsing

### Integrations
- **Google Sheets API**: Spreadsheet integration
- **Anthropic/OpenAI APIs**: LLM features

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container deployment
- **GitHub Actions**: CI/CD

## Design Patterns

### Repository Pattern
Data access through repository classes for abstraction and testability.

### Service Layer Pattern
Business logic encapsulated in service classes, separate from API and data layers.

### Factory Pattern
Fetcher factory for creating appropriate fetcher instances based on ATS type.

### Strategy Pattern
Different scoring strategies based on user preferences and job characteristics.

## Error Handling

### Exception Hierarchy
- Custom exceptions for different error types
- Consistent error response format
- Proper logging of errors

### External API Errors
- Retry logic with exponential backoff
- Circuit breaker pattern for failing services
- Graceful degradation when services are unavailable

## Monitoring & Observability

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Request/response logging

### Health Checks
- Database connectivity
- External API availability
- Service health status

### Metrics (Future)
- Request latency
- Error rates
- Job processing metrics
- User engagement metrics