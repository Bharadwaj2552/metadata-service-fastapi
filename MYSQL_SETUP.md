# 🗄️ How to Run MySQL Server

## Option 1️⃣ : Using Windows Installer (Easiest)

### Step 1: Download MySQL
1. Visit: https://dev.mysql.com/downloads/mysql/
2. Download "MySQL Community Server" (8.0+)
3. Choose Windows installer

### Step 2: Install
1. Run the installer `.msi` file
2. Choose typical setup
3. Follow the configuration wizard
4. **Important**: Remember the root password you set!

### Step 3: Start MySQL Service
Open PowerShell as **Administrator**:

```powershell
# Start MySQL service
net start MySQL80

# Stop MySQL service
net stop MySQL80

# Check if running
Get-Service MySQL80 | Select-Object Status
```

**Expected output:** `Status : Running`

### Step 4: Verify Connection
```powershell
# Test connection
mysql -u root -p
# Enter your password when prompted
```

---

## Option 2️⃣ : Using Docker (Recommended if available)

### Prerequisites
- Docker Desktop installed (you have it!)
- Command: `docker -v` returns version

### Step 1: Create `docker-compose.yml` for Just MySQL

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: metadata_mysql
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_USER: metadata_user
      MYSQL_PASSWORD: metadata_password
      MYSQL_DATABASE: metadata_db
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

volumes:
  mysql_data:
```

### Step 2: Start MySQL Container

```powershell
# Navigate to project directory
cd "c:\Users\annep\OneDrive\Desktop\My Learnings\File\metadata-service"

# Start MySQL only
docker-compose up -d mysql

# Expected output:
# Creating metadata_mysql ... done
```

### Step 3: Check if Running

```powershell
docker ps

# Look for: metadata_mysql  mysql:8.0  Up X seconds
```

### Step 4: Stop MySQL

```powershell
docker-compose down

# Or just stop without removing
docker-compose stop
```

---

## Option 3️⃣ : Using Chocolatey (If installed)

```powershell
# Install MySQL
choco install mysql -y

# Start service
net start MySQL80
```

---

## Option 4️⃣ : Using Windows Subsystem for Linux (WSL)

```bash
# Inside WSL terminal
sudo apt-get update
sudo apt-get install mysql-server -y

# Start MySQL
sudo service mysql start

# Check status
sudo service mysql status
```

---

## ✅ Verify MySQL is Running

### Test 1: PowerShell Check
```powershell
# Check Windows service
Get-Service MySQL80 | Select-Object Status
```

**Expected:** `Status : Running`

### Test 2: Connection Test
```powershell
# Try connecting
mysql -u root -p

# Type your password, should see:
# mysql>
```

### Test 3: From Your App
```powershell
cd "c:\Users\annep\OneDrive\Desktop\My Learnings\File\metadata-service"

& "c:\Users\annep\OneDrive\Desktop\My Learnings\File\.venv\Scripts\python.exe" -c "
from app.core.database import get_engine
try:
    engine = get_engine()
    engine.connect()
    print('✅ Database connected successfully!')
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

---

## 🔧 Troubleshooting

### Port 3306 Already in Use
```powershell
# Find what's using port 3306
netstat -ano | findstr :3306

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in .env to 3307
DB_PORT=3307
```

### MySQL Service Won't Start
```powershell
# Try repairing installation
# Run installer again and choose "Repair"

# Or restart the service
net stop MySQL80
net start MySQL80
```

### Forgot Root Password
```powershell
# Reset MySQL root password
# (Complex process - reinstall is easier)

# Or use Docker and just recreate container
docker-compose down
docker-compose up -d mysql
# New default: root/root_password
```

---

## 🚀 Quick Start (Copy-Paste)

### If Using Windows Service:
```powershell
# PowerShell as Administrator
net start MySQL80

# Verify
Get-Service MySQL80
```

### If Using Docker:
```powershell
# Make sure Docker is running first!
# Then in your project directory:

docker-compose up -d mysql

# Verify
docker ps | findstr mysql
```

### Then Start Your App:
```powershell
cd "c:\Users\annep\OneDrive\Desktop\My Learnings\File\metadata-service"

& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# ✅ Database initialized successfully
```

---

## 🧪 Test the Connection

Once MySQL is running:

```powershell
# 1. Check from terminal
mysql -u metadata_user -p

# Password: metadata_password
# Should see: mysql>

# 2. Create a test database
CREATE DATABASE test_db;
SHOW DATABASES;

# 3. Exit
EXIT;
```

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| "Can't connect to MySQL server" | Make sure service is running: `net start MySQL80` |
| Port 3306 busy | Change port in `.env` or kill process using it |
| "Access denied" | Check username/password in `.env` matches MySQL setup |
| Docker container exits | Check logs: `docker logs metadata_mysql` |

---

## 📋 Your Current `.env` Settings

Check yours matches (or update MySQL with these values):

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=metadata_user
DB_PASSWORD=metadata_password
DB_NAME=metadata_db
```

If using Docker with my config above, these match exactly! ✅

---

## ✨ Recommended Setup

**For development on Windows:**
1. Use **Docker** (Option 2) - Easiest to manage
2. Or **Windows Installer** (Option 1) - Direct control

**Steps:**
```powershell
# 1. Start MySQL (choose one)
docker-compose up -d mysql      # Docker method
# OR
net start MySQL80               # Windows Service method

# 2. Wait a few seconds

# 3. Start your FastAPI app
cd metadata-service
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Test in browser
# http://localhost:8000/docs
```

Done! 🎉
