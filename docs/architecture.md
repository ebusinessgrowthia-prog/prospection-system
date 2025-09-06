

docs/architecture.md
# Architecture Documentation

## Overview

EBUSINESS AI is a comprehensive prospect automation system designed to find, qualify, and contact e-commerce businesses in French-speaking Europe. This document provides a detailed architectural overview of the system, including components, data flow, and technical decisions.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│    Render      │───▶   Web Service   │
└─────────────────┘    │    Platform     │    │   (FastAPI)     │
                       └─────────────────┘    └─────────────────┘
                              │                       │
                              │              ┌─────────────────┐
                              │              │   Dashboard     │
                              │              │  (Streamlit)    │
                              │              └─────────────────┘
                              │                       │
                              │              ┌─────────────────┐
                              └──────────────│   Background    │
                                            │    Worker       │
                                            └─────────────────┘
```

### Core Components

#### 1. Web Service (FastAPI)
- **Purpose**: Main API server and application entry point
- **Port**: 10000
- **Responsibilities**:
  - REST API endpoints
  - Health checks
  - System statistics
  - Request routing

#### 2. Dashboard (Streamlit)
- **Purpose**: User interface for monitoring and management
- **Port**: 8501
- **Responsibilities**:
  - Real-time metrics display
  - Prospect management
  - Campaign monitoring
  - System configuration

#### 3. Background Worker
- **Purpose**: Scheduled tasks and background processing
- **Technology**: APScheduler
- **Responsibilities**:
  - Prospect searching
  - Email generation
  - Email sending
  - System maintenance

### Data Flow

```
Google Dorks → Scraping → Qualification → Enrichment → Email Generation → Email Sending → Tracking
     │              │             │            │              │              │
     ▼              ▼             ▼            ▼              ▼              ▼
   SerpAPI       Database      Mistral AI    Website       SMTP          Analytics
                               API         Analysis                    Dashboard
```

## Technical Stack

### Backend Technologies

| Component | Technology | Version | Purpose |
|-----------|-------------|---------|---------|
| Web Framework | FastAPI | 0.104.1 | API server and routing |
| ASGI Server | Uvicorn | 0.24.0 | Application server |
| Database | SQLite | Built-in | Data persistence |
| ORM | SQLAlchemy | 2.0.23 | Database abstraction |
| Scheduling | APScheduler | 3.10.4 | Task scheduling |
| HTTP Client | Requests | 2.31.0 | HTTP requests |
| Email | smtplib | Built-in | Email sending |
| Templating | Jinja2 | 3.1.2 | Email templates |

### AI and ML Technologies

| Component | Technology | Version | Purpose |
|-----------|-------------|---------|---------|
| Language Model | Mistral AI | Latest | Email personalization |
| Search API | SerpAPI | Latest | Google Dorks scraping |
| Text Processing | BeautifulSoup | 4.12.2 | Web scraping |
| Data Processing | Pandas | 2.1.4 | Data manipulation |
| Numerical Computing | NumPy | 1.25.2 | Numerical operations |

### Frontend Technologies

| Component | Technology | Version | Purpose |
|-----------|-------------|---------|---------|
| Dashboard | Streamlit | 1.28.0 | User interface |
| Visualization | Plotly | Built-in | Charts and graphs |
| Styling | CSS | 3.0 | Dashboard styling |

### Infrastructure

| Component | Technology | Version | Purpose |
|-----------|-------------|---------|---------|
| Platform | Render | Latest | Cloud deployment |
| Version Control | Git | Latest | Code management |
| CI/CD | GitHub Actions | Latest | Automated deployment |
| Monitoring | Render Metrics | Latest | Performance monitoring |

## Directory Structure

```
ebusiness-ai-prospection/
├── .github/                    # GitHub Actions workflows
│   └── workflows/
│       └── deploy.yml          # Automated deployment
├── src/                        # Source code
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── database.py          # Database operations
│   │   ├── models.py            # Data models
│   │   └── utils.py             # Utility functions
│   ├── scrapers/               # Web scraping modules
│   │   ├── __init__.py
│   │   ├── google_dorks_scraper.py
│   │   ├── email_finder.py
│   │   └── website_analyzer.py
│   ├── processors/             # Data processing
│   │   ├── __init__.py
│   │   ├── prospect_qualifier.py
│   │   ├── mistral_personalizer.py
│   │   └── data_enricher.py
│   ├── email/                  # Email management
│   │   ├── __init__.py
│   │   ├── sender.py
│   │   ├── templates/
│   │   └── tracker.py
│   └── scheduler/              # Task scheduling
│       ├── __init__.py
│       ├── tasks.py
│       └── worker.py
├── dashboard/                  # User interface
│   ├── __init__.py
│   ├── dashboard.py            # Main dashboard
│   ├── pages/                  # Dashboard pages
│   ├── components/             # UI components
│   └── static/                 # Static assets
├── data/                       # Data storage
│   ├── prospects.db            # SQLite database
│   ├── logs/                   # Application logs
│   └── exports/                # Data exports
├── tests/                      # Test suite
│   ├── test_scrapers.py
│   ├── test_processors.py
│   ├── test_email.py
│   └── test_scheduler.py
├── docs/                       # Documentation
│   ├── api.md
│   ├── deployment.md
│   ├── architecture.md
│   └── user_guide.md
├── scripts/                    # Utility scripts
│   ├── setup_database.py
│   ├── migrate_data.py
│   ├── backup.py
│   └── deploy.py
├── .python-version             # Python version
├── requirements.txt            # Dependencies
├── render.yaml                 # Render configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
└── LICENSE                     # MIT License
```

## Database Schema

### Core Tables

#### prospects
```sql
CREATE TABLE prospects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL,
    company VARCHAR(200) NOT NULL,
    email VARCHAR(200),
    sector VARCHAR(100),
    country VARCHAR(100),
    website VARCHAR(500),
    phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'nouveau',
    qualification_score FLOAT DEFAULT 0.0,
    problem_detected TEXT,
    specificity TEXT,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_contacted DATETIME,
    date_responded DATETIME,
    date_audit_booked DATETIME,
    email_sent BOOLEAN DEFAULT FALSE,
    email_opened BOOLEAN DEFAULT FALSE,
    email_clicked BOOLEAN DEFAULT FALSE,
    email_opened_at DATETIME,
    email_clicked_at DATETIME,
    source VARCHAR(100) DEFAULT 'google_dorks',
    raw_data TEXT
);
```

#### email_campaigns
```sql
CREATE TABLE email_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prospect_id INTEGER NOT NULL,
    subject VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    opened_at DATETIME,
    clicked_at DATETIME,
    tracking_id VARCHAR(100) UNIQUE NOT NULL
);
```

#### system_logs
```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    extra_data TEXT
);
```

### Relationships

```
prospects (1) ←→ (N) email_campaigns
    ↓
