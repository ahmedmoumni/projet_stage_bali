# Quickstart Guide

## 📋 Prerequisites
- PHP 8.3+ ✓ 
- Node.js 18+ ✓ (v20.19.6)
- Python 3.10+ ✓ (v3.12.3)
- MySQL 8+ ✓
- Composer ✓

All installed and configured!

## 🚀 Quick Start

### Option 1: Run All Services at Once
```bash
cd "/home/ahmed/Bureau/stage project"
./start-dev.sh
```

### Option 2: Run Services Individually

#### 1. Start MySQL
```bash
sudo systemctl start mysql
```

#### 2. Start Laravel (Port 8000)
```bash
cd backend
php artisan serve --port=8000
```

#### 3. Start Python ML Service (Port 5000)
```bash
cd ml-service
source venv/bin/activate
python app.py
```

#### 4. Start React Dev Server (Port 5173)
```bash
cd frontend
npm run dev
```

## 🌐 Access Points
- **Frontend**: http://localhost:5173
- **Laravel API**: http://localhost:8000
- **ML Service**: http://localhost:5000
- **MySQL**: localhost:3306 (nlp_user / NLP@User123)

## 📁 Project Structure
```
stage project/
├── backend/           # Laravel 11 REST API
│   ├── .env
│   ├── database/
│   ├── routes/api.php
│   ├── app/Http/Controllers/
│   └── app/Models/
├── frontend/          # React 18 + TypeScript + Vite
│   ├── .env
│   ├── src/
│   │   ├── api/client.ts
│   │   └── components/
│   └── tailwind.config.js
├── ml-service/        # Python Flask API
│   ├── .env
│   ├── venv/
│   ├── app.py
│   └── requirements.txt
└── docs/              # Documentation

```

## 🔧 Configuration Files

### Backend (.env)
```
APP_NAME="NLP Knowledge Discovery System"
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=nlp_knowledge_db
DB_USERNAME=nlp_user
DB_PASSWORD=NLP@User123

SANCTUM_STATEFUL_DOMAINS=localhost:5173
```

### Frontend (.env)
```
VITE_LARAVEL_API=http://localhost:8000/api
VITE_ML_SERVICE=http://localhost:5000/api
```

### ML Service (.env)
```
REACT_URL=http://localhost:5173
LARAVEL_URL=http://localhost:8000
API_PORT=5000
```

## 📦 Installed Packages

### Backend (Laravel 11)
- `laravel/sanctum` - Token-based authentication
- Core: migrations, models, controllers

### Frontend (React 18)
- `react` & `react-dom`
- `typescript`
- `tailwindcss` & `postcss`
- `axios` - HTTP client

### ML Service (Python)
- `flask` - Web framework
- `flask-cors` - CORS support
- `spacy` - NLP
- `scikit-learn` - ML
- `pdf2image` & `pytesseract` - PDF processing
- `numpy` - Numerical computing

## 🗄️ Database

**Created Database**: `nlp_knowledge_db`
**User**: `nlp_user` (password: `NLP@User123`)

### Tables (Auto-created by Laravel migrations)
- `users` - User accounts
- `personal_access_tokens` - Sanctum tokens
- `cache` - Cache data
- `jobs` - Queued jobs

### Custom Tables (To be created)
- `knowledge_rules`
- `rule_condition_facts`
- `rule_action_facts`
- `fact_values`
- `knowledge_facts`
- `document_log`

## ✅ Verification Checklist

### Backend
```bash
cd backend
php artisan tinker  # Test Laravel
> User::count()     # Should return 0
```

### Frontend
```bash
cd frontend
npm list            # Check dependencies
npm run build       # Test build
```

### ML Service
```bash
cd ml-service
source venv/bin/activate
python -c "import flask; print(flask.__version__)"
```

### Database
```bash
mysql -u nlp_user -p"NLP@User123" -e "USE nlp_knowledge_db; SHOW TABLES;"
```

## 🔗 API Communication Flow

```
React Frontend (5173)
    ↓ (GET/POST JSON)
Laravel API (8000)
    ↓ (HTTP requests)
Python Flask (5000)
    ↓ (ML processing)
MySQL Database (3306)
```

## 📝 Next Steps

1. **Create Database Migrations** - Define the 6 custom tables
2. **Create Seeders** - Add sample data
3. **Build Authentication Flow** - Login/Register with Sanctum
4. **Create React Components** - Pages: Login, Dashboard, Upload, etc.
5. **Implement ML Pipelines** - Pipelines 0, 1, 2
6. **Test API Integration** - End-to-end testing

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000  # Or :5000, :5173

# Kill process
sudo kill -9 <PID>
```

### Laravel Connection Error
```bash
# Check MySQL
sudo systemctl status mysql

# Verify .env credentials
cat backend/.env | grep DB_
```

### ML Service Import Error
```bash
cd ml-service
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### React Build Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

**Configured on**: June 3, 2026
**Status**: ✅ Ready for development
