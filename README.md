# SkillSwap Backend 🚀

The backend API for SkillSwap, a time-credit-based skill exchange platform. Built with FastAPI, PostgreSQL (via Neon), and powered by Google Gemini for AI-driven semantic search and automated certificate processing.

## Prerequisites
* Python 3.9+
* A [Neon.tech](https://neon.tech/) account (for Serverless PostgreSQL)
* A [Google Gemini API Key](https://aistudio.google.com/) (for AI Vision and Vector Embeddings)

## 🛠️ Local Setup & Installation

**1. Clone the repository and navigate to the backend folder**


# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate


pip install -r requirements.txt


# Database (Get this from your Neon Dashboard -> Connection Details)
DATABASE_URL=postgresql://<user>:<password>@<ep-name>.neon.tech/skillswap?sslmode=require

# AI Integration
GEMINI_API_KEY=your_google_gemini_api_key_here
and other env variables

# RUNNIG THE backend
uvicorn app.main:app --reload**

# API Documentation (Swagger UI)

Swagger UI (Interactive): http://127.0.0.1:8000/docs