system_logs (application logs)
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/health` | Health check | None |
| GET | `/api/stats` | System statistics | API Key |
| GET | `/api/prospects` | List prospects | API Key |
| POST | `/api/prospects` | Create prospect | API Key |
| GET | `/api/prospects/{id}` | Get prospect | API Key |
| PUT | `/api/prospects/{id}` | Update prospect | API Key |
| DELETE | `/api/prospects/{id}` | Delete prospect | API Key |

### Email Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/campaigns` | Campaign statistics | API Key |
| GET | `/api/campaigns/{prospect_id}` | Prospect campaigns | API Key |
| POST | `/api/generate-email/{prospect_id}` | Generate email | API Key |
| POST | `/api/send-email/{prospect_id}` | Send email | API Key |

### System Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/system/logs` | System logs | API Key |
| POST | `/api/system/backup` | Create backup | API Key |
| GET | `/api/system/config` | System config | API Key |
| POST | `/api/search` | Manual search | API Key |
| POST | `/api/qualify/{prospect_id}` | Qualify prospect | API Key |

### Tracking Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/track/open/{tracking_id}` | Track email open | None |
| GET | `/track/click/{tracking_id}` | Track email click | None |
| GET | `/unsubscribe/{tracking_id}` | Unsubscribe | None |

## Scheduled Tasks

### Task Definitions

| Task ID | Schedule | Description | Dependencies |
|---------|---------|-------------|---------------|
| search_prospects | Every 2 hours | Search for new prospects | SerpAPI |
| qualify_prospects | Every 1 hour | Qualify prospects | Database |
| enrich_prospects | Every 3 hours | Enrich prospect data | Web scraping |
| generate_emails | Every 30 minutes | Generate emails | Mistral AI |
| send_emails | Every 15 minutes | Send emails | SMTP |
| cleanup | Daily at midnight | System cleanup | Database |
| health_check | Every 5 minutes | Health monitoring | System |

### Task Flow

```
search_prospects → qualify_prospects → enrich_prospects → generate_emails → send_emails
     ↓                    ↓                   ↓                  ↓              ↓
   SerpAPI           Database           Web scraping       Mistral AI      SMTP
```

## Security Architecture

### Authentication

- **API Keys**: Bearer token authentication
- **Environment Variables**: Secure storage of sensitive data
- **Rate Limiting**: 100 requests/minute per API key
- **IP Whitelisting**: Optional IP-based access control

### Data Protection

