from fastapi import FastAPI
from app.database import engine, Base
from app.routers import certificates , matching , economy

# This line creates your tables in Neon if they don't exist yet
# (Though we already created them via the SQL editor, this is good practice)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SkillSwap AI Backend",
    description="Backend of the Project",
    version="1.0.0"
)

app.include_router(certificates.router) 
app.include_router(matching.router)
app.include_router(economy.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the SkillSwap API. The server is alive!"}