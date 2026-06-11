"""Database configuration and session management."""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from typing import Generator

from .settings import settings


# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database by creating all tables."""
    from src.models import profile, job, score  # noqa: F401
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)


def reset_db() -> None:
    """Reset database by dropping and recreating all tables."""
    drop_db()
    init_db()