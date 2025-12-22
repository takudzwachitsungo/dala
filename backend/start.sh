#!/bin/bash

echo "🚀 Starting Dala Backend..."

# Step 1: Start just Postgres and Redis
echo "📦 Starting PostgreSQL and Redis..."
docker-compose up -d postgres redis

# Wait for services to be healthy
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Check if containers are running
if docker ps | grep -q dala_postgres && docker ps | grep -q dala_redis; then
    echo "✅ PostgreSQL and Redis are running"
else
    echo "❌ Failed to start databases"
    exit 1
fi

# Step 2: Set up Python environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

# Step 3: Run migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Step 4: Start backend
echo "🚀 Starting FastAPI server..."
echo ""
echo "✨ Server will be available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
