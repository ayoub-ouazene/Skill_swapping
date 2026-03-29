import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base
from app.routers import auth, certificates, chat, credit, matching, peer_messages, sessions, skills, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # After uvicorn binds to PORT (so host probes succeed), create tables if needed.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SkillSwap AI Backend",
    description="Backend of the Project",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "http://127.0.0.1:5500",
    #     "http://localhost:5500",
    #     "http://127.0.0.1:5501",
    #     "http://localhost:5501",
    # ],
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(skills.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(peer_messages.router)
app.include_router(certificates.router)
app.include_router(matching.router)
app.include_router(credit.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "online", 
        "version": "1.0.0",
        "message": "SkillSwap API is running smoothly."
    }


# Frontend (HTML/JS/CSS) — mount last so /docs, /openapi.json, and API routes stay reachable
_frontend_dir = os.environ.get(
    "FRONTEND_STATIC_DIR",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "Frontendd")),
)
if os.path.isdir(_frontend_dir):
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {"message": "Welcome to the SkillSwap API. The server is alive!"}
