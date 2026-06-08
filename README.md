# NLP Knowledge Discovery System

**For**: Desa Punggul Village, Bali, Indonesia

## Project Overview
A web application that automatically extracts structured knowledge from PDF documents (reports, regulations, activities) and stores them in a MySQL database using ML pipelines.

## Tech Stack
- **Backend**: Laravel 11 (REST API)
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Database**: MySQL 8
- **Authentication**: Laravel Sanctum (token-based)
- **ML Service**: Python Flask API (separate service on port 5000)

## Project Structure
```
stage project/
├── backend/          # Laravel 11 REST API
├── frontend/         # React 18 + TypeScript
├── ml-service/       # Python Flask ML Pipelines
├── docs/             # Documentation
├── docker-compose.yml
└── README.md
```

## Features

### User Roles
- **ADMIN**: Full access (upload, validate, manage all data)
- **PUBLIC**: Read-only access to public knowledge items

### ML Pipelines
1. **Pipeline 0**: Document Router - Detects PDF type (native/scanned), applies OCR if needed
2. **Pipeline 1**: Knowledge Extraction - Extracts IF-THEN rules using spaCy + LLM
3. **Pipeline 2**: Domain Classification - Classifies knowledge by domain (Naive Bayes + Decision Tree)

### Database Tables (6)
- `knowledge_rules` - IF-THEN rule headers
- `rule_condition_facts` - IF conditions
- `rule_action_facts` - THEN actions
- `fact_values` - Continuous/categorical values
- `knowledge_facts` - Subject-relation-object triplets
- `document_log` - Audit trail

### Key Fields
- `domain`: social | economy | infrastructure | health | culture_art
- `visibility`: public | private
- `status`: validated | pending_review
- `logical_operator`: AND | OR | NULL
- `group_id`: Grouping for conditions/actions

## Quick Start

### Prerequisites
- PHP 8.3+
- Node.js 18+
- Python 3.10+
- MySQL 8+
- Composer
- npm/yarn

### Installation

#### 1. Backend (Laravel)
```bash
cd backend
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate
php artisan db:seed
php artisan serve
```

#### 2. Frontend (React)
```bash
cd frontend
npm install
npm run dev
```

#### 3. ML Service (Flask)
```bash
cd ml-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## API Communication Flow
```
React Frontend
    ↓
Laravel REST API (port 8000)
    ↓ (triggers)
Python Flask API (port 5000)
    ↓
ML Pipelines (NLP processing)
    ↓
MySQL Database
```

## Pages (React)
- Login (public)
- Dashboard (stats, charts)
- Upload Document (PDF/CSV/Excel)
- Knowledge Rules (filterable table)
- Knowledge Facts (filterable table)
- Pending Review (admin only)
- Analytics (admin only)
- Settings (admin only)

## Documentation
See `/docs` folder for detailed documentation on:
- Database schema
- API endpoints
- ML pipeline details
- Setup instructions

## Notes
- REST API only (no Blade views)
- CORS enabled for React frontend
- Token-based authentication with Sanctum
- ML service runs on separate port (5000)

## Author
Development Team - Desa Punggul, Bali, Indonesia
Date: June 2026
