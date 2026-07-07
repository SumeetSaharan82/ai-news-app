"""
Database session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.config.settings import get_settings
from backend.core.user_models import Base

settings = get_settings()

# Create database engine (SQLite needs different pool config)
is_sqlite = "sqlite" in settings.database_url
engine_kwargs = dict(echo=settings.sqlalchemy_echo, pool_pre_ping=True)
if not is_sqlite:
    engine_kwargs.update(pool_size=settings.sqlalchemy_pool_size, max_overflow=settings.sqlalchemy_max_overflow)
if is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Dependency for getting database sessions
    Yields a session and ensures it's closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    """
    Base.metadata.create_all(bind=engine)
