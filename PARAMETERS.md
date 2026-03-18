# 📋 API Endpoint Parameters Reference

## Request Body Parameters (JSON)

---

## 1️⃣ CREATE DATASET - `/api/v1/datasets/` (POST)

### Required Parameters

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `fqn` | string | `"mysql.sales.public.customers"` | Fully Qualified Name (4 parts separated by dots) |
| `connection_name` | string | `"mysql"` | Connection/source name |
| `database_name` | string | `"sales"` | Database name |
| `schema_name` | string | `"public"` | Schema name |
| `table_name` | string | `"customers"` | Table/dataset name |
| `source_type` | string | `"MySQL"` | Valid: MySQL, PostgreSQL, MSSQL, Snowflake, Redshift, BigQuery, Oracle |
| `columns` | array | `[{...}]` | Array of column objects (can be empty) |

### Column Object (inside `columns` array)

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `name` | string | `"customer_id"` | Column name |
| `type` | string | `"INT"` | Column data type |

### Example
```json
{
  "fqn": "mysql.sales.public.customers",
  "connection_name": "mysql",
  "database_name": "sales",
  "schema_name": "public",
  "table_name": "customers",
  "source_type": "MySQL",
  "columns": [
    {"name": "customer_id", "type": "INT"},
    {"name": "name", "type": "VARCHAR(255)"},
    {"name": "email", "type": "VARCHAR(255)"}
  ]
}
```

---

## 2️⃣ LIST DATASETS - `/api/v1/datasets/` (GET)

### Query Parameters (Optional)

| Parameter | Type | Default | Example | Description |
|-----------|------|---------|---------|-------------|
| `skip` | integer | 0 | `?skip=0` | Number of datasets to skip |
| `limit` | integer | 100 | `?limit=10` | Number of datasets to return |

### Usage Examples
```
GET /api/v1/datasets/
GET /api/v1/datasets/?skip=0&limit=10
GET /api/v1/datasets/?limit=5
```

---

## 3️⃣ GET SINGLE DATASET - `/api/v1/datasets/{id}` (GET)

### Path Parameters (Required)

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `id` | integer | `1` | Dataset ID |

### Usage Examples
```
GET /api/v1/datasets/1
GET /api/v1/datasets/5
GET /api/v1/datasets/999
```

---

## 4️⃣ GET DATASET WITH LINEAGE - `/api/v1/datasets/{id}/lineage` (GET)

### Path Parameters (Required)

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `id` | integer | `1` | Dataset ID |

### Usage Examples
```
GET /api/v1/datasets/1/lineage
GET /api/v1/datasets/2/lineage
```

---

## 5️⃣ DELETE DATASET - `/api/v1/datasets/{id}` (DELETE)

### Path Parameters (Required)

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `id` | integer | `1` | Dataset ID to delete |

### Usage Examples
```
DELETE /api/v1/datasets/1
DELETE /api/v1/datasets/5
```

---

## 6️⃣ CREATE LINEAGE - `/api/v1/lineage/` (POST)

### Required Parameters

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `upstream_dataset_id` | integer | `1` | Source dataset ID (must exist) |
| `downstream_dataset_id` | integer | `2` | Target dataset ID (must exist) |

### Validation Rules
- ❌ `upstream_dataset_id` must NOT equal `downstream_dataset_id`
- ❌ Both IDs must be different positive integers
- ❌ Cannot create cycles (A→B→C, then C→A forbidden)
- ❌ Both datasets must exist

### Example
```json
{
  "upstream_dataset_id": 1,
  "downstream_dataset_id": 2
}
```

---

## 7️⃣ LIST LINEAGES - `/api/v1/lineage/` (GET)

### No Parameters Required

```
GET /api/v1/lineage/
```

---

## 8️⃣ GET SINGLE LINEAGE - `/api/v1/lineage/{id}` (GET)

### Path Parameters (Required)

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `id` | integer | `1` | Lineage ID |

### Usage Examples
```
GET /api/v1/lineage/1
GET /api/v1/lineage/5
```

---

## 9️⃣ DELETE LINEAGE - `/api/v1/lineage/{id}` (DELETE)

### Path Parameters (Required)

| Parameter | Type | Example | Description |
|-----------|------|---------|-------------|
| `id` | integer | `1` | Lineage ID to delete |

### Usage Examples
```
DELETE /api/v1/lineage/1
DELETE /api/v1/lineage/5
```

---

## 🔟 SEARCH - `/api/v1/search/` (GET)

### Query Parameters

| Parameter | Type | Required | Example | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | ✅ Yes | `?q=customers` | Search query term |

### Search Targets (Priority Order)
1. **Priority 1** - Table name (exact/partial match)
2. **Priority 2** - Column name (exact/partial match)
3. **Priority 3** - Schema name (exact/partial match)
4. **Priority 4** - Database name (exact/partial match)

### Usage Examples
```
GET /api/v1/search/?q=customers
GET /api/v1/search/?q=customer_id
GET /api/v1/search/?q=public
GET /api/v1/search/?q=sales
GET /api/v1/search/?q=orders
```

