from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, certificates, chat, credit, matching, peer_messages, sessions, skills, users

# This line creates your tables in Neon if they don't exist yet
# (Though we already created them via the SQL editor, this is good practice)


# Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="SkillSwap AI Backend",
    description="Backend of the Project",
    version="1.0.0"
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


@app.get("/")
def read_root():
    return {"message": "Welcome to the SkillSwap API. The server is alive!"}


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "online", 
        "version": "1.0.0",
        "message": "SkillSwap API is running smoothly."
    }
