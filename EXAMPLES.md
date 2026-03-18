# Metadata Service - Usage Examples

This file contains practical examples of how to use the Metadata Service API.

## Prerequisites

- API running at `http://localhost:8000`
- `curl` installed (for examples)
- Python 3.10+ with `requests` library (for Python examples)

---

## 1. Create Datasets

### Using curl

Create orders dataset:
```bash
curl -X POST http://localhost:8000/api/v1/datasets/ \
  -H "Content-Type: application/json" \
  -d '{
    "fqn": "snowflake.sales.public.orders",
    "connection_name": "snowflake",
    "database_name": "sales",
    "schema_name": "public",
    "table_name": "orders",
    "source_type": "Snowflake",
    "columns": [
      {"name": "order_id", "type": "INT"},
      {"name": "customer_id", "type": "INT"},
      {"name": "order_date", "type": "DATE"},
      {"name": "amount", "type": "DECIMAL(10,2)"}
    ]
  }'
```

Create orders_clean dataset:
```bash
curl -X POST http://localhost:8000/api/v1/datasets/ \
  -H "Content-Type: application/json" \
  -d '{
    "fqn": "snowflake.sales.public.orders_clean",
    "connection_name": "snowflake",
    "database_name": "sales",
    "schema_name": "public",
    "table_name": "orders_clean",
    "source_type": "Snowflake",
    "columns": [
      {"name": "order_id", "type": "INT"},
      {"name": "customer_id", "type": "INT"},
      {"name": "order_date", "type": "DATE"},
      {"name": "amount", "type": "DECIMAL(10,2)"}
    ]
  }'
```

Create orders_aggregated dataset:
```bash
curl -X POST http://localhost:8000/api/v1/datasets/ \
  -H "Content-Type: application/json" \
  -d '{
    "fqn": "snowflake.sales.public.orders_aggregated",
    "connection_name": "snowflake",
    "database_name": "sales",
    "schema_name": "public",
    "table_name": "orders_aggregated",
    "source_type": "Snowflake",
    "columns": [
      {"name": "customer_id", "type": "INT"},
      {"name": "total_orders", "type": "INT"},
      {"name": "total_amount", "type": "DECIMAL(10,2)"}
    ]
  }'
```

### Using Python

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def create_dataset(fqn, connection_name, database_name, schema_name, table_name, source_type, columns):
    """Create a dataset"""
    url = f"{BASE_URL}/datasets/"
    payload = {
        "fqn": fqn,
        "connection_name": connection_name,
        "database_name": database_name,
        "schema_name": schema_name,
        "table_name": table_name,
        "source_type": source_type,
        "columns": columns
    }
    response = requests.post(url, json=payload)
    return response.json()

# Create datasets
dataset1 = create_dataset(
    fqn="snowflake.sales.public.orders",
    connection_name="snowflake",
    database_name="sales",
    schema_name="public",
    table_name="orders",
    source_type="Snowflake",
    columns=[
        {"name": "order_id", "type": "INT"},
        {"name": "customer_id", "type": "INT"},
        {"name": "order_date", "type": "DATE"},
        {"name": "amount", "type": "DECIMAL(10,2)"}
    ]
)
print(f"Created dataset: {dataset1['id']}")

dataset2 = create_dataset(
    fqn="snowflake.sales.public.orders_clean",
    connection_name="snowflake",
    database_name="sales",
    schema_name="public",
    table_name="orders_clean",
    source_type="Snowflake",
    columns=[
        {"name": "order_id", "type": "INT"},
        {"name": "customer_id", "type": "INT"}
    ]
)
print(f"Created dataset: {dataset2['id']}")

dataset3 = create_dataset(
    fqn="snowflake.sales.public.orders_aggregated",
    connection_name="snowflake",
    database_name="sales",
    schema_name="public",
    table_name="orders_aggregated",
    source_type="Snowflake",
    columns=[
        {"name": "customer_id", "type": "INT"},
        {"name": "total_orders", "type": "INT"}
    ]
)
print(f"Created dataset: {dataset3['id']}")
```

---

## 2. Create Lineage Relationships

### Using curl

Create lineage: orders -> orders_clean
```bash
curl -X POST http://localhost:8000/api/v1/lineage/ \
  -H "Content-Type: application/json" \
  -d '{
    "upstream_dataset_id": 1,
    "downstream_dataset_id": 2
  }'
```

Create lineage: orders_clean -> orders_aggregated
```bash
curl -X POST http://localhost:8000/api/v1/lineage/ \
  -H "Content-Type: application/json" \
  -d '{
    "upstream_dataset_id": 2,
    "downstream_dataset_id": 3
  }'