---

## 🔟 HEALTH - `/health` (GET)

### No Parameters Required

```
GET /health
```

---

## 📊 Complete Parameter Summary Table

### All Required Fields by Endpoint

| Endpoint | Required Parameters | Optional Parameters |
|----------|-------------------|-------------------|
| POST /datasets/ | fqn, connection_name, database_name, schema_name, table_name, source_type, columns | None |
| GET /datasets/ | None | skip, limit |
| GET /datasets/{id} | id (path) | None |
| GET /datasets/{id}/lineage | id (path) | None |
| DELETE /datasets/{id} | id (path) | None |
| POST /lineage/ | upstream_dataset_id, downstream_dataset_id | None |
| GET /lineage/ | None | None |
| GET /lineage/{id} | id (path) | None |
| DELETE /lineage/{id} | id (path) | None |
| GET /search/ | q (query) | None |
| GET /health | None | None |

---

## 🎯 Valid Values Reference

### source_type (String - Pick One)
```
"MySQL"
"PostgreSQL"
"MSSQL"
"Snowflake"
"Redshift"
"BigQuery"
"Oracle"
```

### FQN Format (Required)
```
Format: connection.database.schema.table

Examples:
✅ "mysql.sales.public.customers"
✅ "snowflake.warehouse.raw.orders"
✅ "postgres.analytics.staging.users"
❌ "mysql.sales" (only 2 parts, need 4)
❌ "mysql.sales.public" (only 3 parts, need 4)
```

---

## 📌 Data Types

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | Integer | Auto-generated, > 0 |
| `fqn` | String | 1-512 chars, UNIQUE |
| `connection_name` | String | 1-255 chars |
| `database_name` | String | 1-255 chars |
| `schema_name` | String | 1-255 chars |
| `table_name` | String | 1-255 chars |
| `source_type` | String | Must be in valid list |
| `column.name` | String | 1-255 chars |
| `column.type` | String | 1-100 chars |
| `upstream_dataset_id` | Integer | Must exist, > 0 |
| `downstream_dataset_id` | Integer | Must exist, > 0, ≠ upstream_id |
| `created_at` | DateTime | Auto-generated |
| `updated_at` | DateTime | Auto-generated |

---

## ❌ Validation Errors

### 400 Bad Request
```json
{
  "error": "Cycle detected",
  "detail": "Adding lineage would create a cycle in the graph"
}
```

### 404 Not Found
```json
{
  "error": "Not Found",
  "detail": "Dataset with ID 999 not found"
}
```

### 409 Conflict
```json
{
  "error": "Conflict",
  "detail": "Dataset with FQN 'mysql.sales.public.customers' already exists"
}
```

### 422 Unprocessable Entity
```json
{
  "error": "Validation Error",
  "details": [
    {
      "loc": ["body", "fqn"],
      "msg": "FQN must be in format: connection_name.database_name.schema_name.table_name",
      "type": "value_error"
    }
  ]
}
```

---

## 💡 Common Scenarios

### Scenario 1: Create Dataset with No Columns
```json
{
  "fqn": "mysql.sales.public.customers",
  "connection_name": "mysql",
  "database_name": "sales",
  "schema_name": "public",
  "table_name": "customers",
  "source_type": "MySQL",
  "columns": []
}
```

### Scenario 2: Create Dataset with 3 Columns
```json
{
  "fqn": "snowflake.warehouse.raw.orders",
  "connection_name": "snowflake",
  "database_name": "warehouse",
  "schema_name": "raw",
  "table_name": "orders",
  "source_type": "Snowflake",
  "columns": [
    {"name": "order_id", "type": "INT"},
    {"name": "customer_id", "type": "INT"},
    {"name": "order_date", "type": "DATE"}
  ]
}
```

### Scenario 3: Create Lineage from Dataset 1 to Dataset 2
```json
{
  "upstream_dataset_id": 1,
  "downstream_dataset_id": 2
}
```

### Scenario 4: Paginated Dataset Listing
```
GET /api/v1/datasets/?skip=10&limit=5
(Skip first 10, return next 5)
```

### Scenario 5: Search Multiple Ways
```
GET /api/v1/search/?q=orders       (table name)
GET /api/v1/search/?q=order_id     (column name)
GET /api/v1/search/?q=warehouse    (database name)
GET /api/v1/search/?q=raw          (schema name)
```

---

## 🚀 Quick Copy-Paste Templates

### Create Dataset Template
```json
{
  "fqn": "CONNECTION.DATABASE.SCHEMA.TABLE",
  "connection_name": "CONNECTION",
  "database_name": "DATABASE",
  "schema_name": "SCHEMA",
  "table_name": "TABLE",
  "source_type": "MySQL|PostgreSQL|MSSQL|Snowflake|Redshift|BigQuery|Oracle",
  "columns": [
    {"name": "COLUMN_NAME", "type": "COLUMN_TYPE"}
  ]
}
```

### Create Lineage Template
```json
{
  "upstream_dataset_id": ID_OF_SOURCE,
  "downstream_dataset_id": ID_OF_TARGET
}
```
