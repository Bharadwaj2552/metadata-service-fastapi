# Quick Reference Guide

## 🚀 Quick Start (5 minutes)

### Option 1: Docker (Recommended)
```bash
cd metadata-service
cp .env.example .env
docker-compose up -d
```

### Option 2: Local Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
poetry install
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

**Access API**: http://localhost:8000/docs

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Complete documentation & API reference |
| [EXAMPLES.md](EXAMPLES.md) | Practical usage examples (curl & Python) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development & contribution guidelines |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Production deployment guide |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Architecture & design overview |

---

## 🔑 Key Endpoints

### Datasets
```bash
# Create
POST /api/v1/datasets/ 
{ "fqn": "snowflake.sales.public.orders", ... }

# List (paginated)
GET /api/v1/datasets/?skip=0&limit=100

# Get specific
GET /api/v1/datasets/1

# Get with lineage
GET /api/v1/datasets/1/lineage

# Delete
DELETE /api/v1/datasets/1
```

### Lineage
```bash
# Create relationship
POST /api/v1/lineage/
{ "upstream_dataset_id": 1, "downstream_dataset_id": 2 }

# List all
GET /api/v1/lineage/

# Get specific
GET /api/v1/lineage/1

# Delete
DELETE /api/v1/lineage/1
```

### Search
```bash
# Search by any criteria (table, column, schema, database)
GET /api/v1/search/?q=orders
```

### System
```bash
# Health check
GET /health

# API info
GET /

# Swagger UI
GET /docs

# ReDoc
GET /redoc
```

---

## 🛠 Development Commands

### Using Make (Recommended)
```bash
make help              # Show all available commands
make install           # Install dependencies
make setup-dev         # Setup development environment
make format            # Format code with Black
make lint              # Run flake8
make type-check        # Run mypy
make quality           # All quality checks
make test              # Run tests
make test-cov          # Tests with coverage
make run               # Run application
make migrate           # Run migrations
make pre-commit        # Setup pre-commit hooks
make docker-up         # Start Docker services
make docker-down       # Stop Docker services
```

### Using Poetry
```bash
poetry install         # Install dependencies
poetry lock            # Update lock file
poetry show            # Show dependencies
poetry add <package>   # Add dependency
poetry remove <package># Remove dependency
```

### Using Docker
```bash
docker-compose up -d                    # Start services
docker-compose down                     # Stop services
docker-compose logs -f api              # View logs
docker-compose exec api bash            # Access container
docker-compose exec api pytest tests/ -v # Run tests
```

---

## 📊 Data Model

### Datasets
- **id**: Auto-increment primary key
- **fqn**: Fully qualified name (unique) - `connection.database.schema.table`
- **connection_name, database_name, schema_name, table_name**: FQN components
- **source_type**: MySQL, PostgreSQL, Snowflake, etc.
- **created_at, updated_at**: Timestamps
- **columns**: One-to-many relationship

### Columns
- **id**: Auto-increment primary key
- **dataset_id**: Foreign key to datasets
- **name**: Column name
- **type**: Column type (INT, VARCHAR, etc.)
- **created_at**: Creation timestamp

### Lineage
- **id**: Auto-increment primary key
- **upstream_dataset_id**: Source dataset
- **downstream_dataset_id**: Target dataset
- **created_at**: Creation timestamp
- **Unique constraint** on (upstream, downstream) pair

---

## 🔍 Search Priorities

Higher number = lower priority (searched later in results)

| Priority | Type | Description |
|----------|------|-------------|
| 1 | table_name | Match on table name (highest priority) |
| 2 | column_name | Match on column names |
| 3 | schema_name | Match on schema name |
| 4 | database_name | Match on database name (lowest priority) |

**Result**: Each dataset appears once with its highest-priority match

---

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=metadata_user
DB_PASSWORD=metadata_password
DB_NAME=metadata_db

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Docker Compose Services
- **mysql**: MySQL 8.0 database on port 3306
- **api**: FastAPI application on port 8000

---

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific file
pytest tests/test_api.py -v

# Specific test
pytest tests/test_api.py::TestDatasetEndpoints::test_create_dataset -v