```

### Using Python

```python
def create_lineage(upstream_id, downstream_id):
    """Create a lineage relationship"""
    url = f"{BASE_URL}/lineage/"
    payload = {
        "upstream_dataset_id": upstream_id,
        "downstream_dataset_id": downstream_id
    }
    response = requests.post(url, json=payload)
    return response.json()

# Create lineages
lineage1 = create_lineage(dataset1['id'], dataset2['id'])
print(f"Created lineage: {lineage1['id']}")

lineage2 = create_lineage(dataset2['id'], dataset3['id'])
print(f"Created lineage: {lineage2['id']}")
```

---

## 3. Get Datasets with Lineage

### Using curl

Get dataset with lineage information:
```bash
curl http://localhost:8000/api/v1/datasets/2/lineage
```

Response shows upstream (orders) and downstream (orders_aggregated) relationships.

### Using Python

```python
def get_dataset_lineage(dataset_id):
    """Get dataset with lineage information"""
    url = f"{BASE_URL}/datasets/{dataset_id}/lineage"
    response = requests.get(url)
    return response.json()

# Get dataset with lineage
full_dataset = get_dataset_lineage(2)
print(f"Dataset: {full_dataset['table_name']}")
print(f"Upstream: {[d['table_name'] for d in full_dataset['upstream_datasets']]}")
print(f"Downstream: {[d['table_name'] for d in full_dataset['downstream_datasets']]}")
```

---

## 4. Search Datasets

### Using curl

Search by table name:
```bash
curl "http://localhost:8000/api/v1/search/?q=orders"
```

Search by column name:
```bash
curl "http://localhost:8000/api/v1/search/?q=customer_id"
```

Search by schema name:
```bash
curl "http://localhost:8000/api/v1/search/?q=public"
```

### Using Python

```python
def search_datasets(query):
    """Search for datasets"""
    url = f"{BASE_URL}/search/"
    params = {"q": query}
    response = requests.get(url, params=params)
    return response.json()

# Search examples
results = search_datasets("orders")
print(f"Found {results['total_results']} results for 'orders'")
for result in results['results']:
    print(f"  - {result['dataset']['table_name']} (priority: {result['priority']})")
```

---

## 5. Test Cycle Detection

Attempting to create a cycle will fail:

### Using curl

```bash
# This will fail because it would create a cycle
curl -X POST http://localhost:8000/api/v1/lineage/ \
  -H "Content-Type: application/json" \
  -d '{
    "upstream_dataset_id": 3,
    "downstream_dataset_id": 1
  }'
```

Response:
```json
{
  "error": "Bad Request",
  "detail": "Adding lineage from 3 to 1 would create a cycle. Dataset 1 is already downstream of 3.",
  "status_code": 400
}
```

### Using Python

```python
# Try to create cycle
try:
    cycle = create_lineage(3, 1)
except Exception as e:
    print(f"Cycle creation failed: {e}")
```

---

## 6. List All Datasets

### Using curl

```bash
curl "http://localhost:8000/api/v1/datasets/?skip=0&limit=100"
```

### Using Python

```python
def list_datasets(skip=0, limit=100):
    """List all datasets"""
    url = f"{BASE_URL}/datasets/"
    params = {"skip": skip, "limit": limit}
    response = requests.get(url, params=params)
    return response.json()

datasets = list_datasets()
print(f"Total datasets: {len(datasets)}")
for ds in datasets:
    print(f"  - {ds['fqn']}")
```

---

## 7. List All Lineages

### Using curl

```bash
curl http://localhost:8000/api/v1/lineage/
```

### Using Python

```python
def list_lineages():
    """List all lineages"""
    url = f"{BASE_URL}/lineage/"
    response = requests.get(url)
    return response.json()

lineages = list_lineages()
print(f"Total lineages: {len(lineages)}")
for lineage in lineages:
    print(f"  - Dataset {lineage['upstream_dataset_id']} -> {lineage['downstream_dataset_id']}")
```

---

## 8. Delete Dataset

### Using curl

```bash
curl -X DELETE http://localhost:8000/api/v1/datasets/3
```

### Using Python

```python
def delete_dataset(dataset_id):
    """Delete a dataset"""
    url = f"{BASE_URL}/datasets/{dataset_id}"
    response = requests.delete(url)
    print(f"Delete response: {response.status_code}")

