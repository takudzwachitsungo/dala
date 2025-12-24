# Dala - Mental Health & Faith Companion

A Christian-focused mental health companion app with AI support, mood tracking, and safety planning features.

## Features

- 🤖 AI Companion (Dala) - Christian-focused conversational support
- 📊 Mood Tracking - Daily mood logging with history visualization
- 📖 Daily Verses - Scripture and devotionals based on your mood
- 🛡️ Safety Plan - Crisis management and coping strategies
- 👥 Circles & Paths - Community support and guided journeys
- 🙏 Prayer & Reflection - Journal entries and spiritual growth

## Tech Stack

**Backend:**
- FastAPI (Python 3.11)
- PostgreSQL 15
- Redis 7
- SQLAlchemy (async)
- Alembic migrations
- LangGraph for AI conversations
- Claude (Anthropic) for AI responses

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- Axios

## Local Development

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/takudzwachitsungo/dala.git
cd dala
```

2. **Backend Setup:**
```bash
cd backend
cp .env.example .env
# Edit .env with your configuration
docker-compose up -d
```

The backend will be available at `http://localhost:8000`

3. **Frontend Setup:**
```bash
cd ui
npm install
cp .env.example .env
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Digital Ocean App Platform

1. Fork/clone this repository
2. Connect your Digital Ocean account to GitHub
3. Create a new App from the `.do/app.yaml` spec
4. Add environment variables:
   - `JWT_SECRET_KEY` - Random secure string
   - `ANTHROPIC_API_KEY` - Your Claude API key
5. Deploy!

### Environment Variables

See `backend/.env.example` for required backend variables.
See `ui/.env.example` for required frontend variables.

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
dala/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── db/           # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic & AI
│   ├── alembic/          # Database migrations
│   └── Dockerfile
├── ui/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── api/          # API client
│   └── package.json
└── docker-compose.yml
```

## Contributing

This is a personal project, but feedback and suggestions are welcome!

## License

MIT License - feel free to use this for learning or personal projects.

## Support

For Zimbabwe-specific crisis support:
- Childline Zimbabwe: 116 (toll-free)
- Befrienders Zimbabwe: +263 9 65000
- Emergency Services: 999 or 112

---

Built with ❤️ for mental health and spiritual wellness.
