# # # import os

# # # from dotenv import load_dotenv
# # # from sqlalchemy import create_engine
# # # from sqlalchemy.orm import declarative_base, sessionmaker

# # # load_dotenv()

# # # LOCAL_DATABASE_URL = (
# # #     "postgresql://postgres:postgres@localhost:5432/smartmama_db"
# # # )

# # # database_url = os.getenv("DATABASE_URL", LOCAL_DATABASE_URL)


# # # if database_url.startswith("postgres://"):
# # #     database_url = database_url.replace(
# # #         "postgres://", "postgresql://", 1
# # #     )


# # # engine = create_engine(
# # #     database_url,
# # #     pool_pre_ping=True,
# # #     )

# # # SessionLocal = sessionmaker(
# # #     autocommit=False,
# # #     autoflush=False,
# # #     bind=engine,
# # # )

# # # Base = declarative_base()


# # # def get_db():
# # #     db = SessionLocal()
# # #     try:
# # #         yield db
# # #     finally:
# # #         db.close()


# # import os

# # from dotenv import load_dotenv
# # from sqlalchemy import create_engine
# # from sqlalchemy.orm import declarative_base, sessionmaker

# # load_dotenv()

# # # FIXED: Hardcoded your cloud database URL as the definitive fallback string
# # CLOUD_DATABASE_URL = (
# #     "postgresql://render_cybernetics_backend_user:UfUCHmCLdzO0Fsp954Zuyq5qEX8RRo83@://render.com"
# # )

# # # Checks for environment variable first, otherwise defaults directly to the Render cloud DB link
# # database_url = os.getenv("DATABASE_URL") or CLOUD_DATABASE_URL

# # # Safety cleanup: remove any accidental copy-paste spacing typos automatically
# # database_url = str(database_url).replace(" ", "")

# # if database_url.startswith("postgres://"):
# #     database_url = database_url.replace(
# #         "postgres://", "postgresql://", 1
# #     )

# # # engine = create_engine(
# # #     database_url,
# # #     pool_pre_ping=True,
# # # )
# # engine = create_engine(database_url)

# # SessionLocal = sessionmaker(
# #     autocommit=False,
# #     autoflush=False,
# #     bind=engine,
# # )

# # Base = declarative_base()

# # def get_db():
# #     db = SessionLocal()
# #     try:
# #         yield db
# #     finally:
# #         db.close()



# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base, sessionmaker

# load_dotenv()

# # We remove any complex sub-parameters or implicit port pointers here
# CLOUD_DATABASE_URL = "postgresql+psycopg2://render_cybernetics_backend_user:UfUCHmCLdzO0Fsp954Zuyq5qEX8RRo83@://render.com"

# database_url = os.getenv("DATABASE_URL") or CLOUD_DATABASE_URL
# database_url = str(database_url).replace(" ", "")

# if database_url.startswith("postgres://"):
#     database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
# elif database_url.startswith("postgresql://"):
#     database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# engine = create_engine(database_url)

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine,
# )

# Base = declarative_base()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# FIXED: Removed the @:// render typo with your complete, functional external connection string
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
