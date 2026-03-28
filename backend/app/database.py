import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy Engine
# Neon is serverless and sometimes drops idle connections, so pool_pre_ping helps keep it alive
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal class will be used to create individual database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our database models to inherit from
Base = declarative_base()

# Dependency to get the database session in our endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()