- **Encryption**: HTTPS for all communications
- **Database**: SQLite with file permissions
- **Email Security**: SPF/DKIM configuration
- **Input Validation**: Sanitization of all user inputs

### Access Control

- **Role-Based Access**: Admin, User, Viewer roles
- **Endpoint Security**: Different access levels for different endpoints
- **Audit Logging**: All actions logged for security review

## Performance Architecture

### Caching Strategy

- **Database Caching**: Query result caching
- **API Caching**: Response caching for frequent requests
- **File Caching**: Static asset caching

### Optimization Techniques

- **Database Indexes**: Optimized queries with proper indexing
- **Connection Pooling**: Reuse database connections
- **Async Processing**: Non-blocking operations for better performance
- **Memory Management**: Efficient memory usage patterns

### Monitoring

- **Render Metrics**: CPU, memory, response times
- **Application Metrics**: Custom performance indicators
- **Error Tracking**: Comprehensive error logging and alerting
- **Health Checks**: Regular system health verification

## Deployment Architecture

### Render Configuration

```yaml
services:
  - type: web
    name: ebusiness-ai-prospection
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python src/main.py
    envVars:
      # Environment variables
    healthCheckPath: /health
    autoDeploy: true

  - type: worker
    name: ebusiness-ai-worker
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python src/scheduler/worker.py
```

### Deployment Process

1. **Code Push**: Push to GitHub repository
2. **Auto-Deploy**: Render automatically deploys changes
3. **Health Check**: Verify deployment success
4. **Monitoring**: Continuous monitoring of services

### Scaling Strategy

- **Vertical Scaling**: Upgrade instance types as needed
- **Horizontal Scaling**: Multiple instances for high traffic
- **Database Scaling**: Migration to PostgreSQL for larger datasets
- **Load Balancing**: Render's built-in load balancing

## Integration Architecture

### External Integrations

| Service | Type | Purpose | Authentication |
|---------|------|---------|----------------|
| Mistral AI | API | Email personalization | API Key |
| SerpAPI | API | Google Dorks scraping | API Key |
| Gmail | SMTP | Email sending | App Password |
| Render | Platform | Cloud deployment | API Key |

### Webhook Support

- **Events**: prospect.created, email.sent, email.opened
- **Configuration**: Dashboard or API-based webhook setup
- **Security**: HMAC signature verification
- **Retry Logic**: Automatic retry on failed deliveries

### API Integration

- **RESTful Design**: Standard REST API patterns
- **SDK Support**: Python SDK for easy integration
- **Webhook Support**: Real-time notifications
- **Rate Limiting**: Configurable rate limits

## Error Handling Architecture

### Error Types

| Error Type | Description | Handling Strategy |
|------------|-------------|------------------|
| Network Errors | Connection issues | Retry with exponential backoff |
| API Errors | External service failures | Graceful degradation |
| Database Errors | Data persistence issues | Transaction rollback |
| Validation Errors | Invalid input data | Detailed error messages |

### Logging Strategy

- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Automatic log file rotation
- **Centralized Logging**: All services log to central location

### Monitoring and Alerting

- **Health Checks**: Regular system health verification
- **Performance Metrics**: CPU, memory, response times
- **Error Rates**: Track error rates and trends
- **Alerting**: Email alerts for critical issues

## Future Enhancements

### Planned Features

1. **Advanced Analytics**
   - Predictive lead scoring
   - Campaign performance prediction
   - Advanced reporting dashboards

2. **Multi-Channel Support**
   - LinkedIn integration
   - SMS campaign support
   - Social media prospecting

3. **AI Enhancements**
   - Advanced NLP for email optimization
   - Predictive analytics
   - Automated campaign optimization

4. **Scalability Improvements**
   - PostgreSQL migration
   - Microservices architecture
   - Kubernetes deployment

### Technical Debt

1. **Database Optimization**
   - Query optimization
   - Index optimization
   - Connection pooling

2. **Code Quality**
   - Unit test coverage improvement
   - Integration testing
   - Code documentation

3. **Performance**
   - Caching optimization
   - Memory usage optimization
   - Response time improvement

## Conclusion

EBUSINESS AI architecture is designed to be scalable, maintainable, and extensible. The system uses modern technologies and best practices to ensure reliable operation in production environments.

Key architectural decisions include:
- **Microservices-inspired design** with separate services for different concerns
- **Event-driven architecture** for loose coupling between components
- **Cloud-native deployment** on Render for easy scaling
- **Comprehensive monitoring** for operational excellence
- **Security-first approach** with proper authentication and data protection

The architecture supports the core business requirements of finding, qualifying, and contacting e-commerce prospects while providing the flexibility to evolve with changing business needs.
