# 🧪 Manual Endpoint Testing Guide

## Prerequisites
- Server running on `http://localhost:8000`
- PowerShell or any terminal with `curl` or use browser

---

## 1️⃣ HEALTH CHECK

**Purpose:** Verify the API is alive

### Browser
```
http://localhost:8000/health
```

### PowerShell (curl)
```powershell
curl http://localhost:8000/health
```

**Expected Response (200 OK):**
```json
{"status": "healthy", "service": "metadata-service", "version": "1.0.0"}
```

---

## 2️⃣ CREATE DATASET (POST)

**Purpose:** Add a new dataset to the system

### PowerShell
```powershell
$body = @{
    fqn = "mysql.sales.public.customers"
    connection_name = "mysql"
    database_name = "sales"
    schema_name = "public"
    table_name = "customers"
    source_type = "MySQL"
    columns = @(
        @{ name = "customer_id"; type = "INT" },
        @{ name = "name"; type = "VARCHAR(255)" },
        @{ name = "email"; type = "VARCHAR(255)" }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/datasets/" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### curl (Windows Git Bash or similar)
```bash
curl -X POST http://localhost:8000/api/v1/datasets/ \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": 1,
  "fqn": "mysql.sales.public.customers",
  "connection_name": "mysql",
  "database_name": "sales",
  "schema_name": "public",
  "table_name": "customers",
  "source_type": "MySQL",
  "columns": [
    {"id": 1, "dataset_id": 1, "name": "customer_id", "type": "INT", "created_at": "..."},
    {"id": 2, "dataset_id": 1, "name": "name", "type": "VARCHAR(255)", "created_at": "..."},
    {"id": 3, "dataset_id": 1, "name": "email", "type": "VARCHAR(255)", "created_at": "..."}
  ],
  "created_at": "...",
  "updated_at": "..."
}
```

---

## 3️⃣ CREATE SECOND DATASET

### PowerShell
```powershell
$body = @{
    fqn = "snowflake.warehouse.raw.orders"
    connection_name = "snowflake"
    database_name = "warehouse"
    schema_name = "raw"
    table_name = "orders"
    source_type = "Snowflake"
    columns = @(
        @{ name = "order_id"; type = "INT" },
        @{ name = "customer_id"; type = "INT" },
        @{ name = "amount"; type = "DECIMAL(10,2)" }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/datasets/" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**Note:** This will have `id = 2`

---

## 4️⃣ LIST ALL DATASETS (GET)

**Purpose:** See all datasets you've created

### Browser
```
http://localhost:8000/api/v1/datasets/
```

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/datasets/" `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### curl
```bash
curl http://localhost:8000/api/v1/datasets/
```

**Expected Response (200 OK):**
```json
[
  {
    "id": 1,
    "fqn": "mysql.sales.public.customers",
    "connection_name": "mysql",
    "database_name": "sales",
    "schema_name": "public",
    "table_name": "customers",
    "source_type": "MySQL",
    "columns": [...],
    "created_at": "...",
    "updated_at": "..."
  },
  {
    "id": 2,
    "fqn": "snowflake.warehouse.raw.orders",
    ...
  }
]
```

---

## 5️⃣ GET SINGLE DATASET (GET by ID)

**Purpose:** Get details of a specific dataset

### Browser
```
http://localhost:8000/api/v1/datasets/1
```

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/datasets/1" `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### curl
```bash
curl http://localhost:8000/api/v1/datasets/1
```

**Replace `1` with any dataset ID**

**Expected Response (200 OK):** Same as single dataset object

---

## 6️⃣ CREATE LINEAGE (POST)

**Purpose:** Define data lineage relationship (A → B means A flows to B)

### PowerShell
```powershell
$body = @{
    upstream_dataset_id = 1
    downstream_dataset_id = 2
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/lineage/" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### curl
```bash
curl -X POST http://localhost:8000/api/v1/lineage/ \
  -H "Content-Type: application/json" \
  -d '{"upstream_dataset_id": 1, "downstream_dataset_id": 2}'
```

**Expected Response (201 Created):**
```json
{
  "id": 1,
  "upstream_dataset_id": 1,
  "downstream_dataset_id": 2,
  "created_at": "..."
}
```

---

## 7️⃣ TEST CYCLE DETECTION ⚠️

**Purpose:** Verify the system prevents circular lineage

### PowerShell - This should FAIL with 400
```powershell
$body = @{
    upstream_dataset_id = 2
    downstream_dataset_id = 1
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/lineage/" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body `
  -UseBasicParsing
```

**Expected Response (400 Bad Request):**
```json
{
  "error": "Cycle detected",
  "detail": "Adding lineage would create a cycle in the graph"
}
```

---

## 8️⃣ GET DATASET WITH LINEAGE (GET)

**Purpose:** See a dataset plus all its upstream and downstream relationships

### Browser
```
http://localhost:8000/api/v1/datasets/1/lineage
```

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/datasets/1/lineage" `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### curl
```bash
curl http://localhost:8000/api/v1/datasets/1/lineage
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "fqn": "mysql.sales.public.customers",
  ...
  "upstream_datasets": [],
  "downstream_datasets": [
    {
      "id": 2,
      "fqn": "snowflake.warehouse.raw.orders",
      ...
    }
  ]
}
```

---

## 9️⃣ SEARCH DATASETS (GET)

**Purpose:** Search by table name, column name, schema, or database

### Browser
```
http://localhost:8000/api/v1/search/?q=customers
```

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/search/?q=customers" `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### curl
```bash
curl "http://localhost:8000/api/v1/search/?q=customers"
```

**Try different searches:**
- `?q=orders` - Search by table name
- `?q=customer_id` - Search by column name
- `?q=public` - Search by schema
- `?q=warehouse` - Search by database

**Expected Response (200 OK):**
```json
{
  "query": "customers",
  "total_results": 1,
  "results": [
    {
      "dataset": {
        "id": 1,
        "fqn": "mysql.sales.public.customers",
        ...
      },
      "match_type": "table_name",
      "priority": 1
    }
  ]
}
```

---

## 🔟 LIST ALL LINEAGES (GET)

**Purpose:** See all lineage relationships

### Browser
```
http://localhost:8000/api/v1/lineage/
```

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/lineage/" `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### curl
```bash
curl http://localhost:8000/api/v1/lineage/
```

**Expected Response (200 OK):**
```json
[
  {
    "id": 1,
    "upstream_dataset_id": 1,
    "downstream_dataset_id": 2,
    "created_at": "..."
  }
]
```

---

## 1️⃣1️⃣ GET SINGLE LINEAGE (GET by ID)

**Purpose:** Get details of a specific lineage relationship

### Browser
```
http://localhost:8000/api/v1/lineage/1
```

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/lineage/1" `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

---

## 1️⃣2️⃣ DELETE LINEAGE (DELETE)

**Purpose:** Remove a lineage relationship

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/lineage/1" `
  -Method DELETE `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### curl
```bash
curl -X DELETE http://localhost:8000/api/v1/lineage/1
```

**Expected Response (200 OK):**
```json
{"message": "Lineage deleted successfully"}
```

---

## 1️⃣3️⃣ DELETE DATASET (DELETE)

**Purpose:** Remove a dataset (also removes its columns and lineages)

### PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/datasets/1" `
  -Method DELETE `
  -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### curl
```bash
curl -X DELETE http://localhost:8000/api/v1/datasets/1
```

**Expected Response (200 OK):**
```json
{"message": "Dataset deleted successfully"}
```

---

## 🧪 MANUAL TEST SEQUENCE

**Follow this order to test everything:**

```
1. ✅ Health Check (endpoint 1)
2. ✅ Create Dataset 1 (endpoint 2)
3. ✅ Create Dataset 2 (endpoint 3)
4. ✅ List Datasets (endpoint 4)
5. ✅ Get Dataset 1 (endpoint 5)
6. ✅ Create Lineage 1→2 (endpoint 6)
7. ✅ Try Invalid Lineage 2→1 (endpoint 7) - Should FAIL ⚠️
8. ✅ Get Dataset 1 with Lineage (endpoint 8)
9. ✅ Search "customers" (endpoint 9)
10. ✅ List Lineages (endpoint 10)
11. ✅ Get Lineage 1 (endpoint 11)
12. ✅ Delete Lineage 1 (endpoint 12)
13. ✅ Delete Dataset 1 (endpoint 13)
14. ✅ List Datasets - Should show only Dataset 2 now
```

---

## 📊 QUICK REFERENCE TABLE

| # | Endpoint | Method | URL | Purpose |
|---|----------|--------|-----|---------|
| 1 | Health | GET | `/health` | Check API status |
| 2 | Create Dataset | POST | `/api/v1/datasets/` | Add new dataset |
| 3 | List Datasets | GET | `/api/v1/datasets/` | Show all datasets |
| 4 | Get Dataset | GET | `/api/v1/datasets/{id}` | Get one dataset |
| 5 | Get with Lineage | GET | `/api/v1/datasets/{id}/lineage` | Dataset + relationships |
| 6 | Create Lineage | POST | `/api/v1/lineage/` | Add data flow |
| 7 | List Lineages | GET | `/api/v1/lineage/` | Show all lineages |
| 8 | Get Lineage | GET | `/api/v1/lineage/{id}` | Get one lineage |
| 9 | Delete Lineage | DELETE | `/api/v1/lineage/{id}` | Remove relationship |
| 10 | Search | GET | `/api/v1/search/?q=X` | Find datasets |
| 11 | Delete Dataset | DELETE | `/api/v1/datasets/{id}` | Remove dataset |

---

## ⚙️ INTERACTIVE TESTING (Easiest!)

Just open this URL in your browser:
```
http://localhost:8000/docs
```

This gives you a **Swagger UI** where you can:
- 🔘 Click "Try it out"
- 📝 Fill in parameters
- ✅ Execute requests
- 📊 See responses with syntax highlighting

**No curl needed!**

---

## ✅ ERROR CODES (What to expect)

| Code | Meaning | Example |
|------|---------|---------|
| 200 | ✅ Success | GET dataset returned |
| 201 | ✅ Created | POST dataset succeeded |
| 400 | ❌ Bad Request | Cycle detected in lineage |
| 404 | ❌ Not Found | Dataset ID doesn't exist |
| 409 | ❌ Conflict | Dataset FQN already exists |
| 422 | ❌ Validation Error | Invalid JSON or missing fields |

---

## 💡 TIPS

1. **Save responses** - Copy the `id` values for subsequent requests
2. **Test with Swagger** (`/docs`) first - Easier than curl
3. **Check order** - Create datasets before creating lineages
4. **FQN is unique** - Can't create two datasets with same FQN
5. **Cascade delete** - Deleting dataset deletes its columns and lineages
