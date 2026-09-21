# # # import os
# # # from dotenv import load_dotenv
# # # from database import Base
# # # from smartmama import models  
# # # load_dotenv()
# # # from logging.config import fileConfig

# # # from sqlalchemy import engine_from_config
# # # from sqlalchemy import pool

# # # from alembic import context

# # # # this is the Alembic Config object, which provides
# # # # access to the values within the .ini file in use.
# # # # config = context.config
# # # # database_url = os.getenv("DATABASE_URL")
# # # # if database_url and database_url.startswith("postgres://"):
# # # #     database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
# # # # # config.set_main_option("sqlalchemy.url", database_url)
# # # config = context.config

# # # # 1. Try to read the environment variable first
# # # database_url = os.getenv("DATABASE_URL")

# # # # 2. Fix the postgres dialect dialect prefix if it exists
# # # if database_url and database_url.startswith("postgres://"):
# # #     database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)

# # # # 3. CRITICAL FALLBACK: If database_url is empty, None, or broken, force your real link here
# # # if not database_url or len(str(database_url).strip()) < 20:
# # #     # ⚠️ Replace the text inside quotes below with your ACTUAL Render Internal Database URL!
# # #     database_url = "postgresql+psycopg2://sandbox_user:your_password@srv-db-instance:5432/smartmama_db"

# # # config.set_main_option('sqlalchemy.url', str(database_url))


# # # # Interpret the config file for Python logging.
# # # # This line sets up loggers basically.
# # # if config.config_file_name is not None:
# # #     fileConfig(config.config_file_name)

# # # # add your model's MetaData object here
# # # # for 'autogenerate' support
# # # # from myapp import mymodel
# # # # target_metadata = mymodel.Base.metadata
# # # target_metadata = Base.metadata

# # # # other values from the config, defined by the needs of env.py,
# # # # can be acquired:
# # # # my_important_option = config.get_main_option("my_important_option")
# # # # ... etc.


# # # def run_migrations_offline() -> None:
# # #     """Run migrations in 'offline' mode.

# # #     This configures the context with just a URL
# # #     and not an Engine, though an Engine is acceptable
# # #     here as well.  By skipping the Engine creation
# # #     we don't even need a DBAPI to be available.

# # #     Calls to context.execute() here emit the given string to the
# # #     script output.
    

# # #     """
# # #     url = config.get_main_option("sqlalchemy.url")
# # #     context.configure(
# # #         url=url,
# # #         target_metadata=target_metadata,
# # #         literal_binds=True,
# # #         dialect_opts={"paramstyle": "named"},
# # #     )

# # #     with context.begin_transaction():
# # #         context.run_migrations()


# # # def run_migrations_online() -> None:
# # #     """Run migrations in 'online' mode.

# # #     In this scenario we need to create an Engine
# # #     and associate a connection with the context.

# # #     """
# # #     connectable = engine_from_config(
# # #         config.get_section(config.config_ini_section, {}),
# # #         prefix="sqlalchemy.",
# # #         poolclass=pool.NullPool,
# # #     )

# # #     with connectable.connect() as connection:
# # #         context.configure(
# # #             connection=connection, target_metadata=target_metadata
# # #         )

# # #         with context.begin_transaction():
# # #             context.run_migrations()


# # # if context.is_offline_mode():
# # #     run_migrations_offline()
# # # else:
# # #     run_migrations_online()

# # import os
# # from dotenv import load_dotenv
# # from database import Base
# # from smartmama import models  
# # load_dotenv()
# # from logging.config import fileConfig

# # from sqlalchemy import engine_from_config
# # from sqlalchemy import pool

# # from alembic import context

# # # this is the Alembic Config object, which provides
# # # access to the values within the .ini file in use.
# # config = context.config

# # # 1. Fetch from environment, or use your direct Render Database URL string
# # database_url = os.getenv("DATABASE_URL") or "postgresql://render_cybernetics_backend_user:UfUCHmCLdzO0Fsp954Zuyq5qEX8RRo83@dpg-daoeua740ujc73f1td40-a/render_cybernetics_backend"

# # # 2. Safety cleanup: remove any accidental space characters that break URL parsing
# # database_url = str(database_url).replace(" ", "")

# # # 3. Ensure the prefix is compatible with SQLAlchemy 2.x execution rules
# # if database_url.startswith("postgres://"):
# #     database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
# # elif database_url.startswith("postgresql://"):
# #     database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# # # 4. Bind the cleaned string straight to the configuration runtime
# # config.set_main_option('sqlalchemy.url', database_url)

# # # Interpret the config file for Python logging.
# # if config.config_file_name is not None:
# #     fileConfig(config.config_file_name)

# # target_metadata = Base.metadata



# import os
# from dotenv import load_dotenv
# from database import Base
# from smartmama import models  
# load_dotenv()
# from logging.config import fileConfig

# from sqlalchemy import engine_from_config
# from sqlalchemy import pool

# from alembic import context

# # this is the Alembic Config object, which provides
# # access to the values within the .ini file in use.
# config = context.config

# # 1. Fetch from environment, or use your direct Render EXTERNAL Database URL string
# database_url = os.getenv("DATABASE_URL") or "postgresql://render_cybernetics_backend_user:UfUCHmCLdzO0Fsp954Zuyq5qEX8RRo83@dpg-daoeua740ujc73f1td40-a.virginia-postgres.render.com/render_cybernetics_backend"

# # 2. Safety cleanup: remove any accidental space characters that break URL parsing
# database_url = str(database_url).replace(" ", "")

# # 3. Ensure the prefix is compatible with SQLAlchemy 2.x execution rules
# if database_url.startswith("postgres://"):
#     database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
# elif database_url.startswith("postgresql://"):
#     database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# # 4. Bind the cleaned string straight to the configuration runtime
# config.set_main_option('sqlalchemy.url', database_url)

# # Interpret the config file for Python logging.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# target_metadata = Base.metadata

# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode.

#     This configures the context with just a URL
#     and not an Engine, though an Engine is acceptable
#     here as well. By skipping the Engine creation
#     we don't even need a DBAPI to be available.

#     Calls to context.execute() here emit the given string to the
#     script output.
#     """
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )

#     with context.begin_transaction():
#         context.run_migrations()

# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.

#     In this scenario we need to create an Engine
#     and associate a connection with the context.
#     """
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata
#         )

#         with context.begin_transaction():
#             context.run_migrations()

# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()

import os
from dotenv import load_dotenv
from database import Base
from smartmama import models  
load_dotenv()
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

config = context.config

CLOUD_DATABASE_URL = "postgresql+psycopg2://render_cybernetics_backend_user:UfUCHmCLdzO0Fsp954Zuyq5qEX8RRo83@://render.com"

database_url = os.getenv("DATABASE_URL") or CLOUD_DATABASE_URL
database_url = str(database_url).replace(" ", "")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

config.set_main_option('sqlalchemy.url', database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ... leave the rest of your migration runner functions (run_migrations_offline, etc.) below as they are ...
