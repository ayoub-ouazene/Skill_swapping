# SkillSwap Backend 🚀

**A peer-to-peer skill exchange platform powered by AI, Time Credits economy, and smart skill matching.**

SkillSwap is a comprehensive backend API built with **FastAPI** and **PostgreSQL (Neon)**, enabling users to teach and learn skills from each other while earning and spending Time Credits. The platform features AI-driven semantic search for skill matching, AI vision for certificate verification, and intelligent chatbot assistance.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Setup & Installation](#local-setup--installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Project Structure](#project-structure)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Core Modules & Services](#core-modules--services)
- [API Endpoints Overview](#api-endpoints-overview)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Core Platform Features
- **User Account Management**: Registration, authentication, and user profiles with bio support
- **Skill Listing & Discovery**: Browse and search available skills with rich filtering
- **Time Credit Economy**: Earn credits by teaching, spend by learning (base allocation: 2.0 credits per new user)
- **Session Management**: Schedule, track, and rate skill-sharing sessions
- **Internal Certification**: Automatic certificate generation upon session completion
- **Ratings & Reputation**: User ratings and reputation tracking based on session quality
- **User Matching**: Smart matching algorithm to connect learners with appropriate teachers

### AI-Powered Features
- **Semantic Skill Matching**: AI embeddings (HuggingFace `all-MiniLM-L6-v2`) for intelligent skill search and recommendation
- **AI Vision Certificate Analysis**: Groq Vision API for automated external certificate verification and validation
- **Smart Chatbot**: Groq LLaMA-powered personal assistant for:
  - Contextual help and guidance
  - Skill recommendations
  - Session planning
  - Platform assistance
- **Embedding Storage**: PostgreSQL vector database integration (`pgvector`) for fast similarity searches

### Additional Features
- **Email Notifications**: Resend email service integration for transactional emails
- **PDF Generation & Parsing**: FPDF2 and PyMupDF for certificate generation and analysis
- **JWT Authentication**: Secure token-based authentication with 7-day expiration
- **CORS Support**: Full cross-origin resource sharing for frontend integration
- **Health Monitoring**: Built-in health check endpoints for system status

---

## 🛠️ Tech Stack

### Backend Framework & Core
| Component | Technology | Version |
|-----------|-----------|---------|
| **Web Framework** | FastAPI | Latest |
| **Server** | Uvicorn | Latest |
| **Python** | Python | 3.9+ |
| **Request Validation** | Pydantic | Latest |

### Database & Persistence
| Component | Technology | Details |
|-----------|-----------|---------|
| **Primary Database** | PostgreSQL (Neon) | Serverless, pooled connections |
| **ORM** | SQLAlchemy | 2.x with async support |
| **Vector DB** | pgvector | For AI embeddings (384-dimensional vectors) |
| **Connection String** | psycopg2 | Binary Python driver for PostgreSQL |

### AI & Machine Learning
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Embeddings Model** | Sentence-Transformers | `all-MiniLM-L6-v2` (384-dim vectors) |
| **LLM Provider** | Groq | `llama-3.1-8b-instant` for chatbot & `llama-4-scout-17b` for vision |
| **Vision Analysis** | Groq Vision API | Certificate and document OCR/analysis |
| **Search Optimization** | Vector Similarity | PostgreSQL pgvector for K-NN search |

### Authentication & Security
| Component | Technology | Details |
|-----------|-----------|---------|
| **Password Hashing** | bcrypt | 4.0+, `passlib` incompatible |
| **JWT Tokens** | python-jose | HS256 algorithm, 7-day expiration |
| **Encryption** | cryptography | For JWT signing and verification |

### File & Document Processing
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **PDF Generation** | FPDF2 | Create certificate PDFs |
| **PDF Reading** | PyMupDF (fitz) & pdfplumber | Extract metadata and text from PDFs |

### Email Service
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Email Delivery** | Resend | Transactional email API |

### Utilities
| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Configuration** | python-dotenv | Load environment variables from `.env` |
| **File Upload** | python-multipart | Handle multipart form data |
| **Email Validation** | email-validator | Validate and normalize email addresses |

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed and configured:

### System Requirements
- **Python**: 3.9 or higher
- **PostgreSQL Client**: psycopg2 (included via requirements)
- **Operating System**: Windows, macOS, or Linux

### External Accounts & API Keys Required

1. **Neon PostgreSQL Database**
   - Visit: [neon.tech](https://neon.tech/)
   - Create a free serverless PostgreSQL database
   - Obtain your connection string (DATABASE_URL)

2. **Google Gemini API Key**
   - Visit: [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key
   - Used for (future) advanced AI features

3. **Groq API Key**
   - Visit: [console.groq.com](https://console.groq.com/)
   - Create a new API key
   - Used for LLaMA-based chatbot and vision analysis

4. **Email Service (Resend)**
   - Visit: [resend.com](https://resend.com/)
   - Create an account
   - Obtain your API key (optional if not using email features)

5. **Gmail App Password** (Optional - for email notifications)
   - Configure via Google Account settings
   - Generate app-specific password for EMAIL_PASSWORD

---

## 🚀 Local Setup & Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/ayoub-ouazene/Skill_swapping.git
cd Skill_swapping/backend
```

### Step 2: Create Virtual Environment

#### On Windows (PowerShell or CMD):
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected installation output:
```
Successfully installed fastapi uvicorn sqlalchemy psycopg2-binary pgvector 
sentence-transformers groq google-genai python-dotenv bcrypt python-jose 
fpdf2 pdfplumber pymupdf resend [and dependencies...]
```

### Step 4: Configure Environment Variables

Create a `.env` file in the `backend/` directory with the following content:

```env
# Database Connection String (from Neon Dashboard)
DATABASE_URL="postgresql://neondb_owner:your_password@ep-xxxxx.region.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Groq API Key (for LLaMA chatbot and vision)
GROQ_API_KEY="gsk_your_groq_api_key_here"

# Google Gemini API Key (for future AI features)
GEMINI_API_KEY="AIzaSy_your_gemini_key_here"

# JWT Secret (change to a secure random string in production)
JWT_SECRET_KEY="your-super-secret-jwt-key-change-in-production"

# Email Configuration
EMAIL_SENDER="your-email@gmail.com"
EMAIL_PASSWORD="your-app-password-from-gmail"

# Resend Email Service (optional)
RESEND_API_KEY="re_your_resend_api_key_here"
```

### Step 5: Verify Environment Setup

```bash
python -c "import fastapi; import sqlalchemy; import sentence_transformers; print('✅ All imports successful!')"
```

---

## 📝 Environment Variables Reference

| Variable | Example Value | Required | Purpose |
|----------|---------------|----------|---------|
| `DATABASE_URL` | `postgresql://user:pass@host/db?sslmode=require` | ✅ Yes | PostgreSQL connection string from Neon |
| `GROQ_API_KEY` | `gsk_ZR0d4MfMb1dfKMm...` | ✅ Yes | Groq API key for LLaMA models |
| `GEMINI_API_KEY` | `AIzaSyAuelI8REnpe...` | ❌ Optional | Google Gemini API key for future features |
| `JWT_SECRET_KEY` | `my-super-secret-key` | ❌ Optional | JWT signing key (auto-generated if missing) |
| `EMAIL_SENDER` | `your-email@gmail.com` | ❌ Optional | Sender email address for notifications |
| `EMAIL_PASSWORD` | `app-password-xyz` | ❌ Optional | App password for email service |
| `RESEND_API_KEY` | `re_xxxxx_xxxxx` | ❌ Optional | Resend email service API key |

---

## 🗄️ Database Setup

### Automatic Schema Creation (Option 1 - Recommended)

When you run the server, FastAPI will automatically create all tables. To enable this:

1. Uncomment this line in `app/main.py`:
```python
Base.metadata.create_all(bind=engine)
```

2. Run the server once to initialize the database

### Manual SQL Setup (Option 2)

If you prefer manual control:

1. Go to your Neon Dashboard → SQL Editor
2. Run the migration scripts in order:
   - [001_add_users_bio.sql](migrations/001_add_users_bio.sql)
   - [002_chat_tables.sql](migrations/002_chat_tables.sql)

### Database Tables Overview

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | User accounts and profiles | id, email, first_name, last_name, bio, credit, rating |
| `skills` | Skills offered by users | id, user_id, skill_name, embedding (vector) |
| `external_certificates` | User-uploaded certificates | id, user_id, skill_id, document_url |
| `sessions` | Skill-sharing sessions | id, teacher_id, student_id, skill_id, status, duration_hours, rating |
| `internal_certificates` | Auto-generated session certificates | id, session_id, student_id, teacher_id, duration_hours |
| `chat_conversations` | Chat conversation history | id, user_id, title |
| `chat_messages` | Individual chat messages | id, conversation_id, role, content, timestamp |

---

## 📂 Project Structure

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization, routers, middleware
│   ├── database.py             # SQLAlchemy engine, session, and Base class
│   ├── models.py               # SQLAlchemy ORM models (User, Skill, Session, etc.)
│   ├── schemas.py              # Pydantic request/response models
│   ├── deps.py                 # Dependency injection (get_current_user, etc.)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── security.py         # JWT token creation, password hashing/verification
│   │
│   ├── routers/                # API endpoint handlers
│   │   ├── __init__.py
│   │   ├── auth.py             # Registration, login (/auth/register, /auth/login)
│   │   ├── users.py            # User profile management (/users/*)
│   │   ├── skills.py           # Skill listing and management (/skills/*)
│   │   ├── sessions.py         # Session scheduling (/sessions/*)
│   │   ├── chat.py             # Personal chatbot (/chat/*)
│   │   ├── certificates.py     # Certificate validation (/certificates/*)
│   │   ├── matching.py         # Smart skill matching (/matching/*)
│   │   └── credit.py           # Credit/reward management (/credit/*)
│   │
│   └── services/               # Business logic and external service integration
│       ├── __init__.py
│       ├── ai_embeddings.py    # Sentence-Transformers for skill embeddings
│       ├── ai_vision.py        # Groq Vision API for certificate analysis
│       ├── chat_user_context.py # Build contextual prompts for chatbot
│       └── rewards.py          # Credit calculation and reward logic
│
├── migrations/                 # SQL migration scripts
│   ├── 001_add_users_bio.sql
│   └── 002_chat_tables.sql
│
├── scripts/                    # One-off scripts for database setup
│   ├── apply_bio_column.py
│   └── apply_chat_tables.py
│
├── temp_uploads/               # Temporary directory for certificate uploads
│
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (DO NOT COMMIT)
└── .vscode/
    └── settings.json           # VS Code workspace settings

frontend/ (Separate Repository)
│
├── index.html                  # Homepage
├── login.html                  # Login page
├── signup.html                 # Registration page
├── profile.html                # User profile
├── chatbot.html                # AI chatbot interface
├── home.html                   # Dashboard
│
├── script.js                   # Main JavaScript logic
├── chatbot.js                  # Chatbot frontend
│
├── style.css                   # Global styles
├── profile.css                 # Profile page styles
└── style1.css                  # Alternative styles
```

---

## ▶️ Running the Server

### Start the Development Server

```bash
cd backend
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Will watch for changes in these directories: ['C:\Users\YourName\Desktop\Skill_Swapping\backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [54321]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Server Configuration Options

```bash
# Run on specific port
uvicorn app.main:app --reload --port 8080

# Run in production mode (no auto-reload)
uvicorn app.main:app

# Run with multiple workers
uvicorn app.main:app --workers 4

# Enable debug logging
uvicorn app.main:app --reload --log-level debug
```

### Verify Server is Running

- **Health Check**: http://127.0.0.1:8000/health
- **Root Endpoint**: http://127.0.0.1:8000/

Expected responses:
```json
{
  "status": "online",
  "version": "1.0.0",
  "message": "SkillSwap API is running smoothly."
}
```

---

## 📚 API Documentation

### Interactive Swagger UI

Once the server is running, visit:

- **Swagger UI (Interactive)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc (Alternative)**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

The Swagger UI provides:
- Full endpoint documentation with descriptions
- Try-it-out functionality to test endpoints live
- Request/response schema visualization
- Authentication bearer token support

---

## 🧠 Core Modules & Services

### 1. **AI Embeddings Service** (`ai_embeddings.py`)

Generates 384-dimensional vector embeddings for skill names using HuggingFace's `all-MiniLM-L6-v2` model.

**Key Features:**
- Lazy loading: Model loads only on first use
- Efficient similarity search for skill matching
- Stored in PostgreSQL with pgvector extension

**Usage:**
```python
from app.services.ai_embeddings import generate_embedding

embedding = generate_embedding("Python Programming")
# Returns: [0.123, 0.456, -0.789, ...]  # 384 floats
```

### 2. **AI Vision Service** (`ai_vision.py`)

Analyzes uploaded certificate images using Groq's LLaMA Vision API for OCR and validation.

**Key Features:**
- Extracts: Student name, Skill name, Certificate validity
- Returns: `{"status": "VALID/INVALID", "student_name": "...", "skill_name": "..."}`
- Base64 image encoding for API transmission

**Usage:**
```python
from app.services.ai_vision import analyze_external_certificate

result = analyze_external_certificate("path/to/certificate.jpg")
# Returns structured certificate data
```

### 3. **Chatbot Context Builder** (`chat_user_context.py`)

Builds personalized context for the LLaMA chatbot including user data, skills, and session history.

**Key Features:**
- Includes user first name, available credits, skills list
- Session history and statistics
- Platform status and available features

**Usage:**
```python
from app.services.chat_user_context import build_user_context

context = build_user_context(user_id, db_session)
# Returns formatted context string for chatbot system prompt
```

### 4. **Rewards & Credit Logic** (`rewards.py`)

Manages Time Credit allocation, session billing, and reward distribution.

**Key Features:**
- Base allocation: 2.0 credits per new user
- Session cost calculation based on duration
- Automatic credit transfer on session completion

---

## 🌐 API Endpoints Overview

### Authentication Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login user, return JWT token | ❌ |

### User Management

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/users/me` | Get current user profile | ✅ |
| PUT | `/users/{user_id}` | Update user profile | ✅ |
| GET | `/users/{user_id}` | Get user details | ✅ |
| GET | `/users` | List all users with pagination | ✅ |

### Skills Management

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/skills` | List all skills (paginated) | ✅ |
| POST | `/skills` | Add new skill | ✅ |
| GET | `/skills/{skill_id}` | Get skill details | ✅ |
| PUT | `/skills/{skill_id}` | Update skill | ✅ |
| DELETE | `/skills/{skill_id}` | Delete skill | ✅ |

### Sessions

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/sessions` | Schedule new session | ✅ |
| GET | `/sessions` | List user sessions | ✅ |
| GET | `/sessions/{session_id}` | Get session details | ✅ |
| PUT | `/sessions/{session_id}` | Update session status | ✅ |
| POST | `/sessions/{session_id}/rate` | Rate completed session | ✅ |

### Certificates

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/certificates/upload` | Upload external certificate | ✅ |
| GET | `/certificates` | List user certificates | ✅ |
| POST | `/certificates/{cert_id}/validate` | Validate certificate with AI | ✅ |
| GET | `/certificates/{cert_id}/download` | Download certificate | ✅ |

### Smart Matching

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/matching/search_skills` | Search skills using chatbot | ✅ |
| POST | `/matching/recommend` | Get skill recommendations | ✅ |

### Personal Chat

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/chat/conversations` | Create new conversation | ✅ |
| GET | `/chat/conversations` | List conversations | ✅ |
| POST | `/chat/message` | Send message to chatbot | ✅ |
| GET | `/chat/message/{message_id}` | Get message details | ✅ |

### Credit Management

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/credit/balance` | Get user credit balance | ✅ |
| GET | `/credit/history` | View credit transaction history | ✅ |
| POST | `/credit/transfer` | Transfer credits to another user | ✅ |

### Health & Status

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | ❌ |
| GET | `/` | Welcome message | ❌ |

---

## 🔐 Authentication

The API uses **JWT (JSON Web Tokens)** for stateless authentication.

### How It Works

1. **Registration**: User registers → receives JWT token
2. **Login**: User logs in → receives JWT token (7-day expiration)
3. **Authenticated Requests**: Include token in header:
   ```
   Authorization: Bearer <your_jwt_token_here>
   ```

### Token Expiration

- **Default**: 7 days (168 hours)
- Configure in `app/core/security.py`: `ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7`

### Password Security

- **Algorithm**: bcrypt with salt
- **Never stored in plain text**
- Verified on login using `verify_password()`

---

## 🚨 Troubleshooting

### Issue: "Waiting for application startup" - Server Hangs Indefinitely

**Cause**: AI model loading during startup blocking the server.

**Solution**: The project uses **lazy loading**:
- Models load on first API request, not on server start
- This prevents the hanging issue
- First request to an AI endpoint may take 5-10 seconds
- Subsequent requests are instant (model cached in memory)

### Issue: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
cd backend  # Make sure you're in the backend directory
uvicorn app.main:app --reload
```

### Issue: PostgreSQL Connection Error

**Symptoms**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions**:
1. Verify `DATABASE_URL` in `.env` is correct
2. Check Neon connection pooler is enabled
3. Ensure SSL/TLS connection: `?sslmode=require`
4. Test connection manually:
   ```python
   from sqlalchemy import create_engine
   engine = create_engine(os.getenv("DATABASE_URL"))
   connection = engine.connect()
   print("✅ Connected!")
   ```

### Issue: "pgvector extension not available"

**Symptoms**:
```
sqlalchemy.exc.ProgrammingError: type "vector" does not exist
```

**Solution** (in Neon Dashboard):
1. Go to SQL Editor
2. Run: `CREATE EXTENSION IF NOT EXISTS vector;`
3. Run: `CREATE EXTENSION IF NOT EXISTS uuid-ossp;`

### Issue: Groq/Gemini API Errors

**Solutions**:
1. Verify API keys in `.env` are correct and not expired
2. Check Groq/Gemini account has active credits
3. Verify internet connection
4. Check error logs for specific API responses

### Issue: "Cannot find ffmpeg" or "Image processing failed"

**Solution**: Install system dependencies:

**Windows**:
```bash
# Using chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS**:
```bash
brew install ffmpeg
```

**Linux**:
```bash
sudo apt-get install ffmpeg
```

### Issue: Uvicorn Not Found

**Solution**:
```bash
# Verify virtual environment is activated
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: CORS Errors in Frontend

**Current Config**: All origins allowed (`allow_origins=["*"]`)

**For Production**, update in `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Out of Memory - Large Model Loading

**Solution**: Use a lighter embeddings model:
```python
# In app/services/ai_embeddings.py
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# Already using the lightweight model (only 22.7 MB)
```

---

## 🔄 Development Workflow

### Adding a New Feature

1. **Create models** in `app/models.py`
2. **Create schemas** in `app/schemas.py` (Pydantic models)
3. **Create endpoints** in `app/routers/feature.py`
4. **Register router** in `app/main.py`:
   ```python
   app.include_router(feature.router)
   ```
5. **Test in Swagger UI**: http://127.0.0.1:8000/docs

### Adding New Dependencies

```bash
pip install new-package
pip freeze > requirements.txt
```

### Running Migrations

```bash
# Manual SQL migrations
# Go to Neon Dashboard → SQL Editor
# Run the migration scripts in order

# Or use Python scripts
python scripts/apply_bio_column.py
python scripts/apply_chat_tables.py
```

---

## 📊 Performance Optimization Tips

1. **Database Indexing**: Add indexes on frequently queried columns
   ```sql
   CREATE INDEX idx_users_email ON users(email);
   CREATE INDEX idx_skills_user_id ON skills(user_id);
   ```

2. **Connection Pooling**: Already configured in `database.py` with `pool_pre_ping=True`

3. **Vector Search**: pgvector with HNSW algorithm for fast similarity searches

4. **Lazy Loading Models**: AI models load on first use, not on server startup

5. **Caching**: Consider adding Redis for frequently accessed data

---

## 📝 License

This project is part of the SkillSwap platform.

---

## 🤝 Support & Contact

For issues, questions, or contributions:
- **GitHub Issues**: [Repository Issues](https://github.com/ayoub-ouazene/Skill_swapping/issues)
- **Email**: quickhire.contactteam@gmail.com

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Neon PostgreSQL](https://neon.tech/docs)
- [Sentence-Transformers](https://www.sbert.net/)
- [Groq API Documentation](https://console.groq.com/docs)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)

---

**Last Updated**: March 29, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
