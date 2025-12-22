# Quick Start Guide - Dala Backend

## Option 1: Docker (Recommended)

### Start Everything with Docker Compose
```bash
cd backend

# Create .env file
cp .env.example .env

# Edit .env and add your GROQ_API_KEY
# The rest can use defaults for local development

# Start all services (PostgreSQL, Redis, Backend)
docker-compose up
```

That's it! The backend will be available at http://localhost:8000

API docs: http://localhost:8000/docs

## Option 2: Manual Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (running)
- Redis 7+ (running)

### Steps

1. **Run setup script:**
```bash
cd backend
./setup.sh
```

2. **Activate virtual environment:**
```bash
source venv/bin/activate
```

3. **Create .env file and add your keys:**
```bash
# Copy from .env.example
cp .env.example .env

# Edit .env and set:
# - GROQ_API_KEY (get from https://console.groq.com)
# - Database credentials (if different from defaults)
```

4. **Create database:**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE dala_db;
CREATE USER dala_user WITH PASSWORD 'dala_password';
GRANT ALL PRIVILEGES ON DATABASE dala_db TO dala_user;
\q
```

5. **Run migrations:**
```bash
alembic upgrade head
```

6. **Start the server:**
```bash
uvicorn app.main:app --reload
```

Server will start at: http://localhost:8000

## Test the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Create Anonymous Session
```bash
curl -X POST http://localhost:8000/api/v1/auth/anonymous-session \
  -H "Content-Type: application/json" \
  -d '{"privacy_consent": true}'
```

Save the `access_token` from the response.

### 3. Log a Mood Entry
```bash
curl -X POST http://localhost:8000/api/v1/mood \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "mood_score": 7,
    "emotions": ["calm", "focused"],
    "notes": "Had a good day"
  }'
```

### 4. Get Profile
```bash
curl http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Next Steps

The MVP foundation is ready with:
- ✅ Authentication (anonymous + registered users)
- ✅ Mood tracking with streaks
- ✅ Profile with milestones
- ✅ Database models for conversations

**Still to implement:**
- LangGraph AI conversation workflow
- GroqCloud/MiniMax LLM integration
- WebSocket streaming
- Sentiment analysis & crisis detection
- Redis caching layer

## Troubleshooting

### PostgreSQL connection error
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in .env match your database

### Redis connection error
- Check Redis is running: `redis-cli ping`
- Should return: `PONG`

### Module not found
- Ensure virtual environment is activated
- Run: `pip install -r requirements.txt`

## API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
