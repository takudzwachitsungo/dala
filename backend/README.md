# Dala Mental Health Platform - Backend

Privacy-first mental health support platform with AI companion, built with FastAPI, LangGraph, and PostgreSQL.

## Features

- **Anonymous Sessions**: Users can start without registration
- **AI Companion (Dala)**: Conversation modes (Listen, Reflect, Ground) with GroqCloud/MiniMax
- **Sentiment Analysis**: Real-time emotion detection and crisis support
- **Mood Tracking**: Daily mood check-ins with history visualization
- **Profile & Milestones**: Streaks, badges, and progress tracking

## Tech Stack

- **Framework**: FastAPI 0.109
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Cache**: Redis
- **AI/LLM**: LangGraph + GroqCloud API (primary) + MiniMax API (fallback)
- **Sentiment**: Transformers (HuggingFace)
- **Auth**: JWT with python-jose

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

1. Clone the repository and navigate to backend:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Update `.env` with your credentials:
- Database credentials
- Redis host/port
- JWT secret key (generate with: `openssl rand -hex 32`)
- GroqCloud API key
- (Optional) MiniMax API key

6. Initialize database:
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Running the Server

Development mode (with auto-reload):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Access the API at: http://localhost:8000

API docs available at: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /api/v1/auth/anonymous-session` - Create anonymous session
- `POST /api/v1/auth/register` - Register user account
- `POST /api/v1/auth/login` - Login

### Conversations (AI Chat)
- `POST /api/v1/conversations` - Create conversation
- `GET /api/v1/conversations` - List conversations
- `GET /api/v1/conversations/{id}/messages` - Get messages
- `WS /api/v1/ws/chat` - WebSocket for real-time chat

### Mood Tracking
- `POST /api/v1/mood` - Log mood entry
- `GET /api/v1/mood/history` - Get mood history

### Profile
- `GET /api/v1/profile` - Get user profile
- `PATCH /api/v1/profile` - Update profile
- `GET /api/v1/profile/milestones` - Get milestones

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Config, security
│   ├── db/               # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   │   └── ai/           # LangGraph, LLM, sentiment
│   └── utils/            # Utilities
├── alembic/              # Database migrations
├── requirements.txt
└── .env
```

## Development

### Database Migrations

Create new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

### Testing

(TODO: Add test suite)

## License

Proprietary - Dala Mental Health Platform
