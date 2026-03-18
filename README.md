# Metadata Management Service

A production-grade backend service for managing **dataset metadata, lineage relationships, and search** in data governance platforms. Built with **FastAPI, MySQL, SQLAlchemy, and Alembic**.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![License](https://img.shields.io/badge/license-MIT-blue)

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Design Decisions](#design-decisions)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **Dataset Management** | Store and manage dataset metadata with fully qualified names (FQN) |
| **Lineage Tracking** | Define upstream/downstream relationships between datasets |
| **Cycle Detection** | Prevent invalid circular dependencies in lineage graphs |
| **Multi-Priority Search** | Search by table name, column name, schema name, or database name |
| **Auto-Migration** | Automatic database schema setup with Alembic |
| **API Documentation** | Interactive Swagger UI and ReDoc documentation |

### Technical Features

- ✅ **Type-safe** with Pydantic v2 validation
- ✅ **Production-ready** error handling and HTTP status codes
- ✅ **Comprehensive logging** and monitoring
- ✅ **Pre-commit hooks** for code quality
- ✅ **Unit & integration tests** with pytest
- ✅ **Docker & Docker Compose** for easy deployment
- ✅ **SQLAlchemy ORM** with proper indexing and relationships
- ✅ **Cycle detection** using Depth-First Search (DFS)

---

## 🏗 Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  API Layer           │  Service Layer      │  Repository Layer
│  ─────────────────   │  ──────────────     │  ─────────────────
│  • datasets_routes   │  • DatasetService   │  • DatasetRepository
│  • lineage_routes    │  • LineageService   │  • LineageRepository
│  • search_routes     │  • SearchService    │  • ColumnRepository
│                      │                     │
│  Schema Layer        │  Utilities          │
│  ──────────────      │  ────────────       │
│  • Pydantic models   │  • Graph algorithms │
│  • Validation       │  • Cycle detection  │
└─────────────────────────────────────────────────────────────┘
                            ↓
                      ┌──────────────┐
                      │    MySQL     │
                      │   Database   │
                      └──────────────┘
```

### Entity Relationship Diagram

```
┌──────────────────┐
│    Datasets      │
├──────────────────┤
│ id (PK)          │
│ fqn (UNIQUE)     │
│ connection_name  │
│ database_name    │
│ schema_name      │
│ table_name       │
│ source_type      │
│ created_at       │
│ updated_at       │
└──────────────────┘
        │ 1
        │ │ M
        ├─────────────┐
        │             │
        │             │
    ┌───────┐     ┌──────────┐
    │Columns│     │ Lineage  │
    ├───────┤     ├──────────┤
    │ id    │     │ id       │
    │ name  │     │ upstream │
    │ type  │     │downstream
    └───────┘     └──────────┘
```

### Layer Responsibilities

**API Layer**: Request/response handling, HTTP status codes
**Service Layer**: Business logic, validation, cycle detection
**Repository Layer**: Database operations, queries
**Models**: SQLAlchemy ORM definitions
**Schemas**: Pydantic validation models

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (recommended)
- MySQL 8.0+ (optional if using Docker)

### Option 1: Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd metadata-service

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

The API will be available at `http://localhost:8000`

### Option 2: Local Development

```bash
# Create Python environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install poetry
poetry install

# Setup .env file
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start the application
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/

# Interactive docs
open http://localhost:8000/docs
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=metadata_user
DB_PASSWORD=metadata_password
DB_NAME=metadata_db

# Environment
ENVIRONMENT=development

# API Configuration
API_TITLE=Metadata Management Service
API_VERSION=1.0.0
API_DESCRIPTION=Production-grade metadata management and lineage tracking system
```

### Database Setup

The database is automatically initialized on application startup:

1. **Docker Compose**: Automatically creates MySQL container and tables
2. **Local Development**: Run `alembic upgrade head`
3. **Manual**: Run migrations: `docker exec metadata_api alembic upgrade head`

---

## 📚 API Documentation

### Base URL

```
http://localhost:8000/api/v1
```

### Authentication

Currently no authentication. For production, add API keys or OAuth2.

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/datasets/` | Create dataset |
| **GET** | `/datasets/` | List datasets |
| **GET** | `/datasets/{id}` | Get dataset |
| **GET** | `/datasets/{id}/lineage` | Get dataset with lineage |
| **DELETE** | `/datasets/{id}` | Delete dataset |
| **POST** | `/lineage/` | Create lineage relationship |
| **GET** | `/lineage/` | List lineages |
| **GET** | `/lineage/{id}` | Get lineage |
| **DELETE** | `/lineage/{id}` | Delete lineage |
| **GET** | `/search/` | Search datasets |

### Dataset Endpoints

#### Create Dataset

```bash
POST /datasets/

{
  "fqn": "snowflake.sales.public.orders",
  "connection_name": "snowflake",
  "database_name": "sales",
  "schema_name": "public",
  "table_name": "orders",
  "source_type": "Snowflake",
  "columns": [
    {"name": "order_id", "type": "INT"},
    {"name": "customer_id", "type": "INT"},
    {"name": "amount", "type": "DECIMAL(10, 2)"}
  ]
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "fqn": "snowflake.sales.public.orders",
  "connection_name": "snowflake",
  "database_name": "sales",
  "schema_name": "public",
  "table_name": "orders",
  "source_type": "Snowflake",
  "columns": [
    {
      "id": 1,
      "name": "order_id",
      "type": "INT",
      "dataset_id": 1,
      "created_at": "2024-03-17T10:00:00"
    }
  ],
  "created_at": "2024-03-17T10:00:00",
  "updated_at": "2024-03-17T10:00:00"
}
```

#### Get Dataset with Lineage

```bash
GET /datasets/1/lineage
```

**Response (200 OK):**
```json
{
  "id": 1,
  "fqn": "snowflake.sales.public.orders",
  "connection_name": "snowflake",
  "database_name": "sales",
  "schema_name": "public",
  "table_name": "orders",
  "source_type": "Snowflake",
  "columns": [],
  "upstream_datasets": [],
  "downstream_datasets": [
    {
      "id": 2,
      "fqn": "snowflake.sales.public.orders_clean",
      "connection_name": "snowflake",
      "database_name": "sales",
      "schema_name": "public",
      "table_name": "orders_clean",
      "source_type": "Snowflake",
      "columns": [],
      "created_at": "2024-03-17T10:01:00",
      "updated_at": "2024-03-17T10:01:00"
    }
  ],
  "created_at": "2024-03-17T10:00:00",
  "updated_at": "2024-03-17T10:00:00"
}
```

### Lineage Endpoints

#### Create Lineage

```bash
POST /lineage/

{
  "upstream_dataset_id": 1,
  "downstream_dataset_id": 2
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "upstream_dataset_id": 1,
  "downstream_dataset_id": 2,
  "created_at": "2024-03-17T10:00:00"
}
```

**Error on Cycle Detection (400 Bad Request):**
```json
{
  "error": "Bad Request",
  "detail": "Adding lineage from 2 to 1 would create a cycle. Dataset 1 is already downstream of 2.",
  "status_code": 400
}
```

### Search Endpoints

#### Search Datasets

```bash
GET /search/?q=orders
```

**Response (200 OK):**
```json
{
  "query": "orders",
  "total_results": 2,
  "results": [
    {
      "priority": 1,
      "match_type": "table_name",
      "dataset": {
        "id": 1,
        "fqn": "snowflake.sales.public.orders",
        "connection_name": "snowflake",
        "database_name": "sales",
        "schema_name": "public",
        "table_name": "orders",
        "source_type": "Snowflake",
        "columns": [],
        "created_at": "2024-03-17T10:00:00",
        "updated_at": "2024-03-17T10:00:00"
      }
    },
    {
      "priority": 2,
      "match_type": "column_name",
      "dataset": {
        "id": 3,
        "fqn": "snowflake.sales.public.order_items",
        "connection_name": "snowflake",
        "database_name": "sales",
        "schema_name": "public",
        "table_name": "order_items",
        "source_type": "Snowflake",
        "columns": [
          {
            "id": 5,
            "name": "orders_id",
            "type": "INT",
            "dataset_id": 3,
            "created_at": "2024-03-17T10:00:00"
          }
        ],
        "created_at": "2024-03-17T10:00:00",
        "updated_at": "2024-03-17T10:00:00"
      }
    }
  ]
}
```

### Search Priorities

Results are sorted by match priority:

1. **Priority 1 (table_name)**: Exact or partial match on table name - HIGHEST
2. **Priority 2 (column_name)**: Match on column names
3. **Priority 3 (schema_name)**: Match on schema name
4. **Priority 4 (database_name)**: Match on database name - LOWEST

> **Note**: Each dataset appears only once with its highest priority match

---

## 📁 Project Structure

```
metadata-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── datasets_routes.py  # Dataset CRUD endpoints
│   │   ├── lineage_routes.py   # Lineage management endpoints
│   │   └── search_routes.py    # Search functionality endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration and settings
│   │   └── database.py         # SQLAlchemy setup and session
│   ├── models/
│   │   └── __init__.py         # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── __init__.py         # Pydantic validation schemas
│   ├── services/
│   │   └── __init__.py         # Business logic layer
│   ├── repository/
│   │   └── __init__.py         # Database operations layer
│   └── utils/
│       └── __init__.py         # Graph algorithms, utilities
│
├── alembic/
│   ├── versions/
│   │   └── 001_initial_tables.py  # Initial schema migration
│   ├── env.py                 # Alembic configuration
│   └── script.py.mako         # Migration template
│
├── tests/
│   ├── __init__.py
│   ├── test_utils.py          # Graph algorithm tests
│   └── test_api.py            # API endpoint tests
│
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml         # Docker Compose setup
├── pyproject.toml             # Poetry dependencies
├── .env.example               # Environment variable template
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── .gitignore                 # Git ignore rules
├── alembic.ini                # Alembic configuration
└── README.md                  # This file
```

---

## 👨‍💻 Development

### Setup Development Environment

```bash
# Install development dependencies
poetry install

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Format code
black app/ tests/

# Lint code  
flake8 app/ tests/ --max-line-length=100

# Type checking
mypy app/
```

### Create Database Models

All models are in `app/models/__init__.py`. Modify as needed and create migrations:

```bash
# Create auto migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Add New Endpoints

1. Create route in `/app/api/`
2. Add service logic in `/app/services/`
3. Add repository methods in `/app/repository/`
4. Add Pydantic schemas in `/app/schemas/`
5. Include router in `app/main.py`

---

## 🧪 Testing

### Run All Tests

```bash
# Run all tests with output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::TestDatasetEndpoints::test_create_dataset -v
```

### Test Structure

- **test_utils.py**: Unit tests for graph algorithms
- **test_api.py**: Integration tests for API endpoints

### Test Database

Tests use SQLite in-memory database for speed and isolation.

---

## 🏛️ Design Decisions

### 1. **Database Choice: MySQL**

**Why MySQL?**
- Reliable, mature, widely used in enterprise data platforms
- Good performance for metadata queries with proper indexing
- ACID compliance ensures data consistency during lineage changes
- Easy deployment with Docker

**Trade-offs**: Could use PostgreSQL for advanced JSON features or SQLite for development

### 2. **Cycle Detection Algorithm: DFS**

**Why DFS?**
- Simple and elegant for DAG validation
- $ O(V + E) $ time complexity (V=vertices=datasets, E=edges=lineage)
- No need for complex graph algorithms like topological sorting

**Implementation**:
```python
def has_cycle(graph, start_node, target_node):
    """DFS to detect if adding edge creates cycle"""
    visited = set()
    def dfs(node):
        if node == target_node:
            return True
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited and dfs(neighbor):
                return True
        return False
    return dfs(start_node)
```

### 3. **Search Implementation: Priority-Based Deduplication**

**Why?**
- Users want most relevant results first
- Single dataset can match multiple criteria (should appear once, highest priority)
- Maintains result quality and performance

**Priority Order**:
1. Table name match (most specific)
2. Column name match
3. Schema name match
4. Database name match (least specific)

### 4. **Fully Qualified Name (FQN)**

**Format**: `connection_name.database_name.schema_name.table_name`

**Example**: `snowflake_prod.sales.public.orders`

**Benefits**:
- Globally unique identifier
- Encodes full dataset location
- Makes cross-system lineage clear
- Indexed for fast lookups

### 5. **Repository Pattern**

**Why?**
- Decouples business logic from database operations
- Makes testing easier (can mock repositories)
- Single responsibility principle
- Easy to swap implementations

### 6. **Service Layer for Business Logic**

**Why?**
- Centralized validation and error handling
- Reusable across endpoints
- Testable independently
- Clear separation of concerns

### 7. **Pydantic for Validation**

**Why?**
- Type-safe schemas
- Automatic validation and serialization
- Excellent error messages
- OpenAPI documentation generation

### 8. **Auto-Migrations with Alembic**

**Why?**
- Version control for database schema
- Easy rollbacks
- Team collaboration on schema changes
- Reproducible deployments

---

## 🐛 Troubleshooting

### Issue: Database Connection Failed

```
Error: Can't connect to MySQL server
```

**Solution**:
```bash
# Check environment variables
cat .env

# Verify MySQL is running (Docker)
docker-compose ps

# Check MySQL logs
docker-compose logs mysql

# Restart MySQL
docker-compose restart mysql
```

### Issue: Migration Fails

```
Error: Table already exists / Foreign key constraint fails
```

**Solution**:
```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Reset database (WARNING: deletes data)
docker-compose exec mysql mysql -u root -p -e "DROP DATABASE metadata_db; CREATE DATABASE metadata_db;"

# Re-run migrations
alembic upgrade head
```

### Issue: Cycle Not Detected

**Verify**:
1. Check that `has_cycle()` returns `True` for C->A when A->B->C exists
2. Review the DFS implementation
3. Ensure lineage edges are loaded from database before checking

### Issue: Tests Fail Locally

```bash
# Ensure pytest and dependencies are installed
poetry install

# Use absolute imports
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run single test
pytest tests/test_utils.py::TestCycleDetection::test_has_cycle_simple_cycle -v
```

### Issue: Docker Build Fails

```bash
# Clear Docker cache
docker-compose down --volumes

# Rebuild
docker-compose build --no-cache

# Start
docker-compose up -d
```

---

## 📝 Code Quality

### Pre-commit Hooks

Automatically run on each commit:
- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
- Standard pre-commit hooks

```bash
# Skip hooks (not recommended)
git commit --no-verify

# Run manually
pre-commit run --all-files
```

### Type Checking

```bash
# Check types
mypy app/

# Strict mode
mypy app/ --strict
```

---

## 📊 Performance Considerations

### Indexes

Strategic indexes for common queries:

- `datasets.fqn` - Primary lookup
- `datasets.table_name` - Search queries
- `datasets.database_name` - Search queries
- `datasets.schema_name` - Search queries
- `columns.name` - Column search
- `lineage.upstream_dataset_id` - Upstream queries
- `lineage.downstream_dataset_id` - Downstream queries

### Query Optimization

- Use database connection pooling (NullPool for Docker)
- Eager load relationships where needed
- Limit result sets with pagination
- Cache frequently accessed metadata

### Scalability

For production deployments with millions of datasets:

1. **Read Replicas**: Add MySQL read replicas
2. **Caching**: Implement Redis caching for search results
3. **Partitioning**: Partition lineage table by date/dataset
4. **Async Processing**: Use Celery for heavy lineage analysis
5. **Search Engine**: Consider Elasticsearch for full-text search

---

## 🔒 Security Considerations

### Current Implementation

- No authentication (development only)
- No rate limiting
- No input sanitization (Pydantic handles this)
- No CORS configuration

### Production Hardening

1. **Authentication**: Implement JWT or OAuth2
2. **Rate Limiting**: Add rate limiting middleware
3. **CORS**: Configure CORS for frontend domain
4. **SQL Injection**: SQLAlchemy ORM prevents this
5. **HTTPS**: Enable SSL/TLS in production
6. **Audit Logging**: Log all changes to audit table
7. **Database Credentials**: Use secrets management (HashiCorp Vault, AWS Secrets)

---

## 📈 Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connection
Test via any dataset query
```

### Logging

Configure in `app/core/config.py`:

```python
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
```

Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Metrics to Track

- API response times
- Database query performance
- Lineage graph size
- Search query frequency
- Error rates

---

## 🚀 Deployment

### Production Docker Setup

```bash
# Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Health check
curl http://api:8000/health

# View logs
docker-compose logs -f api
```

### Kubernetes Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: metadata-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: metadata-service
  template:
    metadata:
      labels:
        app: metadata-service
    spec:
      containers:
      - name: api
        image: metadata-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_HOST
          value: mysql-service
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

1. Create branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add your feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit pull request

---

## 📞 Support

For issues and questions:
- Check [Troubleshooting](#troubleshooting) section
- Review API documentation at `/docs`
- Check test files for usage examples

---

**Happy coding! 🎉**
>>>>>>> 04bc807 (Initial commit)
