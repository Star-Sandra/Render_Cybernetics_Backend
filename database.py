import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()
database_url = os.getenv("DATABASE_URL", "").strip() or "postgresql://render_cybernetics_backend_user:PASSWORD@dpg-daoeua740ujc73f1td40-a/render_cybernetics_backend"
# database_url = os.getenv("DATABASE_URL", "").strip()
# if not database_url:
#     seen = sorted(k for k in os.environ if "DATA" in k.upper() or "URL" in k.upper())
#     raise RuntimeError(f"DATABASE_URL is not set. Similar env vars seen: {seen}")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(database_url, pool_pre_ping=True)

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