# With coverage
pytest tests/ --cov=app
```

### Test Files
- `tests/test_utils.py` - Graph algorithm tests
- `tests/test_api.py` - API endpoint tests

### Test Database
Uses SQLite in-memory for speed and isolation

---

## 🔒 Source Type Options

Valid `source_type` values:
- MySQL
- PostgreSQL
- MSSQL
- Snowflake
- Redshift
- BigQuery
- Oracle

---

## 🐛 Troubleshooting

### API won't start
```bash
# Check logs
docker-compose logs api

# Restart
docker-compose restart api

# Or locally - check port 8000 is free
```

### Database connection failed
```bash
# Check MySQL is running
docker-compose logs mysql

# Verify credentials in .env

# Test connection
docker-compose exec mysql mysql -u root -p
```

### Migrations failed
```bash
# Check current status
docker-compose exec api alembic current

# View history
docker-compose exec api alembic history

# Downgrade one step
docker-compose exec api alembic downgrade -1
```

### Tests fail
```bash
# Install test dependencies
poetry install

# Run single test for debugging
pytest tests/test_utils.py::TestCycleDetection::test_has_cycle_simple_cycle -vv
```

---

## 📦 Project Structure

```
metadata-service/
├── app/                 # Main application
│   ├── api/            # API routes
│   ├── core/           # Config & database
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── repository/     # Data access
│   └── utils/          # Utilities
├── alembic/            # Database migrations
├── tests/              # Test suite
├── docker-compose.yml  # Docker setup
├── Dockerfile          # Container image
├── pyproject.toml      # Dependencies
├── Makefile            # Commands
└── README.md           # Full documentation
```

---

## 🏃 Common Workflows

### Create a Dataset with Lineage
```bash
# 1. Create first dataset
curl -X POST http://localhost:8000/api/v1/datasets/ \
  -H "Content-Type: application/json" \
  -d '{
    "fqn": "snowflake.sales.public.orders",
    "connection_name": "snowflake",
    "database_name": "sales",
    "schema_name": "public",
    "table_name": "orders",
    "source_type": "Snowflake",
    "columns": [{"name": "id", "type": "INT"}]
  }'
# Returns: {"id": 1, ...}

# 2. Create second dataset
curl -X POST http://localhost:8000/api/v1/datasets/ \
  -H "Content-Type: application/json" \
  -d '{...dataset 2 data...}'
# Returns: {"id": 2, ...}

# 3. Create lineage
curl -X POST http://localhost:8000/api/v1/lineage/ \
  -H "Content-Type: application/json" \
  -d '{
    "upstream_dataset_id": 1,
    "downstream_dataset_id": 2
  }'

# 4. View lineage
curl http://localhost:8000/api/v1/datasets/1/lineage
```

### Search Datasets
```bash
# Search by table name
curl "http://localhost:8000/api/v1/search/?q=orders"

# Search by column name
curl "http://localhost:8000/api/v1/search/?q=customer_id"

# Search by schema
curl "http://localhost:8000/api/v1/search/?q=public"
```

---

## 📈 Performance Tips

1. **Use pagination** for large datasets
   ```bash
   GET /api/v1/datasets/?limit=50&skip=0
   ```

2. **Build lineage carefully** to avoid performance issues with large graphs

3. **Search queries are case-insensitive** - good for user experience

4. **Indexed columns**: fqn, table_name, column_name, schema_name, database_name

---

## 🚀 Next Steps

### For Users
1. Read README.md for complete API documentation
2. Check EXAMPLES.md for practical examples
3. Ask questions or report issues

### For Developers
1. Read CONTRIBUTING.md
2. Setup development environment
3. Make changes in feature branch
4. Run tests and quality checks
5. Submit pull request

### For Operations
1. Read DEPLOYMENT.md for production setup
2. Configure monitoring and logging
3. Setup backup procedures
4. Create runbooks
5. Train team

---

## 📞 Support & Resources

- **Documentation**: See README.md, EXAMPLES.md
- **API Docs**: http://localhost:8000/docs
- **Issues**: Check GitHub issues or contact team
- **Deployment Help**: See DEPLOYMENT.md

---

## ✅ Checklist for Production

- [ ] Environment variables configured
- [ ] Database backups scheduled
- [ ] SSL/TLS certificates configured
- [ ] Monitoring and logging setup
- [ ] Rate limiting configured
- [ ] Load testing completed
- [ ] Disaster recovery plan documented
- [ ] Team trained on operations
- [ ] Documentation updated

---

**Last Updated**: March 17, 2024
**Version**: 1.0.0
