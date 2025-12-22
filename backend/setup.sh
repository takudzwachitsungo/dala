#!/bin/bash

# Dala Backend Setup Script

echo "🚀 Starting Dala Backend Setup..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Update .env with generated key (macOS compatible)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    fi
    
    echo "✅ .env file created with generated SECRET_KEY"
    echo "⚠️  Please update GROQ_API_KEY and database credentials in .env"
else
    echo "✅ .env file already exists"
fi

# Check if Python venv exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your API keys and database credentials"
echo "2. Start PostgreSQL and Redis (or run: docker-compose up -d postgres redis)"
echo "3. Run migrations: alembic upgrade head"
echo "4. Start the server: uvicorn app.main:app --reload"
echo ""
echo "Or use Docker Compose: docker-compose up"
