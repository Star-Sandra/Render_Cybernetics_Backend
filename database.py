import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# FIXED: Removed the @://render.com layout with your fully qualified external link string
CLOUD_DATABASE_URL = "postgresql+psycopg2://render_cybernetics_backend_user:UfUCHmCLdzO0Fsp954Zuyq5qEX8RRo83@://render.com"

database_url = CLOUD_DATABASE_URL
database_url = str(database_url).replace(" ", "")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(database_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