delete_dataset(3)
```

---

## Complete Example Script

A complete Python script that demonstrates all functionality:

```python
#!/usr/bin/env python3
"""Complete example of using Metadata Service API"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000/api/v1"

def main():
    print("=" * 60)
    print("Metadata Service - Complete Example")
    print("=" * 60)
    print()
    
    # 1. Create datasets
    print("1️⃣  Creating datasets...")
    datasets = []
    dataset_specs = [
        {
            "fqn": "snowflake.sales.raw.orders",
            "connection": "snowflake",
            "database": "sales",
            "schema": "raw",
            "table": "orders",
            "source_type": "Snowflake"
        },
        {
            "fqn": "snowflake.sales.processed.orders_clean",
            "connection": "snowflake",
            "database": "sales",
            "schema": "processed",
            "table": "orders_clean",
            "source_type": "Snowflake"
        },
        {
            "fqn": "snowflake.sales.analytics.daily_orders",
            "connection": "snowflake",
            "database": "sales",
            "schema": "analytics",
            "table": "daily_orders",
            "source_type": "Snowflake"
        }
    ]
    
    for spec in dataset_specs:
        response = requests.post(f"{BASE_URL}/datasets/", json={
            "fqn": spec["fqn"],
            "connection_name": spec["connection"],
            "database_name": spec["database"],
            "schema_name": spec["schema"],
            "table_name": spec["table"],
            "source_type": spec["source_type"],
            "columns": [
                {"name": "id", "type": "INT"},
                {"name": "created_at", "type": "TIMESTAMP"}
            ]
        })
        datasets.append(response.json())
        print(f"   ✓ Created: {spec['fqn']}")
    print()
    
    # 2. Create lineage
    print("2️⃣  Creating lineage relationships...")
    lineages = []
    lineage_specs = [
        (datasets[0]['id'], datasets[1]['id']),
        (datasets[1]['id'], datasets[2]['id'])
    ]
    
    for upstream_id, downstream_id in lineage_specs:
        response = requests.post(f"{BASE_URL}/lineage/", json={
            "upstream_dataset_id": upstream_id,
            "downstream_dataset_id": downstream_id
        })
        lineages.append(response.json())
        print(f"   ✓ Created: Dataset {upstream_id} -> Dataset {downstream_id}")
    print()
    
    # 3. Get dataset with lineage
    print("3️⃣  Getting dataset with lineage information...")
    response = requests.get(f"{BASE_URL}/datasets/{datasets[1]['id']}/lineage")
    dataset_with_lineage = response.json()
    print(f"   Table: {dataset_with_lineage['table_name']}")
    print(f"   Upstream: {', '.join([d['table_name'] for d in dataset_with_lineage['upstream_datasets']])}")
    print(f"   Downstream: {', '.join([d['table_name'] for d in dataset_with_lineage['downstream_datasets']])}")
    print()
    
    # 4. Search
    print("4️⃣  Searching for datasets...")
    queries = ["orders", "clean", "analytics"]
    for query in queries:
        response = requests.get(f"{BASE_URL}/search/?q={query}")
        results = response.json()
        print(f"   Query '{query}': Found {results['total_results']} results")
    print()
    
    # 5. Test cycle detection
    print("5️⃣  Testing cycle detection...")
    try:
        response = requests.post(f"{BASE_URL}/lineage/", json={
            "upstream_dataset_id": datasets[2]['id'],
            "downstream_dataset_id": datasets[0]['id']
        })
        if response.status_code != 201:
            print(f"   ✓ Cycle detected and rejected: {response.json()['detail']}")
    except Exception as e:
        print(f"   ⚠ Error: {e}")
    print()
    
    print("=" * 60)
    print("✅ Example completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

Save as `example.py` and run:
```bash
python example.py
```

---

## Performance Tips

1. **Pagination**: Always use limits when listing datasets
   ```bash
   curl "http://localhost:8000/api/v1/datasets/?limit=50&skip=0"
   ```

2. **Search Optimization**: Queries are case-insensitive
   ```bash
   curl "http://localhost:8000/api/v1/search/?q=ORDERS"  # Same as "orders"
   ```

3. **Batch Operations**: Create multiple datasets before establishing lineage

---

## Error Handling

Common error responses:

### 404 Not Found
```json
{"detail": "Dataset with ID 999 not found", "status_code": 404}
```

### 409 Conflict (Duplicate FQN)
```json
{"detail": "Dataset with FQN 'snowflake.sales.public.orders' already exists", "status_code": 409}
```

### 400 Bad Request (Cycle Detection)
```json
{
  "error": "Bad Request",
  "detail": "Adding lineage from 2 to 1 would create a cycle.",
  "status_code": 400
}
```

### 422 Unprocessable Entity (Validation Error)
```json
{
  "error": "Validation Error",
  "details": [
    {"loc": ["body", "fqn"], "msg": "FQN must be in format: connection.db.schema.table"}
  ]
}
```

---

## Need Help?

- Check API docs: http://localhost:8000/docs
- Read README.md for architecture details
- Run tests: `pytest tests/ -v`
- Check logs: `docker-compose logs -f api`
