from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
from app.config import settings

# SQLite requires connect_args check_same_thread=False for multi-threaded FastAPI execution
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
    echo=False  # Set to True if you want to print all generated raw SQL queries in console
)

# SessionLocal is a factory that produces new database Session instances for each HTTP request
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base class that all database models inherit from
Base = declarative_base()


def get_db() -> Generator:
    """
    FastAPI Dependency that provides a transactional database session per request.
    Automatically closes the connection after request completion or exception.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
