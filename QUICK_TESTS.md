# ⚡ Quick Test Commands (Copy & Paste)

## 1️⃣ HEALTH CHECK
```powershell
curl http://localhost:8000/health
```

---

## 2️⃣ CREATE DATASET #1
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
        @{ name = "name"; type = "VARCHAR(255)" }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/datasets/" `
  -Method POST -Headers @{"Content-Type"="application/json"} `
  -Body $body -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 3️⃣ CREATE DATASET #2
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
        @{ name = "customer_id"; type = "INT" }
    )
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/datasets/" `
  -Method POST -Headers @{"Content-Type"="application/json"} `
  -Body $body -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 4️⃣ LIST DATASETS
```powershell
Invoke-WebRequest "http://localhost:8000/api/v1/datasets/" `
  -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 5️⃣ GET DATASET ID 1
```powershell
Invoke-WebRequest "http://localhost:8000/api/v1/datasets/1" `
  -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 6️⃣ CREATE LINEAGE (1 → 2)
```powershell
$body = @{
    upstream_dataset_id = 1
    downstream_dataset_id = 2
} | ConvertTo-Json

Invoke-WebRequest "http://localhost:8000/api/v1/lineage/" `
  -Method POST -Headers @{"Content-Type"="application/json"} `
  -Body $body -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 7️⃣ TEST CYCLE (Should FAIL)
```powershell
$body = @{
    upstream_dataset_id = 2
    downstream_dataset_id = 1
} | ConvertTo-Json

Invoke-WebRequest "http://localhost:8000/api/v1/lineage/" `
  -Method POST -Headers @{"Content-Type"="application/json"} `
  -Body $body -UseBasicParsing | % Content | ConvertFrom-Json
```

Expected: **400 error** with "Cycle detected"

---

## 8️⃣ GET DATASET WITH LINEAGE
```powershell
Invoke-WebRequest "http://localhost:8000/api/v1/datasets/1/lineage" `
  -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 9️⃣ SEARCH
```powershell
# Search all types
Invoke-WebRequest "http://localhost:8000/api/v1/search/?q=customers" `
  -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 🔟 LIST LINEAGES
```powershell
Invoke-WebRequest "http://localhost:8000/api/v1/lineage/" `
  -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 1️⃣1️⃣ DELETE LINEAGE
```powershell
Invoke-WebRequest "http://localhost:8000/api/v1/lineage/1" `
  -Method DELETE -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 1️⃣2️⃣ DELETE DATASET
```powershell
Invoke-WebRequest "http://localhost:8000/api/v1/datasets/1" `
  -Method DELETE -UseBasicParsing | % Content | ConvertFrom-Json
```

---

## 🚀 EASIEST WAY (NO COMMANDS!)
```
Open this in your browser:
http://localhost:8000/docs
```

Click "Try it out" on any endpoint and test directly in the UI! ✨

